"""
خدمة الأمان المتقدمة وحماية البيانات الطبية
"""

import os
import json
import uuid
import hashlib
import hmac
import secrets
import base64
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from flask import current_app, request
from dataclasses import dataclass
from enum import Enum
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pyotp
import qrcode
from io import BytesIO

class SecurityLevel(Enum):
    LOW = "منخفض"
    MEDIUM = "متوسط"
    HIGH = "عالي"
    CRITICAL = "حرج"

class ThreatType(Enum):
    BRUTE_FORCE = "هجوم القوة الغاشمة"
    SQL_INJECTION = "حقن SQL"
    XSS = "هجوم XSS"
    CSRF = "هجوم CSRF"
    DATA_BREACH = "تسريب البيانات"
    UNAUTHORIZED_ACCESS = "وصول غير مصرح"
    MALWARE = "برمجيات خبيثة"
    PHISHING = "تصيد"
    DDoS = "هجوم حجب الخدمة"

class AuditAction(Enum):
    LOGIN = "تسجيل دخول"
    LOGOUT = "تسجيل خروج"
    DATA_ACCESS = "الوصول للبيانات"
    DATA_MODIFY = "تعديل البيانات"
    DATA_DELETE = "حذف البيانات"
    PERMISSION_CHANGE = "تغيير الصلاحيات"
    SECURITY_ALERT = "تنبيه أمني"
    BACKUP_CREATE = "إنشاء نسخة احتياطية"
    BACKUP_RESTORE = "استعادة نسخة احتياطية"

@dataclass
class SecurityEvent:
    event_id: str
    user_id: str
    event_type: str
    severity: str
    description: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    resolved: bool
    resolution_notes: Optional[str]

@dataclass
class AuditLog:
    log_id: str
    user_id: str
    action: str
    resource: str
    details: Dict
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool

@dataclass
class EncryptionKey:
    key_id: str
    key_type: str
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

class AdvancedSecurityService:
    def __init__(self):
        """تهيئة خدمة الأمان المتقدمة"""
        
        # إعدادات الأمان
        self.security_settings = {
            'password_min_length': 8,
            'password_require_uppercase': True,
            'password_require_lowercase': True,
            'password_require_numbers': True,
            'password_require_symbols': True,
            'password_history_count': 5,
            'password_expiry_days': 90,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30,
            'session_timeout_minutes': 60,
            'require_2fa': True,
            'enable_biometric_auth': True,
            'enable_device_fingerprinting': True,
            'enable_geo_blocking': True,
            'enable_rate_limiting': True,
            'enable_audit_logging': True,
            'data_retention_days': 2555,  # 7 سنوات للبيانات الطبية
            'backup_encryption': True,
            'backup_frequency_hours': 6,
            'backup_retention_days': 365
        }
        
        # مستويات الأمان للبيانات المختلفة
        self.data_classification = {
            'public': SecurityLevel.LOW.value,
            'internal': SecurityLevel.MEDIUM.value,
            'confidential': SecurityLevel.HIGH.value,
            'medical_records': SecurityLevel.CRITICAL.value,
            'payment_info': SecurityLevel.CRITICAL.value,
            'personal_id': SecurityLevel.CRITICAL.value,
            'biometric_data': SecurityLevel.CRITICAL.value
        }
        
        # قواعد الكشف عن التهديدات
        self.threat_detection_rules = {
            'brute_force': {
                'max_attempts': 5,
                'time_window_minutes': 15,
                'action': 'block_ip'
            },
            'suspicious_login': {
                'new_device': True,
                'new_location': True,
                'unusual_time': True,
                'action': 'require_verification'
            },
            'data_access_anomaly': {
                'bulk_access': True,
                'unusual_patterns': True,
                'off_hours_access': True,
                'action': 'alert_admin'
            },
            'privilege_escalation': {
                'rapid_permission_changes': True,
                'unauthorized_admin_access': True,
                'action': 'immediate_block'
            }
        }
        
        # قاعدة بيانات الأمان (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.security_events = {}
        self.audit_logs = {}
        self.encryption_keys = {}
        self.blocked_ips = {}
        self.user_sessions = {}
        self.device_fingerprints = {}
        self.failed_login_attempts = {}
        
        # تهيئة مفاتيح التشفير
        self._initialize_encryption_keys()
    
    def authenticate_user(self, credentials: Dict) -> Dict:
        """
        مصادقة المستخدم مع الأمان المتقدم
        
        Args:
            credentials: بيانات المصادقة
            
        Returns:
            Dict: نتيجة المصادقة
        """
        try:
            username = credentials.get('username')
            password = credentials.get('password')
            ip_address = credentials.get('ip_address', request.remote_addr if request else '127.0.0.1')
            user_agent = credentials.get('user_agent', request.headers.get('User-Agent') if request else '')
            device_fingerprint = credentials.get('device_fingerprint')
            
            # فحص IP المحظور
            if self._is_ip_blocked(ip_address):
                self._log_security_event(
                    None, ThreatType.UNAUTHORIZED_ACCESS.value, SecurityLevel.HIGH.value,
                    f"محاولة دخول من IP محظور: {ip_address}", ip_address, user_agent
                )
                return {
                    'success': False,
                    'error': 'عذراً، تم حظر عنوان IP الخاص بك',
                    'blocked': True
                }
            
            # فحص محاولات تسجيل الدخول الفاشلة
            if self._check_brute_force_attempt(username, ip_address):
                self._block_ip(ip_address, 'محاولات تسجيل دخول متكررة')
                return {
                    'success': False,
                    'error': 'تم تجاوز عدد المحاولات المسموح',
                    'blocked': True
                }
            
            # التحقق من بيانات المستخدم
            user_data = self._verify_user_credentials(username, password)
            if not user_data:
                self._record_failed_login(username, ip_address)
                return {
                    'success': False,
                    'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'
                }
            
            user_id = user_data['user_id']
            
            # فحص حالة الحساب
            account_status = self._check_account_status(user_id)
            if not account_status['active']:
                return {
                    'success': False,
                    'error': account_status['reason']
                }
            
            # فحص الجهاز والموقع
            device_check = self._check_device_and_location(user_id, device_fingerprint, ip_address)
            
            # إنشاء الجلسة
            session_data = self._create_secure_session(user_id, ip_address, user_agent, device_fingerprint)
            
            # تسجيل الدخول الناجح
            self._log_audit_event(
                user_id, AuditAction.LOGIN.value, 'user_session',
                {'session_id': session_data['session_id']}, ip_address, user_agent, True
            )
            
            # إعادة تعيين محاولات تسجيل الدخول الفاشلة
            self._reset_failed_login_attempts(username, ip_address)
            
            response = {
                'success': True,
                'user_id': user_id,
                'session_token': session_data['session_token'],
                'session_id': session_data['session_id'],
                'expires_at': session_data['expires_at'],
                'requires_2fa': self.security_settings['require_2fa'],
                'device_trusted': device_check['trusted'],
                'security_level': user_data.get('security_level', SecurityLevel.MEDIUM.value)
            }
            
            # إضافة تحدي 2FA إذا كان مطلوباً
            if self.security_settings['require_2fa'] and not device_check['trusted']:
                response['requires_2fa'] = True
                response['2fa_methods'] = self._get_available_2fa_methods(user_id)
            
            return response
            
        except Exception as e:
            current_app.logger.error(f"خطأ في مصادقة المستخدم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في المصادقة'
            }
    
    def verify_2fa(self, verification_data: Dict) -> Dict:
        """
        التحقق من المصادقة الثنائية
        
        Args:
            verification_data: بيانات التحقق
            
        Returns:
            Dict: نتيجة التحقق
        """
        try:
            user_id = verification_data.get('user_id')
            method = verification_data.get('method')
            code = verification_data.get('code')
            session_token = verification_data.get('session_token')
            
            # التحقق من صحة الجلسة
            session_valid = self._verify_session_token(session_token, user_id)
            if not session_valid:
                return {
                    'success': False,
                    'error': 'جلسة غير صالحة'
                }
            
            # التحقق من الرمز حسب الطريقة
            verification_result = False
            
            if method == 'totp':
                verification_result = self._verify_totp_code(user_id, code)
            elif method == 'sms':
                verification_result = self._verify_sms_code(user_id, code)
            elif method == 'email':
                verification_result = self._verify_email_code(user_id, code)
            elif method == 'biometric':
                verification_result = self._verify_biometric_data(user_id, verification_data.get('biometric_data'))
            
            if verification_result:
                # تحديث الجلسة لتصبح مصادق عليها بالكامل
                self._update_session_2fa_status(session_token, True)
                
                # تسجيل التحقق الناجح
                self._log_audit_event(
                    user_id, '2FA_VERIFICATION', 'authentication',
                    {'method': method}, verification_data.get('ip_address', ''), '', True
                )
                
                return {
                    'success': True,
                    'message': 'تم التحقق بنجاح',
                    'fully_authenticated': True
                }
            else:
                # تسجيل محاولة التحقق الفاشلة
                self._log_security_event(
                    user_id, 'FAILED_2FA_VERIFICATION', SecurityLevel.MEDIUM.value,
                    f"فشل في التحقق الثنائي بطريقة {method}",
                    verification_data.get('ip_address', ''), ''
                )
                
                return {
                    'success': False,
                    'error': 'رمز التحقق غير صحيح'
                }
                
        except Exception as e:
            current_app.logger.error(f"خطأ في التحقق الثنائي: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في التحقق'
            }
    
    def encrypt_sensitive_data(self, data: Any, classification: str = 'confidential') -> Dict:
        """
        تشفير البيانات الحساسة
        
        Args:
            data: البيانات المراد تشفيرها
            classification: تصنيف البيانات
            
        Returns:
            Dict: البيانات المشفرة
        """
        try:
            # تحديد مستوى التشفير حسب التصنيف
            security_level = self.data_classification.get(classification, SecurityLevel.MEDIUM.value)
            
            # تحويل البيانات إلى JSON إذا لم تكن نص
            if not isinstance(data, str):
                data_string = json.dumps(data, ensure_ascii=False)
            else:
                data_string = data
            
            # اختيار مفتاح التشفير المناسب
            encryption_key = self._get_encryption_key(security_level)
            
            # تشفير البيانات
            fernet = Fernet(encryption_key['key_data'])
            encrypted_data = fernet.encrypt(data_string.encode('utf-8'))
            
            # إنشاء معرف فريد للبيانات المشفرة
            data_id = str(uuid.uuid4())
            
            # حفظ معلومات التشفير
            encryption_info = {
                'data_id': data_id,
                'key_id': encryption_key['key_id'],
                'classification': classification,
                'encrypted_at': datetime.now().isoformat(),
                'algorithm': 'Fernet',
                'checksum': hashlib.sha256(encrypted_data).hexdigest()
            }
            
            return {
                'success': True,
                'data_id': data_id,
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
                'encryption_info': encryption_info
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تشفير البيانات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في التشفير'
            }
    
    def decrypt_sensitive_data(self, encrypted_data: str, encryption_info: Dict) -> Dict:
        """
        فك تشفير البيانات الحساسة
        
        Args:
            encrypted_data: البيانات المشفرة
            encryption_info: معلومات التشفير
            
        Returns:
            Dict: البيانات المفكوكة
        """
        try:
            # التحقق من صحة معلومات التشفير
            key_id = encryption_info.get('key_id')
            if key_id not in self.encryption_keys:
                return {
                    'success': False,
                    'error': 'مفتاح التشفير غير موجود'
                }
            
            # الحصول على مفتاح التشفير
            encryption_key = self.encryption_keys[key_id]
            
            # فك تشفير البيانات
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # التحقق من Checksum
            current_checksum = hashlib.sha256(encrypted_bytes).hexdigest()
            if current_checksum != encryption_info.get('checksum'):
                return {
                    'success': False,
                    'error': 'البيانات تالفة أو تم التلاعب بها'
                }
            
            # فك التشفير
            fernet = Fernet(encryption_key['key_data'])
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            decrypted_string = decrypted_bytes.decode('utf-8')
            
            # محاولة تحويل JSON إذا كان ممكناً
            try:
                decrypted_data = json.loads(decrypted_string)
            except json.JSONDecodeError:
                decrypted_data = decrypted_string
            
            return {
                'success': True,
                'data': decrypted_data,
                'decrypted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في فك التشفير: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في فك التشفير'
            }
    
    def detect_security_threats(self, activity_data: Dict) -> Dict:
        """
        كشف التهديدات الأمنية
        
        Args:
            activity_data: بيانات النشاط
            
        Returns:
            Dict: نتائج كشف التهديدات
        """
        try:
            user_id = activity_data.get('user_id')
            action = activity_data.get('action')
            ip_address = activity_data.get('ip_address')
            user_agent = activity_data.get('user_agent')
            timestamp = datetime.now()
            
            detected_threats = []
            
            # كشف هجمات القوة الغاشمة
            if self._detect_brute_force(user_id, ip_address, timestamp):
                detected_threats.append({
                    'type': ThreatType.BRUTE_FORCE.value,
                    'severity': SecurityLevel.HIGH.value,
                    'description': 'محاولات تسجيل دخول متكررة مشبوهة'
                })
            
            # كشف الوصول المشبوه
            if self._detect_suspicious_access(user_id, ip_address, user_agent, timestamp):
                detected_threats.append({
                    'type': ThreatType.UNAUTHORIZED_ACCESS.value,
                    'severity': SecurityLevel.MEDIUM.value,
                    'description': 'نشاط مشبوه في الحساب'
                })
            
            # كشف أنماط الوصول غير الطبيعية
            if self._detect_anomalous_patterns(user_id, action, timestamp):
                detected_threats.append({
                    'type': 'ANOMALOUS_BEHAVIOR',
                    'severity': SecurityLevel.MEDIUM.value,
                    'description': 'نمط استخدام غير طبيعي'
                })
            
            # كشف محاولات رفع الصلاحيات
            if self._detect_privilege_escalation(user_id, action):
                detected_threats.append({
                    'type': 'PRIVILEGE_ESCALATION',
                    'severity': SecurityLevel.CRITICAL.value,
                    'description': 'محاولة رفع صلاحيات غير مصرح بها'
                })
            
            # تسجيل التهديدات المكتشفة
            for threat in detected_threats:
                self._log_security_event(
                    user_id, threat['type'], threat['severity'],
                    threat['description'], ip_address, user_agent
                )
            
            # اتخاذ إجراءات تلقائية إذا لزم الأمر
            if detected_threats:
                self._take_automated_security_actions(user_id, detected_threats, ip_address)
            
            return {
                'success': True,
                'threats_detected': len(detected_threats),
                'threats': detected_threats,
                'timestamp': timestamp.isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في كشف التهديدات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في كشف التهديدات'
            }
    
    def generate_security_report(self, period_days: int = 30) -> Dict:
        """
        إنشاء تقرير أمني
        
        Args:
            period_days: فترة التقرير بالأيام
            
        Returns:
            Dict: التقرير الأمني
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            
            # جمع الأحداث الأمنية من الفترة المحددة
            period_events = []
            for user_id, events in self.security_events.items():
                period_events.extend([
                    event for event in events 
                    if event.timestamp >= cutoff_date
                ])
            
            # تحليل الأحداث
            total_events = len(period_events)
            critical_events = len([e for e in period_events if e.severity == SecurityLevel.CRITICAL.value])
            high_events = len([e for e in period_events if e.severity == SecurityLevel.HIGH.value])
            resolved_events = len([e for e in period_events if e.resolved])
            
            # أكثر أنواع التهديدات شيوعاً
            threat_counts = {}
            for event in period_events:
                threat_type = event.event_type
                if threat_type not in threat_counts:
                    threat_counts[threat_type] = 0
                threat_counts[threat_type] += 1
            
            most_common_threats = sorted(
                threat_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            # أكثر عناوين IP المشبوهة
            ip_counts = {}
            for event in period_events:
                ip = event.ip_address
                if ip not in ip_counts:
                    ip_counts[ip] = 0
                ip_counts[ip] += 1
            
            suspicious_ips = sorted(
                ip_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            # إحصائيات تسجيل الدخول
            login_logs = []
            for user_id, logs in self.audit_logs.items():
                login_logs.extend([
                    log for log in logs 
                    if log.action == AuditAction.LOGIN.value and log.timestamp >= cutoff_date
                ])
            
            successful_logins = len([log for log in login_logs if log.success])
            failed_logins = len([log for log in login_logs if not log.success])
            
            # توصيات الأمان
            recommendations = self._generate_security_recommendations(period_events)
            
            return {
                'success': True,
                'report_period_days': period_days,
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_security_events': total_events,
                    'critical_events': critical_events,
                    'high_severity_events': high_events,
                    'resolved_events': resolved_events,
                    'resolution_rate': (resolved_events / total_events * 100) if total_events > 0 else 0,
                    'successful_logins': successful_logins,
                    'failed_logins': failed_logins,
                    'login_success_rate': (successful_logins / (successful_logins + failed_logins) * 100) if (successful_logins + failed_logins) > 0 else 0
                },
                'threat_analysis': {
                    'most_common_threats': most_common_threats,
                    'suspicious_ips': suspicious_ips,
                    'blocked_ips_count': len(self.blocked_ips)
                },
                'recommendations': recommendations,
                'security_metrics': {
                    'average_events_per_day': total_events / period_days,
                    'critical_events_percentage': (critical_events / total_events * 100) if total_events > 0 else 0,
                    'threat_diversity': len(threat_counts)
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء التقرير الأمني: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء التقرير'
            }
    
    def setup_2fa_totp(self, user_id: str) -> Dict:
        """
        إعداد المصادقة الثنائية TOTP
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: معلومات إعداد TOTP
        """
        try:
            # إنشاء مفتاح سري جديد
            secret_key = pyotp.random_base32()
            
            # إنشاء TOTP
            totp = pyotp.TOTP(secret_key)
            
            # إنشاء QR Code
            provisioning_uri = totp.provisioning_uri(
                name=f"user_{user_id}",
                issuer_name="صحتك في أمان"
            )
            
            # إنشاء QR Code كصورة
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # تحويل الصورة إلى base64
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # حفظ المفتاح السري (مشفر)
            encrypted_secret = self.encrypt_sensitive_data(secret_key, 'confidential')
            
            # في التطبيق الحقيقي، سيتم حفظ هذا في قاعدة البيانات
            # self._save_user_2fa_secret(user_id, encrypted_secret)
            
            return {
                'success': True,
                'secret_key': secret_key,  # في الإنتاج، لا يتم إرجاع هذا
                'qr_code': qr_code_base64,
                'provisioning_uri': provisioning_uri,
                'backup_codes': self._generate_backup_codes(user_id)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إعداد TOTP: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إعداد المصادقة الثنائية'
            }
    
    def validate_password_strength(self, password: str) -> Dict:
        """
        التحقق من قوة كلمة المرور
        
        Args:
            password: كلمة المرور
            
        Returns:
            Dict: نتيجة التحقق
        """
        try:
            issues = []
            score = 0
            
            # فحص الطول
            if len(password) < self.security_settings['password_min_length']:
                issues.append(f"كلمة المرور يجب أن تكون {self.security_settings['password_min_length']} أحرف على الأقل")
            else:
                score += 1
            
            # فحص الأحرف الكبيرة
            if self.security_settings['password_require_uppercase'] and not any(c.isupper() for c in password):
                issues.append("كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل")
            else:
                score += 1
            
            # فحص الأحرف الصغيرة
            if self.security_settings['password_require_lowercase'] and not any(c.islower() for c in password):
                issues.append("كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل")
            else:
                score += 1
            
            # فحص الأرقام
            if self.security_settings['password_require_numbers'] and not any(c.isdigit() for c in password):
                issues.append("كلمة المرور يجب أن تحتوي على رقم واحد على الأقل")
            else:
                score += 1
            
            # فحص الرموز
            if self.security_settings['password_require_symbols']:
                symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                if not any(c in symbols for c in password):
                    issues.append("كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل")
                else:
                    score += 1
            
            # حساب قوة كلمة المرور
            strength_levels = {
                0: "ضعيف جداً",
                1: "ضعيف",
                2: "متوسط",
                3: "جيد",
                4: "قوي",
                5: "قوي جداً"
            }
            
            strength = strength_levels.get(score, "ضعيف جداً")
            is_valid = len(issues) == 0
            
            return {
                'success': True,
                'is_valid': is_valid,
                'strength': strength,
                'score': score,
                'max_score': 5,
                'issues': issues
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في التحقق من قوة كلمة المرور: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في التحقق'
            }
    
    # الدوال المساعدة
    def _initialize_encryption_keys(self):
        """تهيئة مفاتيح التشفير"""
        # إنشاء مفاتيح تشفير لمستويات الأمان المختلفة
        for level in [SecurityLevel.MEDIUM.value, SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
            key_id = f"key_{level}_{uuid.uuid4()}"
            key_data = Fernet.generate_key()
            
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_type='Fernet',
                key_data=key_data,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=365),
                is_active=True
            )
            
            self.encryption_keys[key_id] = encryption_key
    
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """فحص إذا كان IP محظور"""
        if ip_address in self.blocked_ips:
            block_info = self.blocked_ips[ip_address]
            # فحص إذا كان الحظر ما زال ساري المفعول
            if datetime.now() < block_info['expires_at']:
                return True
            else:
                # إزالة الحظر المنتهي الصلاحية
                del self.blocked_ips[ip_address]
        return False
    
    def _check_brute_force_attempt(self, username: str, ip_address: str) -> bool:
        """فحص محاولات القوة الغاشمة"""
        key = f"{username}_{ip_address}"
        if key in self.failed_login_attempts:
            attempts = self.failed_login_attempts[key]
            recent_attempts = [
                attempt for attempt in attempts 
                if attempt > datetime.now() - timedelta(minutes=15)
            ]
            return len(recent_attempts) >= self.security_settings['max_login_attempts']
        return False
    
    def _verify_user_credentials(self, username: str, password: str) -> Optional[Dict]:
        """التحقق من بيانات المستخدم"""
        # في التطبيق الحقيقي، سيتم البحث في قاعدة البيانات
        # هنا نضع بيانات تجريبية
        test_users = {
            'Ahmedbahnese@yahoo.com': {
                'user_id': 'owner_ahmed_bahnasy',
                'password_hash': hashlib.sha256('Bahnasy123'.encode()).hexdigest(),
                'security_level': SecurityLevel.CRITICAL.value,
                'role': 'owner'
            },
            'admin@sahty.com': {
                'user_id': 'admin_001',
                'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
                'security_level': SecurityLevel.HIGH.value,
                'role': 'admin'
            }
        }
        
        if username in test_users:
            user = test_users[username]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == user['password_hash']:
                return user
        
        return None
    
    def _check_account_status(self, user_id: str) -> Dict:
        """فحص حالة الحساب"""
        # في التطبيق الحقيقي، سيتم فحص قاعدة البيانات
        return {
            'active': True,
            'reason': None
        }
    
    def _check_device_and_location(self, user_id: str, device_fingerprint: str, ip_address: str) -> Dict:
        """فحص الجهاز والموقع"""
        # في التطبيق الحقيقي، سيتم فحص الأجهزة والمواقع المعروفة
        return {
            'trusted': False,  # افتراضياً غير موثوق
            'new_device': True,
            'new_location': True
        }
    
    def _create_secure_session(self, user_id: str, ip_address: str, user_agent: str, device_fingerprint: str) -> Dict:
        """إنشاء جلسة آمنة"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=self.security_settings['session_timeout_minutes'])
        
        # إنشاء JWT token
        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'ip_address': ip_address,
            'device_fingerprint': device_fingerprint,
            'exp': expires_at,
            'iat': datetime.now()
        }
        
        # في التطبيق الحقيقي، سيتم استخدام مفتاح سري من المتغيرات البيئية
        secret_key = 'your-secret-key-here'
        session_token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        # حفظ الجلسة
        self.user_sessions[session_id] = {
            'user_id': user_id,
            'session_token': session_token,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'device_fingerprint': device_fingerprint,
            'created_at': datetime.now(),
            'expires_at': expires_at,
            'is_2fa_verified': False,
            'last_activity': datetime.now()
        }
        
        return {
            'session_id': session_id,
            'session_token': session_token,
            'expires_at': expires_at.isoformat()
        }
    
    def _get_available_2fa_methods(self, user_id: str) -> List[str]:
        """الحصول على طرق المصادقة الثنائية المتاحة"""
        # في التطبيق الحقيقي، سيتم فحص إعدادات المستخدم
        return ['totp', 'sms', 'email']
    
    def _verify_session_token(self, session_token: str, user_id: str) -> bool:
        """التحقق من صحة رمز الجلسة"""
        try:
            # في التطبيق الحقيقي، سيتم استخدام مفتاح سري من المتغيرات البيئية
            secret_key = 'your-secret-key-here'
            payload = jwt.decode(session_token, secret_key, algorithms=['HS256'])
            
            return payload.get('user_id') == user_id
        except jwt.InvalidTokenError:
            return False
    
    def _verify_totp_code(self, user_id: str, code: str) -> bool:
        """التحقق من رمز TOTP"""
        # في التطبيق الحقيقي، سيتم الحصول على المفتاح السري من قاعدة البيانات
        # هنا نضع رمز تجريبي
        secret_key = 'JBSWY3DPEHPK3PXP'  # مفتاح تجريبي
        totp = pyotp.TOTP(secret_key)
        return totp.verify(code, valid_window=1)
    
    def _verify_sms_code(self, user_id: str, code: str) -> bool:
        """التحقق من رمز SMS"""
        # في التطبيق الحقيقي، سيتم فحص الرمز المرسل
        return code == '123456'  # رمز تجريبي
    
    def _verify_email_code(self, user_id: str, code: str) -> bool:
        """التحقق من رمز البريد الإلكتروني"""
        # في التطبيق الحقيقي، سيتم فحص الرمز المرسل
        return code == '654321'  # رمز تجريبي
    
    def _verify_biometric_data(self, user_id: str, biometric_data: Dict) -> bool:
        """التحقق من البيانات البيومترية"""
        # في التطبيق الحقيقي، سيتم مقارنة البيانات البيومترية
        return biometric_data.get('verified', False)
    
    def _update_session_2fa_status(self, session_token: str, verified: bool):
        """تحديث حالة التحقق الثنائي للجلسة"""
        for session_id, session_data in self.user_sessions.items():
            if session_data['session_token'] == session_token:
                session_data['is_2fa_verified'] = verified
                break
    
    def _get_encryption_key(self, security_level: str) -> Dict:
        """الحصول على مفتاح التشفير المناسب"""
        for key_id, key_data in self.encryption_keys.items():
            if security_level in key_id and key_data.is_active:
                return {
                    'key_id': key_id,
                    'key_data': key_data.key_data
                }
        
        # إنشاء مفتاح جديد إذا لم يوجد
        key_id = f"key_{security_level}_{uuid.uuid4()}"
        key_data = Fernet.generate_key()
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_type='Fernet',
            key_data=key_data,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=365),
            is_active=True
        )
        
        self.encryption_keys[key_id] = encryption_key
        
        return {
            'key_id': key_id,
            'key_data': key_data
        }
    
    def _log_security_event(self, user_id: str, event_type: str, severity: str, 
                          description: str, ip_address: str, user_agent: str):
        """تسجيل حدث أمني"""
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id or 'anonymous',
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(),
            resolved=False,
            resolution_notes=None
        )
        
        if user_id not in self.security_events:
            self.security_events[user_id or 'anonymous'] = []
        
        self.security_events[user_id or 'anonymous'].append(event)
    
    def _log_audit_event(self, user_id: str, action: str, resource: str, 
                        details: Dict, ip_address: str, user_agent: str, success: bool):
        """تسجيل حدث مراجعة"""
        log = AuditLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(),
            success=success
        )
        
        if user_id not in self.audit_logs:
            self.audit_logs[user_id] = []
        
        self.audit_logs[user_id].append(log)
    
    def _record_failed_login(self, username: str, ip_address: str):
        """تسجيل محاولة تسجيل دخول فاشلة"""
        key = f"{username}_{ip_address}"
        if key not in self.failed_login_attempts:
            self.failed_login_attempts[key] = []
        
        self.failed_login_attempts[key].append(datetime.now())
    
    def _reset_failed_login_attempts(self, username: str, ip_address: str):
        """إعادة تعيين محاولات تسجيل الدخول الفاشلة"""
        key = f"{username}_{ip_address}"
        if key in self.failed_login_attempts:
            del self.failed_login_attempts[key]
    
    def _block_ip(self, ip_address: str, reason: str):
        """حظر عنوان IP"""
        self.blocked_ips[ip_address] = {
            'reason': reason,
            'blocked_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=self.security_settings['lockout_duration_minutes'])
        }
    
    def _detect_brute_force(self, user_id: str, ip_address: str, timestamp: datetime) -> bool:
        """كشف هجمات القوة الغاشمة"""
        # فحص محاولات تسجيل الدخول المتكررة
        return self._check_brute_force_attempt(user_id or 'anonymous', ip_address)
    
    def _detect_suspicious_access(self, user_id: str, ip_address: str, user_agent: str, timestamp: datetime) -> bool:
        """كشف الوصول المشبوه"""
        # فحص الوصول من أجهزة أو مواقع جديدة في أوقات غير عادية
        hour = timestamp.hour
        
        # الوصول في ساعات غير عادية (منتصف الليل إلى الفجر)
        if 0 <= hour <= 5:
            return True
        
        # فحص User Agent مشبوه
        suspicious_agents = ['bot', 'crawler', 'spider', 'scraper']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            return True
        
        return False
    
    def _detect_anomalous_patterns(self, user_id: str, action: str, timestamp: datetime) -> bool:
        """كشف الأنماط غير الطبيعية"""
        # فحص الوصول المكثف للبيانات
        if action in ['DATA_ACCESS', 'DATA_EXPORT']:
            # في التطبيق الحقيقي، سيتم فحص تاريخ الوصول
            return False
        
        return False
    
    def _detect_privilege_escalation(self, user_id: str, action: str) -> bool:
        """كشف محاولات رفع الصلاحيات"""
        # فحص محاولات تغيير الصلاحيات أو الوصول لموارد محظورة
        if action in ['PERMISSION_CHANGE', 'ADMIN_ACCESS']:
            return True
        
        return False
    
    def _take_automated_security_actions(self, user_id: str, threats: List[Dict], ip_address: str):
        """اتخاذ إجراءات أمنية تلقائية"""
        for threat in threats:
            if threat['severity'] == SecurityLevel.CRITICAL.value:
                # حظر فوري للمستخدم أو IP
                self._block_ip(ip_address, f"تهديد حرج: {threat['description']}")
            elif threat['severity'] == SecurityLevel.HIGH.value:
                # تنبيه المدراء
                self._alert_administrators(threat, user_id, ip_address)
    
    def _alert_administrators(self, threat: Dict, user_id: str, ip_address: str):
        """تنبيه المدراء"""
        # في التطبيق الحقيقي، سيتم إرسال تنبيهات فورية
        pass
    
    def _generate_security_recommendations(self, events: List[SecurityEvent]) -> List[str]:
        """إنشاء توصيات أمنية"""
        recommendations = []
        
        # تحليل الأحداث وإنشاء توصيات
        critical_events = [e for e in events if e.severity == SecurityLevel.CRITICAL.value]
        if len(critical_events) > 5:
            recommendations.append("يُنصح بتعزيز إجراءات الأمان بسبب كثرة الأحداث الحرجة")
        
        brute_force_events = [e for e in events if e.event_type == ThreatType.BRUTE_FORCE.value]
        if len(brute_force_events) > 3:
            recommendations.append("يُنصح بتفعيل CAPTCHA وتقليل عدد محاولات تسجيل الدخول")
        
        if len(self.blocked_ips) > 10:
            recommendations.append("يُنصح بمراجعة قائمة عناوين IP المحظورة وتحديثها")
        
        return recommendations
    
    def _generate_backup_codes(self, user_id: str) -> List[str]:
        """إنشاء رموز احتياطية للمصادقة الثنائية"""
        backup_codes = []
        for _ in range(10):
            code = secrets.token_hex(4).upper()
            backup_codes.append(code)
        
        # في التطبيق الحقيقي، سيتم حفظ هذه الرموز مشفرة في قاعدة البيانات
        return backup_codes

