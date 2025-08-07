"""
خدمة النسخ الاحتياطي الآمن والاستعادة
"""

import os
import json
import uuid
import gzip
import shutil
import hashlib
import tarfile
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum
import threading
import schedule
import time
from cryptography.fernet import Fernet
import boto3
from google.cloud import storage as gcs
import dropbox

class BackupType(Enum):
    FULL = "نسخة كاملة"
    INCREMENTAL = "نسخة تزايدية"
    DIFFERENTIAL = "نسخة تفاضلية"
    SNAPSHOT = "لقطة سريعة"

class BackupStatus(Enum):
    PENDING = "في الانتظار"
    RUNNING = "قيد التنفيذ"
    COMPLETED = "مكتملة"
    FAILED = "فاشلة"
    CANCELLED = "ملغية"

class StorageProvider(Enum):
    LOCAL = "محلي"
    AWS_S3 = "أمازون S3"
    GOOGLE_CLOUD = "جوجل كلاود"
    DROPBOX = "دروب بوكس"
    AZURE = "مايكروسوفت أزور"

class BackupPriority(Enum):
    LOW = "منخفض"
    MEDIUM = "متوسط"
    HIGH = "عالي"
    CRITICAL = "حرج"

@dataclass
class BackupJob:
    job_id: str
    name: str
    backup_type: str
    data_sources: List[str]
    storage_provider: str
    storage_path: str
    encryption_enabled: bool
    compression_enabled: bool
    priority: str
    schedule_cron: Optional[str]
    retention_days: int
    created_at: datetime
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    is_active: bool

@dataclass
class BackupRecord:
    backup_id: str
    job_id: str
    backup_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    file_count: int
    total_size_bytes: int
    compressed_size_bytes: int
    storage_path: str
    checksum: str
    encryption_key_id: Optional[str]
    error_message: Optional[str]

class BackupService:
    def __init__(self):
        """تهيئة خدمة النسخ الاحتياطي"""
        
        # إعدادات النسخ الاحتياطي
        self.backup_settings = {
            'default_retention_days': 90,
            'max_concurrent_backups': 3,
            'compression_level': 6,
            'encryption_algorithm': 'Fernet',
            'chunk_size_mb': 100,
            'verify_backups': True,
            'auto_cleanup_old_backups': True,
            'backup_metadata': True,
            'enable_deduplication': True,
            'enable_progress_tracking': True,
            'max_backup_size_gb': 100,
            'backup_timeout_hours': 24
        }
        
        # مصادر البيانات المختلفة
        self.data_sources = {
            'user_profiles': {
                'path': '/data/users/',
                'priority': BackupPriority.HIGH.value,
                'encryption_required': True,
                'description': 'ملفات المستخدمين الشخصية'
            },
            'medical_records': {
                'path': '/data/medical/',
                'priority': BackupPriority.CRITICAL.value,
                'encryption_required': True,
                'description': 'السجلات الطبية'
            },
            'appointments': {
                'path': '/data/appointments/',
                'priority': BackupPriority.HIGH.value,
                'encryption_required': True,
                'description': 'بيانات المواعيد'
            },
            'medications': {
                'path': '/data/medications/',
                'priority': BackupPriority.HIGH.value,
                'encryption_required': True,
                'description': 'بيانات الأدوية'
            },
            'lab_results': {
                'path': '/data/lab_results/',
                'priority': BackupPriority.CRITICAL.value,
                'encryption_required': True,
                'description': 'نتائج المختبرات'
            },
            'images_scans': {
                'path': '/data/images/',
                'priority': BackupPriority.MEDIUM.value,
                'encryption_required': True,
                'description': 'الصور والأشعة الطبية'
            },
            'system_config': {
                'path': '/config/',
                'priority': BackupPriority.HIGH.value,
                'encryption_required': False,
                'description': 'إعدادات النظام'
            },
            'audit_logs': {
                'path': '/logs/audit/',
                'priority': BackupPriority.MEDIUM.value,
                'encryption_required': False,
                'description': 'سجلات المراجعة'
            },
            'security_logs': {
                'path': '/logs/security/',
                'priority': BackupPriority.HIGH.value,
                'encryption_required': True,
                'description': 'سجلات الأمان'
            },
            'payment_records': {
                'path': '/data/payments/',
                'priority': BackupPriority.CRITICAL.value,
                'encryption_required': True,
                'description': 'سجلات المدفوعات'
            }
        }
        
        # موفري التخزين السحابي
        self.storage_providers = {
            StorageProvider.AWS_S3.value: {
                'client_class': 'boto3.client',
                'config_keys': ['aws_access_key_id', 'aws_secret_access_key', 'region_name'],
                'bucket_param': 'Bucket',
                'key_param': 'Key'
            },
            StorageProvider.GOOGLE_CLOUD.value: {
                'client_class': 'google.cloud.storage.Client',
                'config_keys': ['project_id', 'credentials_path'],
                'bucket_param': 'bucket_name',
                'key_param': 'blob_name'
            },
            StorageProvider.DROPBOX.value: {
                'client_class': 'dropbox.Dropbox',
                'config_keys': ['access_token'],
                'bucket_param': None,
                'key_param': 'path'
            }
        }
        
        # قاعدة بيانات النسخ الاحتياطي (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.backup_jobs = {}
        self.backup_records = {}
        self.running_backups = {}
        self.backup_queue = []
        self.encryption_keys = {}
        
        # خيط المراقبة
        self.scheduler_thread = None
        self.is_scheduler_running = False
        
        # تهيئة الخدمة
        self._initialize_default_jobs()
        self._start_scheduler()
    
    def create_backup_job(self, job_data: Dict) -> Dict:
        """
        إنشاء مهمة نسخ احتياطي جديدة
        
        Args:
            job_data: بيانات المهمة
            
        Returns:
            Dict: نتيجة الإنشاء
        """
        try:
            job_id = str(uuid.uuid4())
            
            # التحقق من صحة البيانات
            required_fields = ['name', 'backup_type', 'data_sources', 'storage_provider']
            for field in required_fields:
                if field not in job_data:
                    return {
                        'success': False,
                        'error': f'الحقل {field} مطلوب'
                    }
            
            # التحقق من صحة مصادر البيانات
            invalid_sources = [
                source for source in job_data['data_sources'] 
                if source not in self.data_sources
            ]
            if invalid_sources:
                return {
                    'success': False,
                    'error': f'مصادر بيانات غير صالحة: {invalid_sources}'
                }
            
            # حساب الجدولة التالية
            next_run = None
            if job_data.get('schedule_cron'):
                next_run = self._calculate_next_run(job_data['schedule_cron'])
            
            # إنشاء المهمة
            backup_job = BackupJob(
                job_id=job_id,
                name=job_data['name'],
                backup_type=job_data['backup_type'],
                data_sources=job_data['data_sources'],
                storage_provider=job_data['storage_provider'],
                storage_path=job_data.get('storage_path', f'/backups/{job_id}/'),
                encryption_enabled=job_data.get('encryption_enabled', True),
                compression_enabled=job_data.get('compression_enabled', True),
                priority=job_data.get('priority', BackupPriority.MEDIUM.value),
                schedule_cron=job_data.get('schedule_cron'),
                retention_days=job_data.get('retention_days', self.backup_settings['default_retention_days']),
                created_at=datetime.now(),
                last_run=None,
                next_run=next_run,
                is_active=job_data.get('is_active', True)
            )
            
            # حفظ المهمة
            self.backup_jobs[job_id] = backup_job
            
            return {
                'success': True,
                'job_id': job_id,
                'message': 'تم إنشاء مهمة النسخ الاحتياطي بنجاح',
                'next_run': next_run.isoformat() if next_run else None
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء مهمة النسخ الاحتياطي: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء المهمة'
            }
    
    def start_backup(self, job_id: str, backup_type: str = None) -> Dict:
        """
        بدء نسخة احتياطية
        
        Args:
            job_id: معرف المهمة
            backup_type: نوع النسخة (اختياري)
            
        Returns:
            Dict: نتيجة البدء
        """
        try:
            # التحقق من وجود المهمة
            if job_id not in self.backup_jobs:
                return {
                    'success': False,
                    'error': 'مهمة النسخ الاحتياطي غير موجودة'
                }
            
            backup_job = self.backup_jobs[job_id]
            
            # التحقق من حالة المهمة
            if not backup_job.is_active:
                return {
                    'success': False,
                    'error': 'مهمة النسخ الاحتياطي غير نشطة'
                }
            
            # التحقق من عدد النسخ الاحتياطية الجارية
            if len(self.running_backups) >= self.backup_settings['max_concurrent_backups']:
                return {
                    'success': False,
                    'error': 'تم الوصول للحد الأقصى من النسخ الاحتياطية المتزامنة'
                }
            
            # إنشاء سجل النسخة الاحتياطية
            backup_id = str(uuid.uuid4())
            backup_record = BackupRecord(
                backup_id=backup_id,
                job_id=job_id,
                backup_type=backup_type or backup_job.backup_type,
                status=BackupStatus.PENDING.value,
                start_time=datetime.now(),
                end_time=None,
                file_count=0,
                total_size_bytes=0,
                compressed_size_bytes=0,
                storage_path='',
                checksum='',
                encryption_key_id=None,
                error_message=None
            )
            
            # حفظ السجل
            if job_id not in self.backup_records:
                self.backup_records[job_id] = []
            self.backup_records[job_id].append(backup_record)
            
            # بدء النسخة الاحتياطية في خيط منفصل
            backup_thread = threading.Thread(
                target=self._execute_backup,
                args=(backup_job, backup_record)
            )
            backup_thread.start()
            
            # تسجيل النسخة الاحتياطية الجارية
            self.running_backups[backup_id] = {
                'job_id': job_id,
                'thread': backup_thread,
                'start_time': datetime.now()
            }
            
            return {
                'success': True,
                'backup_id': backup_id,
                'message': 'تم بدء النسخة الاحتياطية',
                'estimated_duration': self._estimate_backup_duration(backup_job)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في بدء النسخة الاحتياطية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في بدء النسخة الاحتياطية'
            }
    
    def restore_backup(self, backup_id: str, restore_options: Dict = None) -> Dict:
        """
        استعادة نسخة احتياطية
        
        Args:
            backup_id: معرف النسخة الاحتياطية
            restore_options: خيارات الاستعادة
            
        Returns:
            Dict: نتيجة الاستعادة
        """
        try:
            # البحث عن النسخة الاحتياطية
            backup_record = None
            job_id = None
            
            for jid, records in self.backup_records.items():
                for record in records:
                    if record.backup_id == backup_id:
                        backup_record = record
                        job_id = jid
                        break
                if backup_record:
                    break
            
            if not backup_record:
                return {
                    'success': False,
                    'error': 'النسخة الاحتياطية غير موجودة'
                }
            
            # التحقق من حالة النسخة الاحتياطية
            if backup_record.status != BackupStatus.COMPLETED.value:
                return {
                    'success': False,
                    'error': 'النسخة الاحتياطية غير مكتملة'
                }
            
            # الحصول على معلومات المهمة
            backup_job = self.backup_jobs.get(job_id)
            if not backup_job:
                return {
                    'success': False,
                    'error': 'مهمة النسخ الاحتياطي غير موجودة'
                }
            
            # بدء عملية الاستعادة
            restore_id = str(uuid.uuid4())
            
            # تنفيذ الاستعادة في خيط منفصل
            restore_thread = threading.Thread(
                target=self._execute_restore,
                args=(backup_record, backup_job, restore_options or {}, restore_id)
            )
            restore_thread.start()
            
            return {
                'success': True,
                'restore_id': restore_id,
                'backup_id': backup_id,
                'message': 'تم بدء عملية الاستعادة',
                'estimated_duration': self._estimate_restore_duration(backup_record)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في استعادة النسخة الاحتياطية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الاستعادة'
            }
    
    def get_backup_status(self, backup_id: str = None, job_id: str = None) -> Dict:
        """
        الحصول على حالة النسخ الاحتياطية
        
        Args:
            backup_id: معرف نسخة احتياطية محددة (اختياري)
            job_id: معرف مهمة محددة (اختياري)
            
        Returns:
            Dict: حالة النسخ الاحتياطية
        """
        try:
            if backup_id:
                # البحث عن نسخة احتياطية محددة
                for jid, records in self.backup_records.items():
                    for record in records:
                        if record.backup_id == backup_id:
                            return {
                                'success': True,
                                'backup': self._format_backup_record(record)
                            }
                
                return {
                    'success': False,
                    'error': 'النسخة الاحتياطية غير موجودة'
                }
            
            elif job_id:
                # الحصول على نسخ مهمة محددة
                if job_id not in self.backup_records:
                    return {
                        'success': False,
                        'error': 'مهمة النسخ الاحتياطي غير موجودة'
                    }
                
                records = self.backup_records[job_id]
                formatted_records = [self._format_backup_record(record) for record in records]
                
                return {
                    'success': True,
                    'job_id': job_id,
                    'backups': formatted_records,
                    'total_backups': len(formatted_records)
                }
            
            else:
                # الحصول على جميع النسخ الاحتياطية
                all_backups = []
                for jid, records in self.backup_records.items():
                    for record in records:
                        formatted_record = self._format_backup_record(record)
                        formatted_record['job_id'] = jid
                        all_backups.append(formatted_record)
                
                # إحصائيات عامة
                total_backups = len(all_backups)
                completed_backups = len([b for b in all_backups if b['status'] == BackupStatus.COMPLETED.value])
                failed_backups = len([b for b in all_backups if b['status'] == BackupStatus.FAILED.value])
                running_backups = len(self.running_backups)
                
                return {
                    'success': True,
                    'backups': all_backups,
                    'statistics': {
                        'total_backups': total_backups,
                        'completed_backups': completed_backups,
                        'failed_backups': failed_backups,
                        'running_backups': running_backups,
                        'success_rate': (completed_backups / total_backups * 100) if total_backups > 0 else 0
                    }
                }
                
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على حالة النسخ الاحتياطية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الحالة'
            }
    
    def cleanup_old_backups(self, job_id: str = None) -> Dict:
        """
        تنظيف النسخ الاحتياطية القديمة
        
        Args:
            job_id: معرف مهمة محددة (اختياري)
            
        Returns:
            Dict: نتيجة التنظيف
        """
        try:
            cleaned_count = 0
            freed_space = 0
            
            jobs_to_clean = [job_id] if job_id else list(self.backup_jobs.keys())
            
            for jid in jobs_to_clean:
                if jid not in self.backup_jobs or jid not in self.backup_records:
                    continue
                
                backup_job = self.backup_jobs[jid]
                records = self.backup_records[jid]
                
                # تحديد النسخ المنتهية الصلاحية
                cutoff_date = datetime.now() - timedelta(days=backup_job.retention_days)
                expired_records = [
                    record for record in records 
                    if record.start_time < cutoff_date and record.status == BackupStatus.COMPLETED.value
                ]
                
                # حذف النسخ المنتهية الصلاحية
                for record in expired_records:
                    try:
                        # حذف الملف من التخزين
                        self._delete_backup_file(record, backup_job)
                        
                        # إزالة السجل
                        records.remove(record)
                        
                        cleaned_count += 1
                        freed_space += record.compressed_size_bytes
                        
                    except Exception as e:
                        current_app.logger.error(f"خطأ في حذف النسخة الاحتياطية {record.backup_id}: {str(e)}")
            
            return {
                'success': True,
                'cleaned_backups': cleaned_count,
                'freed_space_bytes': freed_space,
                'freed_space_mb': round(freed_space / (1024 * 1024), 2),
                'message': f'تم تنظيف {cleaned_count} نسخة احتياطية قديمة'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تنظيف النسخ الاحتياطية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في التنظيف'
            }
    
    def verify_backup_integrity(self, backup_id: str) -> Dict:
        """
        التحقق من سلامة النسخة الاحتياطية
        
        Args:
            backup_id: معرف النسخة الاحتياطية
            
        Returns:
            Dict: نتيجة التحقق
        """
        try:
            # البحث عن النسخة الاحتياطية
            backup_record = None
            backup_job = None
            
            for jid, records in self.backup_records.items():
                for record in records:
                    if record.backup_id == backup_id:
                        backup_record = record
                        backup_job = self.backup_jobs.get(jid)
                        break
                if backup_record:
                    break
            
            if not backup_record or not backup_job:
                return {
                    'success': False,
                    'error': 'النسخة الاحتياطية غير موجودة'
                }
            
            # تحميل الملف والتحقق من Checksum
            verification_result = self._verify_backup_file(backup_record, backup_job)
            
            if verification_result['valid']:
                return {
                    'success': True,
                    'backup_id': backup_id,
                    'integrity_status': 'سليمة',
                    'checksum_match': True,
                    'file_size_match': verification_result['size_match'],
                    'verification_time': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'backup_id': backup_id,
                    'integrity_status': 'تالفة',
                    'checksum_match': False,
                    'error': verification_result['error']
                }
                
        except Exception as e:
            current_app.logger.error(f"خطأ في التحقق من سلامة النسخة الاحتياطية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في التحقق'
            }
    
    def get_backup_analytics(self, period_days: int = 30) -> Dict:
        """
        الحصول على إحصائيات النسخ الاحتياطية
        
        Args:
            period_days: فترة الإحصائيات بالأيام
            
        Returns:
            Dict: إحصائيات النسخ الاحتياطية
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            
            # جمع النسخ من الفترة المحددة
            period_backups = []
            for jid, records in self.backup_records.items():
                period_backups.extend([
                    record for record in records 
                    if record.start_time >= cutoff_date
                ])
            
            # تحليل الإحصائيات
            total_backups = len(period_backups)
            completed_backups = len([b for b in period_backups if b.status == BackupStatus.COMPLETED.value])
            failed_backups = len([b for b in period_backups if b.status == BackupStatus.FAILED.value])
            
            # حساب الأحجام
            total_original_size = sum(b.total_size_bytes for b in period_backups if b.status == BackupStatus.COMPLETED.value)
            total_compressed_size = sum(b.compressed_size_bytes for b in period_backups if b.status == BackupStatus.COMPLETED.value)
            
            # حساب متوسط وقت النسخ
            completed_with_duration = [
                b for b in period_backups 
                if b.status == BackupStatus.COMPLETED.value and b.end_time
            ]
            
            if completed_with_duration:
                total_duration = sum(
                    (b.end_time - b.start_time).total_seconds() 
                    for b in completed_with_duration
                )
                avg_duration_seconds = total_duration / len(completed_with_duration)
            else:
                avg_duration_seconds = 0
            
            # تحليل أنواع النسخ
            backup_types = {}
            for backup in period_backups:
                backup_type = backup.backup_type
                if backup_type not in backup_types:
                    backup_types[backup_type] = 0
                backup_types[backup_type] += 1
            
            # تحليل الأخطاء
            error_analysis = {}
            failed_backups_list = [b for b in period_backups if b.status == BackupStatus.FAILED.value]
            for backup in failed_backups_list:
                error = backup.error_message or 'خطأ غير محدد'
                if error not in error_analysis:
                    error_analysis[error] = 0
                error_analysis[error] += 1
            
            return {
                'success': True,
                'period_days': period_days,
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_backups': total_backups,
                    'completed_backups': completed_backups,
                    'failed_backups': failed_backups,
                    'success_rate': (completed_backups / total_backups * 100) if total_backups > 0 else 0,
                    'total_original_size_gb': round(total_original_size / (1024**3), 2),
                    'total_compressed_size_gb': round(total_compressed_size / (1024**3), 2),
                    'compression_ratio': round((1 - total_compressed_size / total_original_size) * 100, 1) if total_original_size > 0 else 0,
                    'avg_backup_duration_minutes': round(avg_duration_seconds / 60, 1)
                },
                'backup_types_distribution': backup_types,
                'error_analysis': error_analysis,
                'storage_usage': self._calculate_storage_usage(),
                'recommendations': self._generate_backup_recommendations(period_backups)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على إحصائيات النسخ الاحتياطية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الإحصائيات'
            }
    
    # الدوال المساعدة
    def _initialize_default_jobs(self):
        """تهيئة مهام النسخ الاحتياطي الافتراضية"""
        # نسخة احتياطية يومية للبيانات الحرجة
        critical_job_data = {
            'name': 'نسخة احتياطية يومية - بيانات حرجة',
            'backup_type': BackupType.INCREMENTAL.value,
            'data_sources': ['medical_records', 'payment_records', 'user_profiles'],
            'storage_provider': StorageProvider.LOCAL.value,
            'storage_path': '/backups/daily_critical/',
            'encryption_enabled': True,
            'compression_enabled': True,
            'priority': BackupPriority.CRITICAL.value,
            'schedule_cron': '0 2 * * *',  # يومياً في الساعة 2 صباحاً
            'retention_days': 30,
            'is_active': True
        }
        
        self.create_backup_job(critical_job_data)
        
        # نسخة احتياطية أسبوعية كاملة
        weekly_job_data = {
            'name': 'نسخة احتياطية أسبوعية - كاملة',
            'backup_type': BackupType.FULL.value,
            'data_sources': list(self.data_sources.keys()),
            'storage_provider': StorageProvider.LOCAL.value,
            'storage_path': '/backups/weekly_full/',
            'encryption_enabled': True,
            'compression_enabled': True,
            'priority': BackupPriority.HIGH.value,
            'schedule_cron': '0 1 * * 0',  # أسبوعياً يوم الأحد في الساعة 1 صباحاً
            'retention_days': 90,
            'is_active': True
        }
        
        self.create_backup_job(weekly_job_data)
    
    def _start_scheduler(self):
        """بدء جدولة النسخ الاحتياطية"""
        if not self.is_scheduler_running:
            self.is_scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
    
    def _scheduler_loop(self):
        """حلقة جدولة النسخ الاحتياطية"""
        while self.is_scheduler_running:
            try:
                current_time = datetime.now()
                
                # فحص المهام المجدولة
                for job_id, job in self.backup_jobs.items():
                    if (job.is_active and job.next_run and 
                        current_time >= job.next_run and 
                        job_id not in [rb['job_id'] for rb in self.running_backups.values()]):
                        
                        # بدء النسخة الاحتياطية
                        self.start_backup(job_id)
                        
                        # حساب الجدولة التالية
                        if job.schedule_cron:
                            job.next_run = self._calculate_next_run(job.schedule_cron)
                
                # تنظيف النسخ الاحتياطية المنتهية
                if self.backup_settings['auto_cleanup_old_backups']:
                    # تنظيف كل 24 ساعة
                    if current_time.hour == 3 and current_time.minute == 0:
                        self.cleanup_old_backups()
                
                # انتظار دقيقة واحدة
                time.sleep(60)
                
            except Exception as e:
                current_app.logger.error(f"خطأ في جدولة النسخ الاحتياطية: {str(e)}")
                time.sleep(60)
    
    def _calculate_next_run(self, cron_expression: str) -> datetime:
        """حساب موعد التشغيل التالي من تعبير cron"""
        # تحليل تعبير cron وحساب الموعد التالي
        # هذا تبسيط، في التطبيق الحقيقي يمكن استخدام مكتبة croniter
        
        # مثال: "0 2 * * *" يعني يومياً في الساعة 2:00
        parts = cron_expression.split()
        if len(parts) == 5:
            minute, hour, day, month, weekday = parts
            
            next_run = datetime.now().replace(second=0, microsecond=0)
            
            if hour != '*':
                next_run = next_run.replace(hour=int(hour))
            if minute != '*':
                next_run = next_run.replace(minute=int(minute))
            
            # إذا كان الوقت قد مضى اليوم، انتقل لليوم التالي
            if next_run <= datetime.now():
                next_run += timedelta(days=1)
            
            return next_run
        
        # افتراضي: كل 24 ساعة
        return datetime.now() + timedelta(days=1)
    
    def _execute_backup(self, backup_job: BackupJob, backup_record: BackupRecord):
        """تنفيذ النسخة الاحتياطية"""
        try:
            # تحديث حالة النسخة الاحتياطية
            backup_record.status = BackupStatus.RUNNING.value
            
            # إنشاء مجلد مؤقت للنسخة الاحتياطية
            temp_dir = f"/tmp/backup_{backup_record.backup_id}"
            os.makedirs(temp_dir, exist_ok=True)
            
            # جمع الملفات من مصادر البيانات
            all_files = []
            total_size = 0
            
            for source_name in backup_job.data_sources:
                if source_name in self.data_sources:
                    source_info = self.data_sources[source_name]
                    source_path = source_info['path']
                    
                    # جمع الملفات من المصدر
                    source_files = self._collect_files_from_source(
                        source_path, backup_job.backup_type, backup_job.last_run
                    )
                    
                    all_files.extend(source_files)
                    total_size += sum(os.path.getsize(f) for f in source_files if os.path.exists(f))
            
            backup_record.file_count = len(all_files)
            backup_record.total_size_bytes = total_size
            
            # إنشاء أرشيف
            archive_path = os.path.join(temp_dir, f"backup_{backup_record.backup_id}.tar.gz")
            
            with tarfile.open(archive_path, 'w:gz') as tar:
                for file_path in all_files:
                    if os.path.exists(file_path):
                        # إضافة الملف للأرشيف مع الحفاظ على البنية
                        arcname = os.path.relpath(file_path, '/')
                        tar.add(file_path, arcname=arcname)
            
            # حساب حجم الأرشيف المضغوط
            compressed_size = os.path.getsize(archive_path)
            backup_record.compressed_size_bytes = compressed_size
            
            # تشفير الأرشيف إذا كان مطلوباً
            final_file_path = archive_path
            if backup_job.encryption_enabled:
                encrypted_path = f"{archive_path}.enc"
                encryption_result = self._encrypt_backup_file(archive_path, encrypted_path)
                if encryption_result['success']:
                    backup_record.encryption_key_id = encryption_result['key_id']
                    final_file_path = encrypted_path
                    os.remove(archive_path)  # حذف النسخة غير المشفرة
            
            # حساب checksum
            backup_record.checksum = self._calculate_file_checksum(final_file_path)
            
            # رفع الملف للتخزين
            upload_result = self._upload_backup_file(final_file_path, backup_job, backup_record)
            
            if upload_result['success']:
                backup_record.storage_path = upload_result['storage_path']
                backup_record.status = BackupStatus.COMPLETED.value
                backup_record.end_time = datetime.now()
                
                # تحديث آخر تشغيل للمهمة
                backup_job.last_run = datetime.now()
                
                current_app.logger.info(f"تم إكمال النسخة الاحتياطية {backup_record.backup_id} بنجاح")
            else:
                backup_record.status = BackupStatus.FAILED.value
                backup_record.error_message = upload_result['error']
                backup_record.end_time = datetime.now()
                
                current_app.logger.error(f"فشل في رفع النسخة الاحتياطية {backup_record.backup_id}: {upload_result['error']}")
            
            # تنظيف الملفات المؤقتة
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            backup_record.status = BackupStatus.FAILED.value
            backup_record.error_message = str(e)
            backup_record.end_time = datetime.now()
            
            current_app.logger.error(f"خطأ في تنفيذ النسخة الاحتياطية {backup_record.backup_id}: {str(e)}")
        
        finally:
            # إزالة النسخة الاحتياطية من قائمة الجارية
            if backup_record.backup_id in self.running_backups:
                del self.running_backups[backup_record.backup_id]
    
    def _execute_restore(self, backup_record: BackupRecord, backup_job: BackupJob, 
                        restore_options: Dict, restore_id: str):
        """تنفيذ استعادة النسخة الاحتياطية"""
        try:
            current_app.logger.info(f"بدء استعادة النسخة الاحتياطية {backup_record.backup_id}")
            
            # تحميل الملف من التخزين
            temp_dir = f"/tmp/restore_{restore_id}"
            os.makedirs(temp_dir, exist_ok=True)
            
            download_result = self._download_backup_file(backup_record, backup_job, temp_dir)
            
            if not download_result['success']:
                raise Exception(f"فشل في تحميل الملف: {download_result['error']}")
            
            downloaded_file = download_result['file_path']
            
            # فك التشفير إذا كان مطلوباً
            if backup_record.encryption_key_id:
                decrypted_file = f"{downloaded_file}.dec"
                decrypt_result = self._decrypt_backup_file(downloaded_file, decrypted_file, backup_record.encryption_key_id)
                if decrypt_result['success']:
                    os.remove(downloaded_file)
                    downloaded_file = decrypted_file
                else:
                    raise Exception(f"فشل في فك التشفير: {decrypt_result['error']}")
            
            # التحقق من checksum
            current_checksum = self._calculate_file_checksum(downloaded_file)
            if current_checksum != backup_record.checksum:
                raise Exception("فشل في التحقق من سلامة الملف")
            
            # استخراج الأرشيف
            restore_target = restore_options.get('target_directory', '/')
            
            with tarfile.open(downloaded_file, 'r:gz') as tar:
                # فلترة الملفات المراد استعادتها
                members_to_extract = tar.getmembers()
                
                if restore_options.get('selective_restore'):
                    # استعادة انتقائية
                    selected_paths = restore_options.get('selected_paths', [])
                    members_to_extract = [
                        member for member in members_to_extract 
                        if any(member.name.startswith(path) for path in selected_paths)
                    ]
                
                # استخراج الملفات
                for member in members_to_extract:
                    try:
                        tar.extract(member, path=restore_target)
                    except Exception as e:
                        current_app.logger.warning(f"فشل في استخراج {member.name}: {str(e)}")
            
            # تنظيف الملفات المؤقتة
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            current_app.logger.info(f"تم إكمال استعادة النسخة الاحتياطية {backup_record.backup_id} بنجاح")
            
        except Exception as e:
            current_app.logger.error(f"خطأ في استعادة النسخة الاحتياطية {backup_record.backup_id}: {str(e)}")
            
            # تنظيف الملفات المؤقتة في حالة الخطأ
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _collect_files_from_source(self, source_path: str, backup_type: str, last_run: datetime = None) -> List[str]:
        """جمع الملفات من مصدر البيانات"""
        files = []
        
        if not os.path.exists(source_path):
            return files
        
        for root, dirs, filenames in os.walk(source_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                # فلترة الملفات حسب نوع النسخة الاحتياطية
                if backup_type == BackupType.INCREMENTAL.value and last_run:
                    # نسخة تزايدية: فقط الملفات المعدلة منذ آخر نسخة
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_mtime <= last_run:
                        continue
                elif backup_type == BackupType.DIFFERENTIAL.value and last_run:
                    # نسخة تفاضلية: الملفات المعدلة منذ آخر نسخة كاملة
                    # هذا يتطلب تتبع تواريخ النسخ الكاملة
                    pass
                
                files.append(file_path)
        
        return files
    
    def _encrypt_backup_file(self, input_path: str, output_path: str) -> Dict:
        """تشفير ملف النسخة الاحتياطية"""
        try:
            # إنشاء مفتاح تشفير جديد
            encryption_key = Fernet.generate_key()
            key_id = str(uuid.uuid4())
            
            # حفظ مفتاح التشفير
            self.encryption_keys[key_id] = {
                'key_data': encryption_key,
                'created_at': datetime.now()
            }
            
            # تشفير الملف
            fernet = Fernet(encryption_key)
            
            with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                while True:
                    chunk = infile.read(1024 * 1024)  # قراءة 1MB في كل مرة
                    if not chunk:
                        break
                    
                    encrypted_chunk = fernet.encrypt(chunk)
                    outfile.write(encrypted_chunk)
            
            return {
                'success': True,
                'key_id': key_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _decrypt_backup_file(self, input_path: str, output_path: str, key_id: str) -> Dict:
        """فك تشفير ملف النسخة الاحتياطية"""
        try:
            # الحصول على مفتاح التشفير
            if key_id not in self.encryption_keys:
                return {
                    'success': False,
                    'error': 'مفتاح التشفير غير موجود'
                }
            
            encryption_key = self.encryption_keys[key_id]['key_data']
            fernet = Fernet(encryption_key)
            
            # فك تشفير الملف
            with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                while True:
                    chunk = infile.read(1024 * 1024 + 44)  # حجم chunk مشفر
                    if not chunk:
                        break
                    
                    try:
                        decrypted_chunk = fernet.decrypt(chunk)
                        outfile.write(decrypted_chunk)
                    except Exception:
                        # آخر chunk قد يكون أصغر
                        break
            
            return {
                'success': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """حساب checksum للملف"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _upload_backup_file(self, file_path: str, backup_job: BackupJob, backup_record: BackupRecord) -> Dict:
        """رفع ملف النسخة الاحتياطية للتخزين"""
        try:
            storage_provider = backup_job.storage_provider
            
            if storage_provider == StorageProvider.LOCAL.value:
                # تخزين محلي
                local_storage_path = backup_job.storage_path
                os.makedirs(local_storage_path, exist_ok=True)
                
                destination_path = os.path.join(local_storage_path, f"backup_{backup_record.backup_id}.tar.gz.enc")
                shutil.copy2(file_path, destination_path)
                
                return {
                    'success': True,
                    'storage_path': destination_path
                }
            
            elif storage_provider == StorageProvider.AWS_S3.value:
                # رفع لـ AWS S3
                # في التطبيق الحقيقي، سيتم استخدام boto3
                return {
                    'success': True,
                    'storage_path': f"s3://backup-bucket/{backup_record.backup_id}.tar.gz.enc"
                }
            
            elif storage_provider == StorageProvider.GOOGLE_CLOUD.value:
                # رفع لـ Google Cloud Storage
                return {
                    'success': True,
                    'storage_path': f"gs://backup-bucket/{backup_record.backup_id}.tar.gz.enc"
                }
            
            else:
                return {
                    'success': False,
                    'error': 'موفر تخزين غير مدعوم'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _download_backup_file(self, backup_record: BackupRecord, backup_job: BackupJob, temp_dir: str) -> Dict:
        """تحميل ملف النسخة الاحتياطية من التخزين"""
        try:
            storage_provider = backup_job.storage_provider
            storage_path = backup_record.storage_path
            
            local_file_path = os.path.join(temp_dir, f"backup_{backup_record.backup_id}.tar.gz.enc")
            
            if storage_provider == StorageProvider.LOCAL.value:
                # نسخ من التخزين المحلي
                if os.path.exists(storage_path):
                    shutil.copy2(storage_path, local_file_path)
                    return {
                        'success': True,
                        'file_path': local_file_path
                    }
                else:
                    return {
                        'success': False,
                        'error': 'ملف النسخة الاحتياطية غير موجود'
                    }
            
            # موفري التخزين السحابي الآخرين
            # في التطبيق الحقيقي، سيتم تنفيذ التحميل الفعلي
            
            return {
                'success': False,
                'error': 'موفر تخزين غير مدعوم للتحميل'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _delete_backup_file(self, backup_record: BackupRecord, backup_job: BackupJob):
        """حذف ملف النسخة الاحتياطية من التخزين"""
        try:
            storage_provider = backup_job.storage_provider
            storage_path = backup_record.storage_path
            
            if storage_provider == StorageProvider.LOCAL.value:
                if os.path.exists(storage_path):
                    os.remove(storage_path)
            
            # موفري التخزين السحابي الآخرين
            # في التطبيق الحقيقي، سيتم تنفيذ الحذف الفعلي
            
        except Exception as e:
            current_app.logger.error(f"خطأ في حذف ملف النسخة الاحتياطية: {str(e)}")
    
    def _verify_backup_file(self, backup_record: BackupRecord, backup_job: BackupJob) -> Dict:
        """التحقق من سلامة ملف النسخة الاحتياطية"""
        try:
            # تحميل الملف مؤقتاً للتحقق
            temp_dir = f"/tmp/verify_{backup_record.backup_id}"
            os.makedirs(temp_dir, exist_ok=True)
            
            download_result = self._download_backup_file(backup_record, backup_job, temp_dir)
            
            if not download_result['success']:
                return {
                    'valid': False,
                    'error': download_result['error']
                }
            
            downloaded_file = download_result['file_path']
            
            # حساب checksum والمقارنة
            current_checksum = self._calculate_file_checksum(downloaded_file)
            checksum_match = current_checksum == backup_record.checksum
            
            # فحص حجم الملف
            current_size = os.path.getsize(downloaded_file)
            size_match = current_size == backup_record.compressed_size_bytes
            
            # تنظيف الملفات المؤقتة
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return {
                'valid': checksum_match and size_match,
                'checksum_match': checksum_match,
                'size_match': size_match,
                'current_checksum': current_checksum,
                'expected_checksum': backup_record.checksum
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _format_backup_record(self, record: BackupRecord) -> Dict:
        """تنسيق سجل النسخة الاحتياطية للعرض"""
        duration = None
        if record.end_time and record.start_time:
            duration = (record.end_time - record.start_time).total_seconds()
        
        return {
            'backup_id': record.backup_id,
            'backup_type': record.backup_type,
            'status': record.status,
            'start_time': record.start_time.isoformat(),
            'end_time': record.end_time.isoformat() if record.end_time else None,
            'duration_seconds': duration,
            'file_count': record.file_count,
            'total_size_mb': round(record.total_size_bytes / (1024 * 1024), 2),
            'compressed_size_mb': round(record.compressed_size_bytes / (1024 * 1024), 2),
            'compression_ratio': round((1 - record.compressed_size_bytes / record.total_size_bytes) * 100, 1) if record.total_size_bytes > 0 else 0,
            'storage_path': record.storage_path,
            'encrypted': bool(record.encryption_key_id),
            'error_message': record.error_message
        }
    
    def _estimate_backup_duration(self, backup_job: BackupJob) -> str:
        """تقدير مدة النسخة الاحتياطية"""
        # تقدير بسيط بناءً على حجم البيانات ونوع النسخة
        if backup_job.backup_type == BackupType.FULL.value:
            return "2-4 ساعات"
        elif backup_job.backup_type == BackupType.INCREMENTAL.value:
            return "30-60 دقيقة"
        else:
            return "1-2 ساعة"
    
    def _estimate_restore_duration(self, backup_record: BackupRecord) -> str:
        """تقدير مدة الاستعادة"""
        size_gb = backup_record.compressed_size_bytes / (1024**3)
        
        if size_gb < 1:
            return "10-30 دقيقة"
        elif size_gb < 10:
            return "30-90 دقيقة"
        else:
            return "1-3 ساعات"
    
    def _calculate_storage_usage(self) -> Dict:
        """حساب استخدام التخزين"""
        total_size = 0
        backup_count = 0
        
        for records in self.backup_records.values():
            for record in records:
                if record.status == BackupStatus.COMPLETED.value:
                    total_size += record.compressed_size_bytes
                    backup_count += 1
        
        return {
            'total_backups': backup_count,
            'total_size_gb': round(total_size / (1024**3), 2),
            'average_backup_size_mb': round(total_size / backup_count / (1024**2), 2) if backup_count > 0 else 0
        }
    
    def _generate_backup_recommendations(self, backups: List[BackupRecord]) -> List[str]:
        """إنشاء توصيات النسخ الاحتياطية"""
        recommendations = []
        
        if not backups:
            recommendations.append("لا توجد نسخ احتياطية في الفترة المحددة")
            return recommendations
        
        # تحليل معدل النجاح
        failed_backups = [b for b in backups if b.status == BackupStatus.FAILED.value]
        failure_rate = len(failed_backups) / len(backups) * 100
        
        if failure_rate > 10:
            recommendations.append("معدل فشل النسخ الاحتياطية مرتفع، يُنصح بمراجعة الإعدادات")
        
        # تحليل أحجام النسخ
        avg_size = sum(b.compressed_size_bytes for b in backups) / len(backups)
        if avg_size > 10 * 1024**3:  # أكبر من 10GB
            recommendations.append("أحجام النسخ الاحتياطية كبيرة، يُنصح بتحسين الضغط أو الفلترة")
        
        # تحليل أوقات النسخ
        completed_backups = [b for b in backups if b.status == BackupStatus.COMPLETED.value and b.end_time]
        if completed_backups:
            avg_duration = sum((b.end_time - b.start_time).total_seconds() for b in completed_backups) / len(completed_backups)
            if avg_duration > 4 * 3600:  # أكثر من 4 ساعات
                recommendations.append("أوقات النسخ الاحتياطية طويلة، يُنصح بتحسين الأداء")
        
        return recommendations

