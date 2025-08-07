"""
خدمة العمل بدون إنترنت والمزامنة الذكية
نظام شامل للعمل في البيئات منخفضة الاتصال أو بدون إنترنت
"""

import os
import json
import uuid
import sqlite3
import gzip
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import hashlib

class SyncPriority(Enum):
    CRITICAL = "حرج"      # بيانات طبية حرجة
    HIGH = "عالي"         # مواعيد، أدوية
    MEDIUM = "متوسط"      # تقارير، إحصائيات
    LOW = "منخفض"         # إعدادات، تفضيلات

class DataType(Enum):
    PATIENT_RECORD = "سجل المريض"
    APPOINTMENT = "موعد طبي"
    MEDICATION = "دواء"
    LAB_RESULT = "نتيجة تحليل"
    PRESCRIPTION = "روشتة"
    VITAL_SIGNS = "علامات حيوية"
    EMERGENCY_CONTACT = "جهة اتصال طوارئ"
    MEDICAL_HISTORY = "تاريخ طبي"
    SETTINGS = "إعدادات"
    CACHE_DATA = "بيانات مؤقتة"

class SyncStatus(Enum):
    PENDING = "في الانتظار"
    IN_PROGRESS = "قيد التنفيذ"
    COMPLETED = "مكتمل"
    FAILED = "فاشل"
    CONFLICT = "تعارض"

@dataclass
class OfflineRecord:
    record_id: str
    data_type: str
    patient_id: str
    data: Dict
    created_at: datetime
    modified_at: datetime
    sync_priority: str
    sync_status: str
    version: int
    checksum: str
    size_bytes: int
    is_encrypted: bool

@dataclass
class SyncOperation:
    operation_id: str
    operation_type: str  # create, update, delete
    record_id: str
    data_type: str
    data_before: Optional[Dict]
    data_after: Optional[Dict]
    timestamp: datetime
    user_id: str
    device_id: str
    sync_priority: str
    retry_count: int
    last_error: Optional[str]

@dataclass
class ConflictResolution:
    conflict_id: str
    record_id: str
    local_version: int
    server_version: int
    local_data: Dict
    server_data: Dict
    resolution_strategy: str
    resolved_data: Optional[Dict]
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]

@dataclass
class OfflineSession:
    session_id: str
    user_id: str
    device_id: str
    start_time: datetime
    end_time: Optional[datetime]
    operations_count: int
    data_downloaded_mb: float
    data_uploaded_mb: float
    sync_conflicts: int
    last_sync_time: Optional[datetime]

class OfflineModeService:
    def __init__(self):
        """تهيئة خدمة العمل بدون إنترنت"""
        
        # إعدادات النظام
        self.system_settings = {
            'offline_db_path': '/tmp/sahty_offline.db',
            'max_offline_days': 30,          # أقصى مدة عمل بدون إنترنت
            'sync_batch_size': 100,          # عدد السجلات في كل دفعة مزامنة
            'max_retry_attempts': 5,         # أقصى عدد محاولات
            'compression_enabled': True,      # ضغط البيانات
            'encryption_enabled': True,       # تشفير البيانات الحساسة
            'auto_sync_interval_minutes': 15, # مزامنة تلقائية كل 15 دقيقة
            'conflict_resolution_timeout_hours': 24, # مهلة حل التعارضات
            'cache_size_limit_mb': 500,      # حد حجم التخزين المؤقت
            'priority_sync_interval_minutes': 5  # مزامنة البيانات الحرجة كل 5 دقائق
        }
        
        # قواعد البيانات المحلية
        self.offline_records = {}
        self.sync_operations = {}
        self.conflict_resolutions = {}
        self.offline_sessions = {}
        
        # طوابير المزامنة
        self.sync_queue = queue.PriorityQueue()
        self.conflict_queue = queue.Queue()
        
        # إحصائيات الوضع غير المتصل
        self.offline_stats = {
            'total_offline_time_hours': 0,
            'records_created_offline': 0,
            'records_updated_offline': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'conflicts_resolved': 0,
            'data_saved_mb': 0,
            'last_successful_sync': None
        }
        
        # تهيئة قاعدة البيانات المحلية
        self._initialize_offline_database()
        
        # بدء خدمات المزامنة
        self._start_sync_services()
    
    def enable_offline_mode(self, user_id: str, device_id: str) -> Dict:
        """
        تفعيل الوضع غير المتصل
        
        Args:
            user_id: معرف المستخدم
            device_id: معرف الجهاز
            
        Returns:
            Dict: نتيجة التفعيل
        """
        try:
            # إنشاء جلسة عمل غير متصل
            session = OfflineSession(
                session_id=str(uuid.uuid4()),
                user_id=user_id,
                device_id=device_id,
                start_time=datetime.now(),
                end_time=None,
                operations_count=0,
                data_downloaded_mb=0,
                data_uploaded_mb=0,
                sync_conflicts=0,
                last_sync_time=None
            )
            
            self.offline_sessions[session.session_id] = session
            
            # تحميل البيانات الأساسية للعمل بدون إنترنت
            essential_data = self._download_essential_data(user_id)
            
            # حفظ البيانات في قاعدة البيانات المحلية
            saved_records = self._save_offline_data(essential_data, user_id)
            
            # حساب حجم البيانات المحملة
            session.data_downloaded_mb = sum(record.size_bytes for record in saved_records.values()) / (1024 * 1024)
            
            return {
                'success': True,
                'session_id': session.session_id,
                'offline_mode_enabled': True,
                'essential_data_downloaded': len(saved_records),
                'data_size_mb': round(session.data_downloaded_mb, 2),
                'offline_capabilities': {
                    'view_patient_records': True,
                    'create_appointments': True,
                    'update_medications': True,
                    'record_vital_signs': True,
                    'emergency_contacts': True,
                    'basic_calculations': True,
                    'offline_forms': True
                },
                'limitations': {
                    'no_real_time_sync': True,
                    'limited_search': True,
                    'no_external_integrations': True,
                    'reduced_ai_features': True
                },
                'estimated_offline_duration': f"{self.system_settings['max_offline_days']} أيام"
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تفعيل الوضع غير المتصل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تفعيل الوضع غير المتصل'
            }
    
    def create_offline_record(self, data_type: str, patient_id: str, data: Dict, user_id: str, priority: str = SyncPriority.MEDIUM.value) -> Dict:
        """
        إنشاء سجل جديد في الوضع غير المتصل
        
        Args:
            data_type: نوع البيانات
            patient_id: معرف المريض
            data: البيانات
            user_id: معرف المستخدم
            priority: أولوية المزامنة
            
        Returns:
            Dict: نتيجة الإنشاء
        """
        try:
            # إنشاء السجل
            record = OfflineRecord(
                record_id=str(uuid.uuid4()),
                data_type=data_type,
                patient_id=patient_id,
                data=data,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                sync_priority=priority,
                sync_status=SyncStatus.PENDING.value,
                version=1,
                checksum=self._calculate_checksum(data),
                size_bytes=len(json.dumps(data, ensure_ascii=False).encode('utf-8')),
                is_encrypted=self._should_encrypt_data(data_type)
            )
            
            # تشفير البيانات الحساسة
            if record.is_encrypted:
                record.data = self._encrypt_data(record.data)
            
            # حفظ السجل
            self.offline_records[record.record_id] = record
            self._save_to_offline_db(record)
            
            # إنشاء عملية مزامنة
            sync_operation = SyncOperation(
                operation_id=str(uuid.uuid4()),
                operation_type='create',
                record_id=record.record_id,
                data_type=data_type,
                data_before=None,
                data_after=data,
                timestamp=datetime.now(),
                user_id=user_id,
                device_id='current_device',
                sync_priority=priority,
                retry_count=0,
                last_error=None
            )
            
            self.sync_operations[sync_operation.operation_id] = sync_operation
            
            # إضافة للطابور حسب الأولوية
            priority_value = self._get_priority_value(priority)
            self.sync_queue.put((priority_value, sync_operation.operation_id))
            
            # تحديث الإحصائيات
            self.offline_stats['records_created_offline'] += 1
            self.offline_stats['data_saved_mb'] += record.size_bytes / (1024 * 1024)
            
            return {
                'success': True,
                'record_id': record.record_id,
                'operation_id': sync_operation.operation_id,
                'sync_priority': priority,
                'estimated_sync_time': self._estimate_sync_time(priority),
                'offline_saved': True
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء سجل غير متصل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء السجل'
            }
    
    def update_offline_record(self, record_id: str, updated_data: Dict, user_id: str) -> Dict:
        """
        تحديث سجل في الوضع غير المتصل
        
        Args:
            record_id: معرف السجل
            updated_data: البيانات المحدثة
            user_id: معرف المستخدم
            
        Returns:
            Dict: نتيجة التحديث
        """
        try:
            # البحث عن السجل
            if record_id not in self.offline_records:
                return {
                    'success': False,
                    'error': 'السجل غير موجود'
                }
            
            record = self.offline_records[record_id]
            
            # حفظ البيانات القديمة
            old_data = record.data.copy()
            if record.is_encrypted:
                old_data = self._decrypt_data(old_data)
            
            # تحديث السجل
            record.data = updated_data
            record.modified_at = datetime.now()
            record.version += 1
            record.checksum = self._calculate_checksum(updated_data)
            record.sync_status = SyncStatus.PENDING.value
            
            # تشفير البيانات الجديدة
            if record.is_encrypted:
                record.data = self._encrypt_data(record.data)
            
            # حفظ التحديث
            self._save_to_offline_db(record)
            
            # إنشاء عملية مزامنة
            sync_operation = SyncOperation(
                operation_id=str(uuid.uuid4()),
                operation_type='update',
                record_id=record_id,
                data_type=record.data_type,
                data_before=old_data,
                data_after=updated_data,
                timestamp=datetime.now(),
                user_id=user_id,
                device_id='current_device',
                sync_priority=record.sync_priority,
                retry_count=0,
                last_error=None
            )
            
            self.sync_operations[sync_operation.operation_id] = sync_operation
            
            # إضافة للطابور
            priority_value = self._get_priority_value(record.sync_priority)
            self.sync_queue.put((priority_value, sync_operation.operation_id))
            
            # تحديث الإحصائيات
            self.offline_stats['records_updated_offline'] += 1
            
            return {
                'success': True,
                'record_id': record_id,
                'operation_id': sync_operation.operation_id,
                'version': record.version,
                'sync_queued': True
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحديث سجل غير متصل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تحديث السجل'
            }
    
    def get_offline_records(self, patient_id: str = None, data_type: str = None, limit: int = 100) -> Dict:
        """
        الحصول على السجلات المحفوظة محلياً
        
        Args:
            patient_id: معرف المريض (اختياري)
            data_type: نوع البيانات (اختياري)
            limit: عدد السجلات المطلوبة
            
        Returns:
            Dict: السجلات المطلوبة
        """
        try:
            # فلترة السجلات
            filtered_records = []
            
            for record in self.offline_records.values():
                # تطبيق الفلاتر
                if patient_id and record.patient_id != patient_id:
                    continue
                if data_type and record.data_type != data_type:
                    continue
                
                # فك تشفير البيانات إذا لزم الأمر
                record_data = record.data
                if record.is_encrypted:
                    record_data = self._decrypt_data(record_data)
                
                filtered_records.append({
                    'record_id': record.record_id,
                    'data_type': record.data_type,
                    'patient_id': record.patient_id,
                    'data': record_data,
                    'created_at': record.created_at.isoformat(),
                    'modified_at': record.modified_at.isoformat(),
                    'sync_status': record.sync_status,
                    'version': record.version,
                    'size_bytes': record.size_bytes
                })
            
            # ترتيب حسب تاريخ التعديل
            filtered_records.sort(key=lambda x: x['modified_at'], reverse=True)
            
            # تطبيق الحد الأقصى
            limited_records = filtered_records[:limit]
            
            return {
                'success': True,
                'records': limited_records,
                'total_found': len(filtered_records),
                'returned_count': len(limited_records),
                'filters_applied': {
                    'patient_id': patient_id,
                    'data_type': data_type,
                    'limit': limit
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في جلب السجلات غير المتصلة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في جلب السجلات'
            }
    
    def sync_with_server(self, force_sync: bool = False) -> Dict:
        """
        مزامنة البيانات مع الخادم
        
        Args:
            force_sync: فرض المزامنة حتى لو لم يحن وقتها
            
        Returns:
            Dict: نتيجة المزامنة
        """
        try:
            # التحقق من الاتصال بالإنترنت
            if not self._check_internet_connection():
                return {
                    'success': False,
                    'error': 'لا يوجد اتصال بالإنترنت',
                    'retry_in_minutes': 5
                }
            
            sync_results = {
                'uploaded_records': 0,
                'downloaded_records': 0,
                'conflicts_detected': 0,
                'conflicts_resolved': 0,
                'failed_operations': 0,
                'sync_duration_seconds': 0
            }
            
            start_time = datetime.now()
            
            # مزامنة العمليات المعلقة
            upload_result = self._upload_pending_operations()
            sync_results.update(upload_result)
            
            # تحميل التحديثات من الخادم
            download_result = self._download_server_updates()
            sync_results.update(download_result)
            
            # حل التعارضات
            conflict_result = self._resolve_sync_conflicts()
            sync_results.update(conflict_result)
            
            # تنظيف البيانات القديمة
            cleanup_result = self._cleanup_old_data()
            
            # حساب مدة المزامنة
            sync_results['sync_duration_seconds'] = (datetime.now() - start_time).total_seconds()
            
            # تحديث الإحصائيات
            if sync_results['uploaded_records'] > 0 or sync_results['downloaded_records'] > 0:
                self.offline_stats['successful_syncs'] += 1
                self.offline_stats['last_successful_sync'] = datetime.now()
            else:
                self.offline_stats['failed_syncs'] += 1
            
            return {
                'success': True,
                'sync_results': sync_results,
                'next_sync_time': (datetime.now() + timedelta(minutes=self.system_settings['auto_sync_interval_minutes'])).isoformat(),
                'recommendations': self._generate_sync_recommendations(sync_results)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في المزامنة: {str(e)}")
            self.offline_stats['failed_syncs'] += 1
            return {
                'success': False,
                'error': 'حدث خطأ في المزامنة',
                'retry_in_minutes': 10
            }
    
    def resolve_conflict(self, conflict_id: str, resolution_strategy: str, user_id: str) -> Dict:
        """
        حل تعارض في البيانات
        
        Args:
            conflict_id: معرف التعارض
            resolution_strategy: استراتيجية الحل
            user_id: معرف المستخدم
            
        Returns:
            Dict: نتيجة حل التعارض
        """
        try:
            if conflict_id not in self.conflict_resolutions:
                return {
                    'success': False,
                    'error': 'التعارض غير موجود'
                }
            
            conflict = self.conflict_resolutions[conflict_id]
            
            # تطبيق استراتيجية الحل
            if resolution_strategy == 'use_local':
                resolved_data = conflict.local_data
            elif resolution_strategy == 'use_server':
                resolved_data = conflict.server_data
            elif resolution_strategy == 'merge':
                resolved_data = self._merge_conflicted_data(conflict.local_data, conflict.server_data)
            else:
                return {
                    'success': False,
                    'error': 'استراتيجية حل غير صالحة'
                }
            
            # تحديث التعارض
            conflict.resolution_strategy = resolution_strategy
            conflict.resolved_data = resolved_data
            conflict.resolved_by = user_id
            conflict.resolved_at = datetime.now()
            
            # تحديث السجل الأصلي
            if conflict.record_id in self.offline_records:
                record = self.offline_records[conflict.record_id]
                record.data = resolved_data
                record.modified_at = datetime.now()
                record.version += 1
                record.sync_status = SyncStatus.PENDING.value
                
                # حفظ التحديث
                self._save_to_offline_db(record)
            
            # تحديث الإحصائيات
            self.offline_stats['conflicts_resolved'] += 1
            
            return {
                'success': True,
                'conflict_id': conflict_id,
                'resolution_strategy': resolution_strategy,
                'resolved_data': resolved_data,
                'resolved_at': conflict.resolved_at.isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في حل التعارض: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في حل التعارض'
            }
    
    def get_offline_statistics(self) -> Dict:
        """
        الحصول على إحصائيات الوضع غير المتصل
        
        Returns:
            Dict: الإحصائيات
        """
        try:
            # حساب الإحصائيات الحالية
            pending_operations = len([op for op in self.sync_operations.values() if op.retry_count < self.system_settings['max_retry_attempts']])
            unresolved_conflicts = len([c for c in self.conflict_resolutions.values() if not c.resolved_at])
            
            # حساب حجم البيانات المحلية
            total_size_mb = sum(record.size_bytes for record in self.offline_records.values()) / (1024 * 1024)
            
            # حساب مدة الجلسات غير المتصلة
            active_sessions = [s for s in self.offline_sessions.values() if not s.end_time]
            total_offline_hours = sum(
                (datetime.now() - session.start_time).total_seconds() / 3600
                for session in active_sessions
            )
            
            return {
                'success': True,
                'statistics': {
                    'offline_mode_active': len(active_sessions) > 0,
                    'active_sessions': len(active_sessions),
                    'total_offline_records': len(self.offline_records),
                    'pending_sync_operations': pending_operations,
                    'unresolved_conflicts': unresolved_conflicts,
                    'local_data_size_mb': round(total_size_mb, 2),
                    'current_offline_duration_hours': round(total_offline_hours, 2),
                    'sync_statistics': {
                        'successful_syncs': self.offline_stats['successful_syncs'],
                        'failed_syncs': self.offline_stats['failed_syncs'],
                        'last_successful_sync': self.offline_stats['last_successful_sync'].isoformat() if self.offline_stats['last_successful_sync'] else None
                    },
                    'data_statistics': {
                        'records_created_offline': self.offline_stats['records_created_offline'],
                        'records_updated_offline': self.offline_stats['records_updated_offline'],
                        'conflicts_resolved': self.offline_stats['conflicts_resolved'],
                        'total_data_saved_mb': round(self.offline_stats['data_saved_mb'], 2)
                    }
                },
                'recommendations': self._generate_offline_recommendations()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في جلب إحصائيات الوضع غير المتصل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في جلب الإحصائيات'
            }
    
    # الدوال المساعدة
    def _initialize_offline_database(self):
        """تهيئة قاعدة البيانات المحلية"""
        
        try:
            conn = sqlite3.connect(self.system_settings['offline_db_path'])
            cursor = conn.cursor()
            
            # إنشاء جداول قاعدة البيانات المحلية
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS offline_records (
                    record_id TEXT PRIMARY KEY,
                    data_type TEXT NOT NULL,
                    patient_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    modified_at TEXT NOT NULL,
                    sync_priority TEXT NOT NULL,
                    sync_status TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    is_encrypted BOOLEAN NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_operations (
                    operation_id TEXT PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    data_before TEXT,
                    data_after TEXT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    sync_priority TEXT NOT NULL,
                    retry_count INTEGER NOT NULL,
                    last_error TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conflict_resolutions (
                    conflict_id TEXT PRIMARY KEY,
                    record_id TEXT NOT NULL,
                    local_version INTEGER NOT NULL,
                    server_version INTEGER NOT NULL,
                    local_data TEXT NOT NULL,
                    server_data TEXT NOT NULL,
                    resolution_strategy TEXT,
                    resolved_data TEXT,
                    resolved_by TEXT,
                    resolved_at TEXT
                )
            ''')
            
            # إنشاء فهارس للأداء
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patient_id ON offline_records(patient_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_type ON offline_records(data_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_status ON offline_records(sync_status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_priority ON sync_operations(sync_priority)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تهيئة قاعدة البيانات المحلية: {str(e)}")
    
    def _start_sync_services(self):
        """بدء خدمات المزامنة في الخلفية"""
        
        # خدمة المزامنة التلقائية
        def auto_sync_worker():
            while True:
                try:
                    # انتظار الفترة المحددة
                    threading.Event().wait(self.system_settings['auto_sync_interval_minutes'] * 60)
                    
                    # تنفيذ المزامنة التلقائية
                    if self._check_internet_connection():
                        self.sync_with_server()
                        
                except Exception as e:
                    current_app.logger.error(f"خطأ في المزامنة التلقائية: {str(e)}")
        
        # خدمة معالجة طابور المزامنة
        def sync_queue_worker():
            while True:
                try:
                    # الحصول على العملية التالية
                    priority, operation_id = self.sync_queue.get(timeout=60)
                    
                    # معالجة العملية
                    if operation_id in self.sync_operations:
                        operation = self.sync_operations[operation_id]
                        self._process_sync_operation(operation)
                    
                    self.sync_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    current_app.logger.error(f"خطأ في معالجة طابور المزامنة: {str(e)}")
        
        # بدء الخدمات في خيوط منفصلة
        auto_sync_thread = threading.Thread(target=auto_sync_worker, daemon=True)
        sync_queue_thread = threading.Thread(target=sync_queue_worker, daemon=True)
        
        auto_sync_thread.start()
        sync_queue_thread.start()
    
    def _download_essential_data(self, user_id: str) -> Dict:
        """تحميل البيانات الأساسية للعمل بدون إنترنت"""
        
        # محاكاة تحميل البيانات الأساسية
        essential_data = {
            'patient_records': [
                {
                    'patient_id': f'patient_{i}',
                    'name': f'مريض {i}',
                    'national_id': f'1234567890123{i}',
                    'phone': f'0100000000{i}',
                    'emergency_contact': f'0120000000{i}',
                    'blood_type': 'O+',
                    'allergies': ['البنسلين'],
                    'chronic_conditions': ['السكري']
                }
                for i in range(1, 11)  # 10 مرضى
            ],
            'medications': [
                {
                    'medication_id': f'med_{i}',
                    'name': f'دواء {i}',
                    'dosage': '500mg',
                    'frequency': 'مرتين يومياً',
                    'instructions': 'بعد الأكل'
                }
                for i in range(1, 21)  # 20 دواء
            ],
            'emergency_contacts': [
                {
                    'name': 'الإسعاف',
                    'phone': '123',
                    'type': 'emergency'
                },
                {
                    'name': 'مستشفى القاهرة',
                    'phone': '0225555555',
                    'type': 'hospital'
                }
            ]
        }
        
        return essential_data
    
    def _save_offline_data(self, data: Dict, user_id: str) -> Dict:
        """حفظ البيانات في قاعدة البيانات المحلية"""
        
        saved_records = {}
        
        try:
            # حفظ سجلات المرضى
            for patient_data in data.get('patient_records', []):
                record = OfflineRecord(
                    record_id=str(uuid.uuid4()),
                    data_type=DataType.PATIENT_RECORD.value,
                    patient_id=patient_data['patient_id'],
                    data=patient_data,
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    sync_priority=SyncPriority.HIGH.value,
                    sync_status=SyncStatus.COMPLETED.value,
                    version=1,
                    checksum=self._calculate_checksum(patient_data),
                    size_bytes=len(json.dumps(patient_data, ensure_ascii=False).encode('utf-8')),
                    is_encrypted=True
                )
                
                if record.is_encrypted:
                    record.data = self._encrypt_data(record.data)
                
                saved_records[record.record_id] = record
                self.offline_records[record.record_id] = record
                self._save_to_offline_db(record)
            
            # حفظ الأدوية
            for medication_data in data.get('medications', []):
                record = OfflineRecord(
                    record_id=str(uuid.uuid4()),
                    data_type=DataType.MEDICATION.value,
                    patient_id='general',
                    data=medication_data,
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    sync_priority=SyncPriority.MEDIUM.value,
                    sync_status=SyncStatus.COMPLETED.value,
                    version=1,
                    checksum=self._calculate_checksum(medication_data),
                    size_bytes=len(json.dumps(medication_data, ensure_ascii=False).encode('utf-8')),
                    is_encrypted=False
                )
                
                saved_records[record.record_id] = record
                self.offline_records[record.record_id] = record
                self._save_to_offline_db(record)
            
            # حفظ جهات الاتصال الطارئة
            for contact_data in data.get('emergency_contacts', []):
                record = OfflineRecord(
                    record_id=str(uuid.uuid4()),
                    data_type=DataType.EMERGENCY_CONTACT.value,
                    patient_id='general',
                    data=contact_data,
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    sync_priority=SyncPriority.CRITICAL.value,
                    sync_status=SyncStatus.COMPLETED.value,
                    version=1,
                    checksum=self._calculate_checksum(contact_data),
                    size_bytes=len(json.dumps(contact_data, ensure_ascii=False).encode('utf-8')),
                    is_encrypted=False
                )
                
                saved_records[record.record_id] = record
                self.offline_records[record.record_id] = record
                self._save_to_offline_db(record)
            
            return saved_records
            
        except Exception as e:
            current_app.logger.error(f"خطأ في حفظ البيانات غير المتصلة: {str(e)}")
            return {}
    
    def _save_to_offline_db(self, record: OfflineRecord):
        """حفظ سجل في قاعدة البيانات المحلية"""
        
        try:
            conn = sqlite3.connect(self.system_settings['offline_db_path'])
            cursor = conn.cursor()
            
            # تحويل البيانات إلى JSON
            data_json = json.dumps(record.data, ensure_ascii=False)
            
            # حفظ أو تحديث السجل
            cursor.execute('''
                INSERT OR REPLACE INTO offline_records 
                (record_id, data_type, patient_id, data, created_at, modified_at, 
                 sync_priority, sync_status, version, checksum, size_bytes, is_encrypted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.record_id, record.data_type, record.patient_id, data_json,
                record.created_at.isoformat(), record.modified_at.isoformat(),
                record.sync_priority, record.sync_status, record.version,
                record.checksum, record.size_bytes, record.is_encrypted
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            current_app.logger.error(f"خطأ في حفظ السجل في قاعدة البيانات المحلية: {str(e)}")
    
    def _calculate_checksum(self, data: Dict) -> str:
        """حساب checksum للبيانات"""
        
        data_string = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_string.encode('utf-8')).hexdigest()
    
    def _should_encrypt_data(self, data_type: str) -> bool:
        """تحديد ما إذا كانت البيانات تحتاج تشفير"""
        
        sensitive_types = [
            DataType.PATIENT_RECORD.value,
            DataType.LAB_RESULT.value,
            DataType.MEDICAL_HISTORY.value,
            DataType.PRESCRIPTION.value
        ]
        
        return data_type in sensitive_types
    
    def _encrypt_data(self, data: Dict) -> Dict:
        """تشفير البيانات الحساسة"""
        
        # محاكاة تشفير بسيط (في التطبيق الحقيقي، استخدم مكتبة تشفير قوية)
        encrypted_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                # تشفير بسيط بـ base64
                import base64
                encrypted_value = base64.b64encode(value.encode('utf-8')).decode('utf-8')
                encrypted_data[f"enc_{key}"] = encrypted_value
            else:
                encrypted_data[key] = value
        
        return encrypted_data
    
    def _decrypt_data(self, encrypted_data: Dict) -> Dict:
        """فك تشفير البيانات"""
        
        # محاكاة فك تشفير بسيط
        decrypted_data = {}
        for key, value in encrypted_data.items():
            if key.startswith("enc_") and isinstance(value, str):
                # فك تشفير base64
                import base64
                try:
                    decrypted_value = base64.b64decode(value.encode('utf-8')).decode('utf-8')
                    original_key = key[4:]  # إزالة "enc_"
                    decrypted_data[original_key] = decrypted_value
                except:
                    decrypted_data[key] = value
            else:
                decrypted_data[key] = value
        
        return decrypted_data
    
    def _get_priority_value(self, priority: str) -> int:
        """تحويل الأولوية إلى قيمة رقمية للترتيب"""
        
        priority_values = {
            SyncPriority.CRITICAL.value: 1,
            SyncPriority.HIGH.value: 2,
            SyncPriority.MEDIUM.value: 3,
            SyncPriority.LOW.value: 4
        }
        
        return priority_values.get(priority, 3)
    
    def _estimate_sync_time(self, priority: str) -> str:
        """تقدير وقت المزامنة"""
        
        if priority == SyncPriority.CRITICAL.value:
            return "فوري"
        elif priority == SyncPriority.HIGH.value:
            return "خلال 5 دقائق"
        elif priority == SyncPriority.MEDIUM.value:
            return "خلال 15 دقيقة"
        else:
            return "خلال ساعة"
    
    def _check_internet_connection(self) -> bool:
        """فحص الاتصال بالإنترنت"""
        
        try:
            # محاكاة فحص الاتصال
            # في التطبيق الحقيقي، استخدم ping أو HTTP request
            import random
            return random.choice([True, False])  # محاكاة عشوائية
            
        except:
            return False
    
    def _upload_pending_operations(self) -> Dict:
        """رفع العمليات المعلقة للخادم"""
        
        uploaded = 0
        failed = 0
        
        # محاكاة رفع العمليات
        for operation in self.sync_operations.values():
            if operation.retry_count < self.system_settings['max_retry_attempts']:
                # محاكاة نجاح/فشل الرفع
                import random
                if random.choice([True, True, False]):  # 66% نجاح
                    uploaded += 1
                else:
                    failed += 1
                    operation.retry_count += 1
                    operation.last_error = "فشل في الاتصال بالخادم"
        
        return {
            'uploaded_records': uploaded,
            'failed_operations': failed
        }
    
    def _download_server_updates(self) -> Dict:
        """تحميل التحديثات من الخادم"""
        
        # محاكاة تحميل التحديثات
        import random
        downloaded = random.randint(0, 10)
        
        return {
            'downloaded_records': downloaded
        }
    
    def _resolve_sync_conflicts(self) -> Dict:
        """حل تعارضات المزامنة"""
        
        conflicts_detected = 0
        conflicts_resolved = 0
        
        # محاكاة كشف وحل التعارضات
        for record in self.offline_records.values():
            if record.sync_status == SyncStatus.CONFLICT.value:
                conflicts_detected += 1
                
                # محاولة حل تلقائي
                if self._auto_resolve_conflict(record):
                    conflicts_resolved += 1
        
        return {
            'conflicts_detected': conflicts_detected,
            'conflicts_resolved': conflicts_resolved
        }
    
    def _auto_resolve_conflict(self, record: OfflineRecord) -> bool:
        """حل تلقائي للتعارض"""
        
        # استراتيجية بسيطة: استخدام النسخة الأحدث
        record.sync_status = SyncStatus.PENDING.value
        return True
    
    def _cleanup_old_data(self) -> Dict:
        """تنظيف البيانات القديمة"""
        
        cleaned_records = 0
        cutoff_date = datetime.now() - timedelta(days=self.system_settings['max_offline_days'])
        
        # حذف السجلات القديمة
        records_to_delete = []
        for record_id, record in self.offline_records.items():
            if record.created_at < cutoff_date and record.sync_status == SyncStatus.COMPLETED.value:
                records_to_delete.append(record_id)
        
        for record_id in records_to_delete:
            del self.offline_records[record_id]
            cleaned_records += 1
        
        return {
            'cleaned_records': cleaned_records
        }
    
    def _merge_conflicted_data(self, local_data: Dict, server_data: Dict) -> Dict:
        """دمج البيانات المتعارضة"""
        
        # استراتيجية دمج بسيطة: أخذ القيم الأحدث
        merged_data = local_data.copy()
        
        for key, value in server_data.items():
            if key not in merged_data or value != merged_data[key]:
                # في حالة التعارض، نأخذ القيمة من الخادم
                merged_data[key] = value
        
        return merged_data
    
    def _process_sync_operation(self, operation: SyncOperation):
        """معالجة عملية مزامنة"""
        
        try:
            # محاكاة معالجة العملية
            import random
            success = random.choice([True, True, False])  # 66% نجاح
            
            if success:
                # تحديث حالة السجل
                if operation.record_id in self.offline_records:
                    record = self.offline_records[operation.record_id]
                    record.sync_status = SyncStatus.COMPLETED.value
            else:
                operation.retry_count += 1
                operation.last_error = "فشل في معالجة العملية"
                
                # إعادة إضافة للطابور إذا لم تتجاوز الحد الأقصى
                if operation.retry_count < self.system_settings['max_retry_attempts']:
                    priority_value = self._get_priority_value(operation.sync_priority)
                    self.sync_queue.put((priority_value, operation.operation_id))
                    
        except Exception as e:
            operation.retry_count += 1
            operation.last_error = str(e)
    
    def _generate_sync_recommendations(self, sync_results: Dict) -> List[str]:
        """إنتاج توصيات المزامنة"""
        
        recommendations = []
        
        if sync_results['failed_operations'] > 0:
            recommendations.append('مراجعة العمليات الفاشلة وإعادة المحاولة')
        
        if sync_results['conflicts_detected'] > 0:
            recommendations.append('حل التعارضات المتبقية يدوياً')
        
        if sync_results['uploaded_records'] == 0 and sync_results['downloaded_records'] == 0:
            recommendations.append('التحقق من اتصال الإنترنت')
        
        recommendations.append('تفعيل المزامنة التلقائية لتجنب تراكم البيانات')
        
        return recommendations
    
    def _generate_offline_recommendations(self) -> List[str]:
        """إنتاج توصيات الوضع غير المتصل"""
        
        recommendations = []
        
        # فحص حجم البيانات
        total_size_mb = sum(record.size_bytes for record in self.offline_records.values()) / (1024 * 1024)
        if total_size_mb > self.system_settings['cache_size_limit_mb'] * 0.8:
            recommendations.append('تنظيف البيانات المحلية لتوفير مساحة')
        
        # فحص العمليات المعلقة
        pending_operations = len([op for op in self.sync_operations.values() if op.retry_count < self.system_settings['max_retry_attempts']])
        if pending_operations > 50:
            recommendations.append('مزامنة البيانات في أقرب وقت ممكن')
        
        # فحص التعارضات
        unresolved_conflicts = len([c for c in self.conflict_resolutions.values() if not c.resolved_at])
        if unresolved_conflicts > 0:
            recommendations.append('حل التعارضات المعلقة')
        
        recommendations.append('تأكد من شحن البطارية قبل المزامنة الطويلة')
        
        return recommendations

