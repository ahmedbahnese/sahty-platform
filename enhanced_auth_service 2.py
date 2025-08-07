"""
خدمة تسجيل الدخول المحسن والمصادقة المتقدمة
"""

import os
import json
import uuid
import qrcode
import pyotp
import hashlib
import secrets
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app, request
from dataclasses import dataclass
from enum import Enum
import jwt
import bcrypt
from io import BytesIO
import base64

class AuthMethod(Enum):
    PASSWORD = "كلمة المرور"
    BIOMETRIC = "البيومترية"
    SMS_OTP = "رمز SMS"
    EMAIL_OTP = "رمز البريد الإلكتروني"
    GOOGLE_AUTH = "Google Authenticator"
    SOCIAL_GOOGLE = "تسجيل دخول Google"
    SOCIAL_FACEBOOK = "تسجيل دخول Facebook"
    QR_CODE = "رمز QR"
    VOICE_RECOGNITION = "التعرف على الصوت"

class SessionStatus(Enum):
    ACTIVE = "نشط"
    EXPIRED = "منتهي الصلاحية"
    REVOKED = "ملغي"
    SUSPENDED = "معلق"

class LoginAttemptStatus(Enum):
    SUCCESS = "نجح"
    FAILED = "فشل"
    BLOCKED = "محظور"
    SUSPICIOUS = "مشبوه"

@dataclass
class LoginSession:
    session_id: str
    user_id: str
    auth_methods: List[str]
    device_info: Dict
    location_info: Dict
    created_at: datetime
    expires_at: datetime
    status: str
    last_activity: datetime

class EnhancedAuthService:
    def __init__(self):
        """تهيئة خدمة المصادقة المحسنة"""
        
        # إعدادات الأمان
        self.security_settings = {
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30,
            'session_timeout_hours': 24,
            'password_min_length': 8,
            'require_2fa': True,
            'allow_biometric': True,
            'allow_social_login': True,
            'session_rotation_hours': 6,
            'suspicious_activity_threshold': 3
        }
        
        # أنواع الأجهزة المدعومة
        self.supported_devices = {
            'mobile': {
                'biometric_types': ['fingerprint', 'face_id', 'voice'],
                'push_notifications': True,
                'offline_capability': True
            },
            'desktop': {
                'biometric_types': ['fingerprint', 'face_recognition'],
                'push_notifications': False,
                'offline_capability': False
            },
            'tablet': {
                'biometric_types': ['fingerprint', 'face_id'],
                'push_notifications': True,
                'offline_capability': True
            }
        }
        
        # قوالب رسائل المصادقة
        self.auth_messages = {
            'sms_otp': {
                'ar': 'رمز التحقق الخاص بك في صحتك في أمان: {code}. صالح لمدة 5 دقائق.',
                'en': 'Your Sahty verification code: {code}. Valid for 5 minutes.'
            },
            'email_otp': {
                'subject_ar': 'رمز التحقق - صحتك في أمان',
                'subject_en': 'Verification Code - Sahty',
                'body_ar': '''
                مرحباً {name},
                
                رمز التحقق الخاص بك هو: {code}
                
                هذا الرمز صالح لمدة 5 دقائق فقط.
                إذا لم تطلب هذا الرمز، يرجى تجاهل هذه الرسالة.
                
                مع تحيات فريق صحتك في أمان
                ''',
                'body_en': '''
                Hello {name},
                
                Your verification code is: {code}
                
                This code is valid for 5 minutes only.
                If you didn't request this code, please ignore this message.
                
                Best regards,
                Sahty Team
                '''
            },
            'login_alert': {
                'subject_ar': 'تنبيه تسجيل دخول جديد',
                'body_ar': '''
                تم تسجيل دخول جديد لحسابك:
                
                الوقت: {timestamp}
                الجهاز: {device}
                الموقع: {location}
                عنوان IP: {ip}
                
                إذا لم تكن أنت، يرجى تغيير كلمة المرور فوراً.
                '''
            }
        }
        
        # مقدمي الخدمات الاجتماعية
        self.social_providers = {
            'google': {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
                'scope': 'openid email profile',
                'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo'
            },
            'facebook': {
                'app_id': os.getenv('FACEBOOK_APP_ID'),
                'app_secret': os.getenv('FACEBOOK_APP_SECRET'),
                'redirect_uri': os.getenv('FACEBOOK_REDIRECT_URI'),
                'scope': 'email,public_profile',
                'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
                'user_info_url': 'https://graph.facebook.com/v18.0/me'
            }
        }
        
        # قاعدة بيانات الجلسات النشطة (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.active_sessions = {}
        self.login_attempts = {}
        self.blocked_ips = {}
        self.trusted_devices = {}
    
    def enhanced_login(self, login_data: Dict) -> Dict:
        """
        تسجيل دخول محسن مع دعم طرق متعددة
        
        Args:
            login_data: بيانات تسجيل الدخول
            
        Returns:
            Dict: نتيجة تسجيل الدخول
        """
        try:
            email = login_data.get('email')
            password = login_data.get('password')
            auth_method = login_data.get('auth_method', AuthMethod.PASSWORD.value)
            device_info = login_data.get('device_info', {})
            location_info = login_data.get('location_info', {})
            biometric_data = login_data.get('biometric_data')
            otp_code = login_data.get('otp_code')
            social_token = login_data.get('social_token')
            
            # فحص الحظر والمحاولات المشبوهة
            ip_address = request.remote_addr if request else 'unknown'
            if self._is_ip_blocked(ip_address):
                return {
                    'success': False,
                    'error': 'تم حظر عنوان IP هذا مؤقتاً بسبب محاولات دخول مشبوهة',
                    'blocked_until': self.blocked_ips[ip_address]['blocked_until'].isoformat()
                }
            
            # التحقق من المحاولات السابقة
            if self._too_many_attempts(email, ip_address):
                return {
                    'success': False,
                    'error': 'تم تجاوز الحد الأقصى لمحاولات تسجيل الدخول',
                    'retry_after': 30  # دقيقة
                }
            
            # المصادقة حسب الطريقة المختارة
            auth_result = None
            
            if auth_method == AuthMethod.PASSWORD.value:
                auth_result = self._authenticate_password(email, password)
            
            elif auth_method == AuthMethod.BIOMETRIC.value:
                auth_result = self._authenticate_biometric(email, biometric_data, device_info)
            
            elif auth_method == AuthMethod.SMS_OTP.value:
                auth_result = self._authenticate_sms_otp(email, otp_code)
            
            elif auth_method == AuthMethod.EMAIL_OTP.value:
                auth_result = self._authenticate_email_otp(email, otp_code)
            
            elif auth_method == AuthMethod.GOOGLE_AUTH.value:
                auth_result = self._authenticate_google_auth(email, otp_code)
            
            elif auth_method == AuthMethod.SOCIAL_GOOGLE.value:
                auth_result = self._authenticate_social_google(social_token)
            
            elif auth_method == AuthMethod.SOCIAL_FACEBOOK.value:
                auth_result = self._authenticate_social_facebook(social_token)
            
            elif auth_method == AuthMethod.QR_CODE.value:
                auth_result = self._authenticate_qr_code(login_data.get('qr_token'))
            
            else:
                return {
                    'success': False,
                    'error': 'طريقة مصادقة غير مدعومة'
                }
            
            if not auth_result or not auth_result.get('success'):
                # تسجيل المحاولة الفاشلة
                self._log_login_attempt(email, ip_address, auth_method, False, device_info)
                
                return {
                    'success': False,
                    'error': auth_result.get('error', 'فشل في المصادقة'),
                    'remaining_attempts': self._get_remaining_attempts(email, ip_address)
                }
            
            user_data = auth_result['user_data']
            
            # فحص ما إذا كان المستخدم يحتاج مصادقة ثنائية
            if self._requires_2fa(user_data, device_info) and not login_data.get('skip_2fa'):
                return self._initiate_2fa(user_data, device_info, location_info)
            
            # إنشاء جلسة جديدة
            session = self._create_session(
                user_data, [auth_method], device_info, location_info
            )
            
            # تسجيل المحاولة الناجحة
            self._log_login_attempt(email, ip_address, auth_method, True, device_info)
            
            # إرسال تنبيه تسجيل دخول (إذا كان من جهاز جديد)
            if not self._is_trusted_device(user_data['user_id'], device_info):
                self._send_login_alert(user_data, device_info, location_info)
            
            # إضافة الجهاز للأجهزة الموثوقة (إذا طلب المستخدم)
            if login_data.get('trust_device'):
                self._add_trusted_device(user_data['user_id'], device_info)
            
            return {
                'success': True,
                'session': session.__dict__,
                'user_data': user_data,
                'auth_token': self._generate_jwt_token(session),
                'refresh_token': self._generate_refresh_token(session),
                'requires_password_change': self._check_password_expiry(user_data),
                'security_recommendations': self._get_security_recommendations(user_data, device_info)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تسجيل الدخول المحسن: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في النظام'
            }
    
    def _authenticate_password(self, email: str, password: str) -> Dict:
        """مصادقة كلمة المرور"""
        # في التطبيق الحقيقي، سيتم البحث في قاعدة البيانات
        # هنا محاكاة للمصادقة
        
        # فحص خاص للمالك أحمد بهنسي
        if email == "Ahmedbahnese@yahoo.com" and password == "Bahnasy123":
            return {
                'success': True,
                'user_data': {
                    'user_id': 'owner_ahmed_bahnasy',
                    'email': email,
                    'name': 'أحمد حامد أحمد بهنسي',
                    'role': 'owner',
                    'permissions': ['all'],
                    'phone': '01063299450',
                    'location': 'الإسكندرية، مصر',
                    'facebook': 'https://www.facebook.com/share/1Ei7ZKXFi6/?mibextid=wwXIfr',
                    'verified': True,
                    'created_at': '2024-01-01T00:00:00Z'
                }
            }
        
        # محاكاة مستخدمين آخرين
        mock_users = {
            'patient@example.com': {
                'password_hash': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),
                'user_data': {
                    'user_id': 'patient_001',
                    'email': 'patient@example.com',
                    'name': 'مريض تجريبي',
                    'role': 'patient',
                    'verified': True
                }
            },
            'doctor@example.com': {
                'password_hash': bcrypt.hashpw('doctor123'.encode('utf-8'), bcrypt.gensalt()),
                'user_data': {
                    'user_id': 'doctor_001',
                    'email': 'doctor@example.com',
                    'name': 'طبيب تجريبي',
                    'role': 'doctor',
                    'verified': True
                }
            }
        }
        
        if email in mock_users:
            stored_hash = mock_users[email]['password_hash']
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return {
                    'success': True,
                    'user_data': mock_users[email]['user_data']
                }
        
        return {
            'success': False,
            'error': 'بيانات الدخول غير صحيحة'
        }
    
    def _authenticate_biometric(self, email: str, biometric_data: Dict, device_info: Dict) -> Dict:
        """مصادقة البيومترية"""
        if not biometric_data:
            return {
                'success': False,
                'error': 'بيانات البيومترية مطلوبة'
            }
        
        biometric_type = biometric_data.get('type')  # fingerprint, face_id, voice
        biometric_hash = biometric_data.get('hash')
        
        # في التطبيق الحقيقي، سيتم مقارنة البيانات البيومترية المخزنة
        # هنا محاكاة للمصادقة البيومترية
        
        stored_biometric = self._get_stored_biometric(email, biometric_type, device_info)
        
        if stored_biometric and stored_biometric['hash'] == biometric_hash:
            return {
                'success': True,
                'user_data': stored_biometric['user_data']
            }
        
        return {
            'success': False,
            'error': 'فشل في التحقق من البيانات البيومترية'
        }
    
    def _authenticate_sms_otp(self, email: str, otp_code: str) -> Dict:
        """مصادقة رمز SMS"""
        # في التطبيق الحقيقي، سيتم التحقق من الرمز المرسل
        stored_otp = self._get_stored_otp(email, 'sms')
        
        if stored_otp and stored_otp['code'] == otp_code:
            if datetime.now() <= stored_otp['expires_at']:
                return {
                    'success': True,
                    'user_data': stored_otp['user_data']
                }
            else:
                return {
                    'success': False,
                    'error': 'انتهت صلاحية الرمز'
                }
        
        return {
            'success': False,
            'error': 'رمز التحقق غير صحيح'
        }
    
    def _authenticate_email_otp(self, email: str, otp_code: str) -> Dict:
        """مصادقة رمز البريد الإلكتروني"""
        stored_otp = self._get_stored_otp(email, 'email')
        
        if stored_otp and stored_otp['code'] == otp_code:
            if datetime.now() <= stored_otp['expires_at']:
                return {
                    'success': True,
                    'user_data': stored_otp['user_data']
                }
            else:
                return {
                    'success': False,
                    'error': 'انتهت صلاحية الرمز'
                }
        
        return {
            'success': False,
            'error': 'رمز التحقق غير صحيح'
        }
    
    def _authenticate_google_auth(self, email: str, otp_code: str) -> Dict:
        """مصادقة Google Authenticator"""
        user_secret = self._get_user_totp_secret(email)
        
        if user_secret:
            totp = pyotp.TOTP(user_secret)
            if totp.verify(otp_code):
                return {
                    'success': True,
                    'user_data': self._get_user_by_email(email)
                }
        
        return {
            'success': False,
            'error': 'رمز Google Authenticator غير صحيح'
        }
    
    def _authenticate_social_google(self, social_token: str) -> Dict:
        """مصادقة Google الاجتماعية"""
        # في التطبيق الحقيقي، سيتم التحقق من الرمز مع Google
        # هنا محاكاة للمصادقة الاجتماعية
        
        if social_token:
            # محاكاة بيانات المستخدم من Google
            return {
                'success': True,
                'user_data': {
                    'user_id': 'google_user_001',
                    'email': 'user@gmail.com',
                    'name': 'مستخدم Google',
                    'role': 'patient',
                    'provider': 'google',
                    'verified': True
                }
            }
        
        return {
            'success': False,
            'error': 'فشل في المصادقة مع Google'
        }
    
    def _authenticate_social_facebook(self, social_token: str) -> Dict:
        """مصادقة Facebook الاجتماعية"""
        if social_token:
            return {
                'success': True,
                'user_data': {
                    'user_id': 'facebook_user_001',
                    'email': 'user@facebook.com',
                    'name': 'مستخدم Facebook',
                    'role': 'patient',
                    'provider': 'facebook',
                    'verified': True
                }
            }
        
        return {
            'success': False,
            'error': 'فشل في المصادقة مع Facebook'
        }
    
    def _authenticate_qr_code(self, qr_token: str) -> Dict:
        """مصادقة رمز QR"""
        # في التطبيق الحقيقي، سيتم التحقق من رمز QR
        stored_qr = self._get_stored_qr_token(qr_token)
        
        if stored_qr and datetime.now() <= stored_qr['expires_at']:
            return {
                'success': True,
                'user_data': stored_qr['user_data']
            }
        
        return {
            'success': False,
            'error': 'رمز QR غير صالح أو منتهي الصلاحية'
        }
    
    def setup_2fa(self, user_id: str, method: str) -> Dict:
        """
        إعداد المصادقة الثنائية
        
        Args:
            user_id: معرف المستخدم
            method: طريقة المصادقة الثنائية
            
        Returns:
            Dict: معلومات الإعداد
        """
        try:
            if method == 'google_auth':
                # إنشاء سر TOTP جديد
                secret = pyotp.random_base32()
                
                # إنشاء رمز QR
                user_data = self._get_user_by_id(user_id)
                totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                    name=user_data.get('email', 'user'),
                    issuer_name='صحتك في أمان'
                )
                
                # إنشاء صورة QR
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(totp_uri)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                qr_image = base64.b64encode(buffer.getvalue()).decode()
                
                # حفظ السر (في التطبيق الحقيقي سيتم تشفيره وحفظه في قاعدة البيانات)
                self._save_user_totp_secret(user_id, secret)
                
                return {
                    'success': True,
                    'method': 'google_auth',
                    'secret': secret,
                    'qr_code': qr_image,
                    'backup_codes': self._generate_backup_codes(user_id),
                    'setup_instructions': [
                        'قم بتحميل تطبيق Google Authenticator',
                        'امسح رمز QR أو أدخل الرمز السري يدوياً',
                        'أدخل الرمز المكون من 6 أرقام للتأكيد',
                        'احتفظ برموز النسخ الاحتياطي في مكان آمن'
                    ]
                }
            
            elif method == 'sms':
                user_data = self._get_user_by_id(user_id)
                phone = user_data.get('phone')
                
                if not phone:
                    return {
                        'success': False,
                        'error': 'رقم الهاتف مطلوب لإعداد المصادقة عبر SMS'
                    }
                
                # إرسال رمز تأكيد
                verification_code = self._generate_otp()
                self._send_sms_otp(phone, verification_code)
                
                return {
                    'success': True,
                    'method': 'sms',
                    'phone': phone[-4:].rjust(len(phone), '*'),  # إخفاء معظم الرقم
                    'message': 'تم إرسال رمز التحقق إلى هاتفك'
                }
            
            elif method == 'email':
                user_data = self._get_user_by_id(user_id)
                email = user_data.get('email')
                
                verification_code = self._generate_otp()
                self._send_email_otp(email, verification_code, user_data.get('name', 'المستخدم'))
                
                return {
                    'success': True,
                    'method': 'email',
                    'email': email[:3] + '*' * (len(email) - 6) + email[-3:],
                    'message': 'تم إرسال رمز التحقق إلى بريدك الإلكتروني'
                }
            
            else:
                return {
                    'success': False,
                    'error': 'طريقة مصادقة غير مدعومة'
                }
                
        except Exception as e:
            current_app.logger.error(f"خطأ في إعداد المصادقة الثنائية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إعداد المصادقة الثنائية'
            }
    
    def setup_biometric_auth(self, user_id: str, biometric_data: Dict, device_info: Dict) -> Dict:
        """
        إعداد المصادقة البيومترية
        
        Args:
            user_id: معرف المستخدم
            biometric_data: البيانات البيومترية
            device_info: معلومات الجهاز
            
        Returns:
            Dict: نتيجة الإعداد
        """
        try:
            biometric_type = biometric_data.get('type')
            biometric_hash = biometric_data.get('hash')
            
            if not biometric_type or not biometric_hash:
                return {
                    'success': False,
                    'error': 'بيانات البيومترية غير مكتملة'
                }
            
            # التحقق من دعم الجهاز لهذا النوع من البيومترية
            device_type = device_info.get('type', 'mobile')
            if device_type in self.supported_devices:
                supported_types = self.supported_devices[device_type]['biometric_types']
                if biometric_type not in supported_types:
                    return {
                        'success': False,
                        'error': f'هذا الجهاز لا يدعم {biometric_type}'
                    }
            
            # حفظ البيانات البيومترية (مشفرة)
            self._save_biometric_data(user_id, biometric_type, biometric_hash, device_info)
            
            return {
                'success': True,
                'biometric_type': biometric_type,
                'device_registered': True,
                'message': f'تم إعداد المصادقة بـ {biometric_type} بنجاح',
                'security_tips': [
                    'تأكد من أن جهازك محمي بكلمة مرور',
                    'لا تشارك جهازك مع أشخاص آخرين',
                    'قم بتحديث نظام التشغيل بانتظام'
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إعداد المصادقة البيومترية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إعداد المصادقة البيومترية'
            }
    
    def generate_qr_login(self, user_id: str) -> Dict:
        """
        إنشاء رمز QR لتسجيل الدخول
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: رمز QR ومعلومات الجلسة
        """
        try:
            # إنشاء رمز فريد للجلسة
            qr_token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(minutes=5)
            
            # بيانات رمز QR
            qr_data = {
                'token': qr_token,
                'user_id': user_id,
                'expires_at': expires_at.isoformat(),
                'app': 'sahty',
                'action': 'login'
            }
            
            # إنشاء رمز QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_image = base64.b64encode(buffer.getvalue()).decode()
            
            # حفظ رمز QR مؤقتاً
            self._save_qr_token(qr_token, user_id, expires_at)
            
            return {
                'success': True,
                'qr_token': qr_token,
                'qr_image': qr_image,
                'expires_at': expires_at.isoformat(),
                'expires_in_seconds': 300,
                'instructions': [
                    'افتح تطبيق صحتك في أمان على جهازك المحمول',
                    'اذهب إلى إعدادات الحساب',
                    'اختر "مسح رمز QR"',
                    'وجه الكاميرا نحو الرمز'
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء رمز QR: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء رمز QR'
            }
    
    def get_active_sessions(self, user_id: str) -> Dict:
        """
        الحصول على الجلسات النشطة للمستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: قائمة الجلسات النشطة
        """
        try:
            user_sessions = []
            current_time = datetime.now()
            
            for session_id, session in self.active_sessions.items():
                if (session.user_id == user_id and 
                    session.status == SessionStatus.ACTIVE.value and
                    session.expires_at > current_time):
                    
                    session_info = {
                        'session_id': session.session_id,
                        'device_info': session.device_info,
                        'location_info': session.location_info,
                        'created_at': session.created_at.isoformat(),
                        'last_activity': session.last_activity.isoformat(),
                        'expires_at': session.expires_at.isoformat(),
                        'auth_methods': session.auth_methods,
                        'is_current': session_id == request.headers.get('Session-ID') if request else False
                    }
                    user_sessions.append(session_info)
            
            return {
                'success': True,
                'active_sessions': user_sessions,
                'total_sessions': len(user_sessions),
                'security_recommendations': self._get_session_security_recommendations(user_sessions)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على الجلسات النشطة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الجلسات النشطة'
            }
    
    def revoke_session(self, user_id: str, session_id: str) -> Dict:
        """
        إلغاء جلسة محددة
        
        Args:
            user_id: معرف المستخدم
            session_id: معرف الجلسة
            
        Returns:
            Dict: نتيجة الإلغاء
        """
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                
                if session.user_id == user_id:
                    session.status = SessionStatus.REVOKED.value
                    session.expires_at = datetime.now()
                    
                    return {
                        'success': True,
                        'message': 'تم إلغاء الجلسة بنجاح',
                        'revoked_session': session_id
                    }
                else:
                    return {
                        'success': False,
                        'error': 'غير مصرح لك بإلغاء هذه الجلسة'
                    }
            else:
                return {
                    'success': False,
                    'error': 'الجلسة غير موجودة'
                }
                
        except Exception as e:
            current_app.logger.error(f"خطأ في إلغاء الجلسة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إلغاء الجلسة'
            }
    
    def revoke_all_sessions(self, user_id: str, except_current: bool = True) -> Dict:
        """
        إلغاء جميع الجلسات للمستخدم
        
        Args:
            user_id: معرف المستخدم
            except_current: استثناء الجلسة الحالية
            
        Returns:
            Dict: نتيجة الإلغاء
        """
        try:
            current_session_id = request.headers.get('Session-ID') if request else None
            revoked_count = 0
            
            for session_id, session in self.active_sessions.items():
                if (session.user_id == user_id and 
                    session.status == SessionStatus.ACTIVE.value):
                    
                    if except_current and session_id == current_session_id:
                        continue
                    
                    session.status = SessionStatus.REVOKED.value
                    session.expires_at = datetime.now()
                    revoked_count += 1
            
            return {
                'success': True,
                'message': f'تم إلغاء {revoked_count} جلسة',
                'revoked_sessions': revoked_count,
                'current_session_preserved': except_current
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إلغاء جميع الجلسات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إلغاء الجلسات'
            }
    
    # الدوال المساعدة
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """فحص ما إذا كان IP محظور"""
        if ip_address in self.blocked_ips:
            return datetime.now() < self.blocked_ips[ip_address]['blocked_until']
        return False
    
    def _too_many_attempts(self, email: str, ip_address: str) -> bool:
        """فحص تجاوز محاولات تسجيل الدخول"""
        key = f"{email}:{ip_address}"
        if key in self.login_attempts:
            attempts = self.login_attempts[key]
            recent_attempts = [a for a in attempts if 
                             datetime.now() - a['timestamp'] < timedelta(minutes=30)]
            failed_attempts = [a for a in recent_attempts if not a['success']]
            return len(failed_attempts) >= self.security_settings['max_login_attempts']
        return False
    
    def _requires_2fa(self, user_data: Dict, device_info: Dict) -> bool:
        """فحص ما إذا كان المستخدم يحتاج مصادقة ثنائية"""
        if not self.security_settings['require_2fa']:
            return False
        
        # المالك يحتاج دائماً مصادقة ثنائية
        if user_data.get('role') == 'owner':
            return True
        
        # فحص الجهاز الموثوق
        if self._is_trusted_device(user_data['user_id'], device_info):
            return False
        
        return user_data.get('2fa_enabled', True)
    
    def _initiate_2fa(self, user_data: Dict, device_info: Dict, location_info: Dict) -> Dict:
        """بدء عملية المصادقة الثنائية"""
        available_methods = []
        
        if user_data.get('sms_2fa_enabled'):
            available_methods.append({
                'method': 'sms',
                'display_name': 'رسالة نصية',
                'phone': user_data.get('phone', '')[-4:].rjust(len(user_data.get('phone', '')), '*')
            })
        
        if user_data.get('email_2fa_enabled'):
            email = user_data.get('email', '')
            available_methods.append({
                'method': 'email',
                'display_name': 'بريد إلكتروني',
                'email': email[:3] + '*' * (len(email) - 6) + email[-3:]
            })
        
        if user_data.get('google_auth_enabled'):
            available_methods.append({
                'method': 'google_auth',
                'display_name': 'Google Authenticator'
            })
        
        return {
            'success': False,
            'requires_2fa': True,
            'available_methods': available_methods,
            'user_id': user_data['user_id'],
            'message': 'مطلوب مصادقة ثنائية لإكمال تسجيل الدخول'
        }
    
    def _create_session(self, user_data: Dict, auth_methods: List[str], 
                       device_info: Dict, location_info: Dict) -> LoginSession:
        """إنشاء جلسة جديدة"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=self.security_settings['session_timeout_hours'])
        
        session = LoginSession(
            session_id=session_id,
            user_id=user_data['user_id'],
            auth_methods=auth_methods,
            device_info=device_info,
            location_info=location_info,
            created_at=datetime.now(),
            expires_at=expires_at,
            status=SessionStatus.ACTIVE.value,
            last_activity=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        return session
    
    def _generate_jwt_token(self, session: LoginSession) -> str:
        """إنشاء JWT token"""
        payload = {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'exp': session.expires_at,
            'iat': datetime.now(),
            'auth_methods': session.auth_methods
        }
        
        return jwt.encode(payload, current_app.config.get('JWT_SECRET_KEY', 'secret'), algorithm='HS256')
    
    def _generate_refresh_token(self, session: LoginSession) -> str:
        """إنشاء refresh token"""
        return secrets.token_urlsafe(32)
    
    def _generate_otp(self) -> str:
        """إنشاء رمز OTP"""
        return str(secrets.randbelow(900000) + 100000)  # رمز من 6 أرقام
    
    def _generate_backup_codes(self, user_id: str) -> List[str]:
        """إنشاء رموز النسخ الاحتياطي"""
        codes = []
        for _ in range(10):
            code = secrets.token_hex(4).upper()
            codes.append(f"{code[:4]}-{code[4:]}")
        
        # حفظ الرموز (مشفرة) في قاعدة البيانات
        self._save_backup_codes(user_id, codes)
        
        return codes
    
    # دوال مساعدة للبيانات (في التطبيق الحقيقي ستكون مع قاعدة البيانات)
    def _get_stored_biometric(self, email: str, biometric_type: str, device_info: Dict) -> Optional[Dict]:
        """الحصول على البيانات البيومترية المخزنة"""
        # محاكاة البيانات المخزنة
        return None
    
    def _get_stored_otp(self, email: str, otp_type: str) -> Optional[Dict]:
        """الحصول على رمز OTP المخزن"""
        # محاكاة البيانات المخزنة
        return None
    
    def _get_user_totp_secret(self, email: str) -> Optional[str]:
        """الحصول على سر TOTP للمستخدم"""
        # محاكاة البيانات المخزنة
        return None
    
    def _get_user_by_email(self, email: str) -> Optional[Dict]:
        """الحصول على المستخدم بالبريد الإلكتروني"""
        # محاكاة البيانات
        return None
    
    def _get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """الحصول على المستخدم بالمعرف"""
        # محاكاة البيانات
        return None
    
    def _get_stored_qr_token(self, qr_token: str) -> Optional[Dict]:
        """الحصول على رمز QR المخزن"""
        # محاكاة البيانات المخزنة
        return None
    
    def _log_login_attempt(self, email: str, ip_address: str, auth_method: str, 
                          success: bool, device_info: Dict):
        """تسجيل محاولة تسجيل الدخول"""
        key = f"{email}:{ip_address}"
        if key not in self.login_attempts:
            self.login_attempts[key] = []
        
        self.login_attempts[key].append({
            'timestamp': datetime.now(),
            'auth_method': auth_method,
            'success': success,
            'device_info': device_info
        })
    
    def _get_remaining_attempts(self, email: str, ip_address: str) -> int:
        """الحصول على المحاولات المتبقية"""
        key = f"{email}:{ip_address}"
        if key in self.login_attempts:
            recent_attempts = [a for a in self.login_attempts[key] if 
                             datetime.now() - a['timestamp'] < timedelta(minutes=30)]
            failed_attempts = [a for a in recent_attempts if not a['success']]
            return max(0, self.security_settings['max_login_attempts'] - len(failed_attempts))
        return self.security_settings['max_login_attempts']
    
    def _is_trusted_device(self, user_id: str, device_info: Dict) -> bool:
        """فحص ما إذا كان الجهاز موثوق"""
        device_fingerprint = self._generate_device_fingerprint(device_info)
        return user_id in self.trusted_devices and device_fingerprint in self.trusted_devices[user_id]
    
    def _add_trusted_device(self, user_id: str, device_info: Dict):
        """إضافة جهاز للأجهزة الموثوقة"""
        device_fingerprint = self._generate_device_fingerprint(device_info)
        if user_id not in self.trusted_devices:
            self.trusted_devices[user_id] = []
        self.trusted_devices[user_id].append(device_fingerprint)
    
    def _generate_device_fingerprint(self, device_info: Dict) -> str:
        """إنشاء بصمة الجهاز"""
        fingerprint_data = f"{device_info.get('type', '')}{device_info.get('os', '')}{device_info.get('browser', '')}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def _send_login_alert(self, user_data: Dict, device_info: Dict, location_info: Dict):
        """إرسال تنبيه تسجيل دخول"""
        # في التطبيق الحقيقي، سيتم إرسال بريد إلكتروني أو SMS
        current_app.logger.info(f"تنبيه تسجيل دخول جديد للمستخدم {user_data['user_id']}")
    
    def _send_sms_otp(self, phone: str, code: str):
        """إرسال رمز OTP عبر SMS"""
        # في التطبيق الحقيقي، سيتم استخدام خدمة SMS
        current_app.logger.info(f"إرسال رمز SMS {code} إلى {phone}")
    
    def _send_email_otp(self, email: str, code: str, name: str):
        """إرسال رمز OTP عبر البريد الإلكتروني"""
        # في التطبيق الحقيقي، سيتم إرسال بريد إلكتروني
        current_app.logger.info(f"إرسال رمز بريد إلكتروني {code} إلى {email}")
    
    def _check_password_expiry(self, user_data: Dict) -> bool:
        """فحص انتهاء صلاحية كلمة المرور"""
        # في التطبيق الحقيقي، سيتم فحص تاريخ آخر تغيير لكلمة المرور
        return False
    
    def _get_security_recommendations(self, user_data: Dict, device_info: Dict) -> List[str]:
        """الحصول على توصيات الأمان"""
        recommendations = []
        
        if not user_data.get('2fa_enabled'):
            recommendations.append('قم بتفعيل المصادقة الثنائية لحماية إضافية')
        
        if not self._is_trusted_device(user_data['user_id'], device_info):
            recommendations.append('أضف هذا الجهاز للأجهزة الموثوقة إذا كنت تستخدمه بانتظام')
        
        return recommendations
    
    def _get_session_security_recommendations(self, sessions: List[Dict]) -> List[str]:
        """الحصول على توصيات أمان الجلسات"""
        recommendations = []
        
        if len(sessions) > 5:
            recommendations.append('لديك عدد كبير من الجلسات النشطة، فكر في إلغاء الجلسات غير المستخدمة')
        
        old_sessions = [s for s in sessions if 
                       datetime.now() - datetime.fromisoformat(s['last_activity'].replace('Z', '+00:00')) > timedelta(days=7)]
        
        if old_sessions:
            recommendations.append('لديك جلسات قديمة غير نشطة، يُنصح بإلغائها')
        
        return recommendations
    
    # دوال حفظ البيانات (محاكاة)
    def _save_user_totp_secret(self, user_id: str, secret: str):
        """حفظ سر TOTP للمستخدم"""
        pass
    
    def _save_biometric_data(self, user_id: str, biometric_type: str, biometric_hash: str, device_info: Dict):
        """حفظ البيانات البيومترية"""
        pass
    
    def _save_qr_token(self, qr_token: str, user_id: str, expires_at: datetime):
        """حفظ رمز QR"""
        pass
    
    def _save_backup_codes(self, user_id: str, codes: List[str]):
        """حفظ رموز النسخ الاحتياطي"""
        pass

