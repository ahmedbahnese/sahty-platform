"""
خدمة البطاقة الصحية الرقمية والهوية الطبية
"""

import os
import json
import uuid
import qrcode
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
import base64
from cryptography.fernet import Fernet
import jwt

class CardType(Enum):
    PATIENT = "مريض"
    DOCTOR = "طبيب"
    NURSE = "ممرض"
    PHARMACIST = "صيدلي"
    TECHNICIAN = "فني"
    EMERGENCY = "طوارئ"
    FAMILY_MEMBER = "فرد عائلة"

class CardStatus(Enum):
    ACTIVE = "نشط"
    SUSPENDED = "معلق"
    EXPIRED = "منتهي الصلاحية"
    REVOKED = "ملغي"
    PENDING_VERIFICATION = "في انتظار التحقق"

class AccessLevel(Enum):
    PUBLIC = "عام"
    MEDICAL_STAFF = "طاقم طبي"
    EMERGENCY_ONLY = "طوارئ فقط"
    FAMILY_ONLY = "عائلة فقط"
    PRIVATE = "خاص"

class VerificationStatus(Enum):
    VERIFIED = "موثق"
    PENDING = "في الانتظار"
    REJECTED = "مرفوض"
    EXPIRED = "منتهي الصلاحية"

@dataclass
class DigitalHealthCard:
    card_id: str
    user_id: str
    card_type: str
    card_number: str
    holder_info: Dict
    medical_info: Dict
    emergency_contacts: List[Dict]
    insurance_info: Dict
    access_permissions: Dict
    verification_status: str
    issued_date: datetime
    expiry_date: datetime
    last_updated: datetime
    status: str

@dataclass
class CardAccess:
    access_id: str
    card_id: str
    accessor_id: str
    access_type: str
    access_level: str
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

class DigitalHealthCardService:
    def __init__(self):
        """تهيئة خدمة البطاقة الصحية الرقمية"""
        
        # إعدادات البطاقة
        self.card_settings = {
            'card_validity_years': 5,
            'emergency_access_duration_hours': 24,
            'qr_code_expiry_minutes': 15,
            'max_emergency_contacts': 5,
            'require_photo_verification': True,
            'enable_biometric_access': True,
            'auto_backup_enabled': True
        }
        
        # مستويات الوصول للمعلومات
        self.access_levels = {
            AccessLevel.PUBLIC.value: {
                'basic_info': True,
                'emergency_contacts': False,
                'medical_history': False,
                'medications': False,
                'allergies': False,
                'insurance': False,
                'family_info': False
            },
            AccessLevel.MEDICAL_STAFF.value: {
                'basic_info': True,
                'emergency_contacts': True,
                'medical_history': True,
                'medications': True,
                'allergies': True,
                'insurance': True,
                'family_info': False
            },
            AccessLevel.EMERGENCY_ONLY.value: {
                'basic_info': True,
                'emergency_contacts': True,
                'medical_history': True,
                'medications': True,
                'allergies': True,
                'insurance': False,
                'family_info': False
            },
            AccessLevel.FAMILY_ONLY.value: {
                'basic_info': True,
                'emergency_contacts': True,
                'medical_history': True,
                'medications': True,
                'allergies': True,
                'insurance': True,
                'family_info': True
            },
            AccessLevel.PRIVATE.value: {
                'basic_info': False,
                'emergency_contacts': False,
                'medical_history': False,
                'medications': False,
                'allergies': False,
                'insurance': False,
                'family_info': False
            }
        }
        
        # قوالب البطاقات
        self.card_templates = {
            CardType.PATIENT.value: {
                'required_fields': [
                    'full_name', 'date_of_birth', 'gender', 'blood_type',
                    'national_id', 'phone', 'address', 'emergency_contact'
                ],
                'optional_fields': [
                    'photo', 'medical_history', 'allergies', 'medications',
                    'insurance_info', 'family_doctor', 'preferred_hospital'
                ],
                'verification_required': ['national_id', 'phone'],
                'default_access_level': AccessLevel.MEDICAL_STAFF.value
            },
            CardType.DOCTOR.value: {
                'required_fields': [
                    'full_name', 'medical_license', 'specialization',
                    'hospital_affiliation', 'phone', 'email'
                ],
                'optional_fields': [
                    'photo', 'qualifications', 'experience_years',
                    'consultation_fees', 'available_hours'
                ],
                'verification_required': ['medical_license', 'hospital_affiliation'],
                'default_access_level': AccessLevel.PUBLIC.value
            },
            CardType.EMERGENCY.value: {
                'required_fields': [
                    'full_name', 'date_of_birth', 'blood_type',
                    'allergies', 'chronic_conditions', 'emergency_medications'
                ],
                'optional_fields': [
                    'photo', 'insurance_info', 'family_contacts'
                ],
                'verification_required': ['blood_type'],
                'default_access_level': AccessLevel.EMERGENCY_ONLY.value
            }
        }
        
        # معايير التشفير
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # قاعدة بيانات البطاقات (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.health_cards = {}
        self.card_accesses = {}
        self.card_activities = {}
        self.verification_requests = {}
        self.qr_tokens = {}
    
    def create_health_card(self, card_data: Dict) -> Dict:
        """
        إنشاء بطاقة صحية رقمية جديدة
        
        Args:
            card_data: بيانات البطاقة
            
        Returns:
            Dict: معلومات البطاقة الجديدة
        """
        try:
            user_id = card_data.get('user_id')
            card_type = card_data.get('card_type', CardType.PATIENT.value)
            holder_info = card_data.get('holder_info', {})
            medical_info = card_data.get('medical_info', {})
            emergency_contacts = card_data.get('emergency_contacts', [])
            insurance_info = card_data.get('insurance_info', {})
            
            # التحقق من البيانات المطلوبة
            template = self.card_templates.get(card_type)
            if not template:
                return {
                    'success': False,
                    'error': 'نوع بطاقة غير مدعوم'
                }
            
            validation_result = self._validate_card_data(holder_info, template)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['errors']
                }
            
            # إنشاء معرف ورقم البطاقة
            card_id = str(uuid.uuid4())
            card_number = self._generate_card_number(card_type)
            
            # تشفير المعلومات الحساسة
            encrypted_medical_info = self._encrypt_sensitive_data(medical_info)
            encrypted_insurance_info = self._encrypt_sensitive_data(insurance_info)
            
            # إنشاء البطاقة
            health_card = DigitalHealthCard(
                card_id=card_id,
                user_id=user_id,
                card_type=card_type,
                card_number=card_number,
                holder_info=holder_info,
                medical_info=encrypted_medical_info,
                emergency_contacts=emergency_contacts,
                insurance_info=encrypted_insurance_info,
                access_permissions=self._get_default_permissions(card_type),
                verification_status=VerificationStatus.PENDING.value,
                issued_date=datetime.now(),
                expiry_date=datetime.now() + timedelta(days=365 * self.card_settings['card_validity_years']),
                last_updated=datetime.now(),
                status=CardStatus.PENDING_VERIFICATION.value
            )
            
            self.health_cards[card_id] = health_card
            
            # بدء عملية التحقق
            verification_result = self._initiate_verification(health_card, template)
            
            # تسجيل النشاط
            self._log_card_activity(
                card_id, user_id, 'card_created',
                f'تم إنشاء بطاقة صحية من نوع {card_type}'
            )
            
            # إنشاء رمز QR للبطاقة
            qr_code = self._generate_card_qr_code(health_card)
            
            return {
                'success': True,
                'health_card': {
                    'card_id': health_card.card_id,
                    'card_number': health_card.card_number,
                    'card_type': health_card.card_type,
                    'holder_name': holder_info.get('full_name'),
                    'status': health_card.status,
                    'verification_status': health_card.verification_status,
                    'issued_date': health_card.issued_date.isoformat(),
                    'expiry_date': health_card.expiry_date.isoformat()
                },
                'qr_code': qr_code,
                'verification_info': verification_result,
                'next_steps': [
                    'انتظر التحقق من البيانات',
                    'قم برفع المستندات المطلوبة',
                    'فعل الإشعارات للحصول على التحديثات'
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء البطاقة الصحية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء البطاقة الصحية'
            }
    
    def get_health_card(self, card_id: str, requester_id: str, 
                       access_context: str = 'normal') -> Dict:
        """
        الحصول على البطاقة الصحية
        
        Args:
            card_id: معرف البطاقة
            requester_id: معرف طالب المعلومات
            access_context: سياق الوصول (normal, emergency, medical)
            
        Returns:
            Dict: معلومات البطاقة
        """
        try:
            # التحقق من وجود البطاقة
            if card_id not in self.health_cards:
                return {
                    'success': False,
                    'error': 'البطاقة غير موجودة'
                }
            
            health_card = self.health_cards[card_id]
            
            # التحقق من صلاحية البطاقة
            if health_card.status not in [CardStatus.ACTIVE.value, CardStatus.PENDING_VERIFICATION.value]:
                return {
                    'success': False,
                    'error': 'البطاقة غير نشطة'
                }
            
            # تحديد مستوى الوصول
            access_level = self._determine_access_level(
                health_card, requester_id, access_context
            )
            
            if not access_level:
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية للوصول لهذه البطاقة'
                }
            
            # فلترة المعلومات حسب مستوى الوصول
            filtered_info = self._filter_card_info(health_card, access_level)
            
            # فك تشفير المعلومات المسموحة
            if access_level in [AccessLevel.MEDICAL_STAFF.value, AccessLevel.EMERGENCY_ONLY.value]:
                filtered_info['medical_info'] = self._decrypt_sensitive_data(
                    health_card.medical_info
                )
                filtered_info['insurance_info'] = self._decrypt_sensitive_data(
                    health_card.insurance_info
                )
            
            # تسجيل الوصول
            self._log_card_access(card_id, requester_id, access_level, access_context)
            
            # إشعار صاحب البطاقة (إذا لم يكن هو الطالب)
            if requester_id != health_card.user_id:
                self._notify_card_access(health_card, requester_id, access_context)
            
            return {
                'success': True,
                'card_info': filtered_info,
                'access_level': access_level,
                'access_context': access_context,
                'accessed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على البطاقة الصحية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على البطاقة'
            }
    
    def update_health_card(self, update_data: Dict) -> Dict:
        """
        تحديث البطاقة الصحية
        
        Args:
            update_data: بيانات التحديث
            
        Returns:
            Dict: نتيجة التحديث
        """
        try:
            card_id = update_data.get('card_id')
            user_id = update_data.get('user_id')
            updates = update_data.get('updates', {})
            
            # التحقق من وجود البطاقة
            if card_id not in self.health_cards:
                return {
                    'success': False,
                    'error': 'البطاقة غير موجودة'
                }
            
            health_card = self.health_cards[card_id]
            
            # التحقق من صلاحية التحديث
            if health_card.user_id != user_id:
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية تحديث هذه البطاقة'
                }
            
            # تطبيق التحديثات
            updated_fields = []
            
            if 'holder_info' in updates:
                health_card.holder_info.update(updates['holder_info'])
                updated_fields.append('معلومات الحامل')
            
            if 'medical_info' in updates:
                encrypted_medical = self._encrypt_sensitive_data(updates['medical_info'])
                health_card.medical_info.update(encrypted_medical)
                updated_fields.append('المعلومات الطبية')
            
            if 'emergency_contacts' in updates:
                health_card.emergency_contacts = updates['emergency_contacts']
                updated_fields.append('جهات الاتصال الطارئة')
            
            if 'insurance_info' in updates:
                encrypted_insurance = self._encrypt_sensitive_data(updates['insurance_info'])
                health_card.insurance_info.update(encrypted_insurance)
                updated_fields.append('معلومات التأمين')
            
            if 'access_permissions' in updates:
                health_card.access_permissions.update(updates['access_permissions'])
                updated_fields.append('صلاحيات الوصول')
            
            # تحديث تاريخ آخر تعديل
            health_card.last_updated = datetime.now()
            
            # إعادة التحقق إذا لزم الأمر
            verification_needed = self._check_verification_needed(updates)
            if verification_needed:
                health_card.verification_status = VerificationStatus.PENDING.value
            
            # تسجيل النشاط
            self._log_card_activity(
                card_id, user_id, 'card_updated',
                f'تم تحديث: {", ".join(updated_fields)}'
            )
            
            # إنشاء رمز QR جديد
            new_qr_code = self._generate_card_qr_code(health_card)
            
            return {
                'success': True,
                'message': 'تم تحديث البطاقة بنجاح',
                'updated_fields': updated_fields,
                'verification_needed': verification_needed,
                'new_qr_code': new_qr_code,
                'last_updated': health_card.last_updated.isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحديث البطاقة الصحية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تحديث البطاقة'
            }
    
    def generate_emergency_access_code(self, card_id: str, requester_info: Dict) -> Dict:
        """
        إنشاء رمز وصول طوارئ
        
        Args:
            card_id: معرف البطاقة
            requester_info: معلومات طالب الوصول
            
        Returns:
            Dict: رمز الوصول الطارئ
        """
        try:
            # التحقق من وجود البطاقة
            if card_id not in self.health_cards:
                return {
                    'success': False,
                    'error': 'البطاقة غير موجودة'
                }
            
            health_card = self.health_cards[card_id]
            
            # إنشاء رمز وصول طوارئ
            emergency_code = self._generate_emergency_code()
            expires_at = datetime.now() + timedelta(
                hours=self.card_settings['emergency_access_duration_hours']
            )
            
            # حفظ رمز الطوارئ
            emergency_access = {
                'access_id': str(uuid.uuid4()),
                'card_id': card_id,
                'emergency_code': emergency_code,
                'requester_info': requester_info,
                'created_at': datetime.now(),
                'expires_at': expires_at,
                'used': False,
                'access_level': AccessLevel.EMERGENCY_ONLY.value
            }
            
            # في التطبيق الحقيقي، سيتم حفظ هذا في قاعدة البيانات
            self.card_accesses[emergency_access['access_id']] = emergency_access
            
            # إشعار صاحب البطاقة
            self._notify_emergency_access_request(health_card, requester_info, emergency_code)
            
            # تسجيل النشاط
            self._log_card_activity(
                card_id, 'emergency_system', 'emergency_access_generated',
                f'تم إنشاء رمز وصول طوارئ بواسطة {requester_info.get("name", "غير محدد")}'
            )
            
            return {
                'success': True,
                'emergency_code': emergency_code,
                'expires_at': expires_at.isoformat(),
                'expires_in_hours': self.card_settings['emergency_access_duration_hours'],
                'access_level': AccessLevel.EMERGENCY_ONLY.value,
                'instructions': [
                    'استخدم هذا الرمز للوصول للمعلومات الطبية الأساسية',
                    'الرمز صالح لمدة 24 ساعة فقط',
                    'تم إشعار صاحب البطاقة بطلب الوصول',
                    'استخدم الرمز بمسؤولية وفقط في حالات الطوارئ'
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء رمز وصول الطوارئ: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء رمز الوصول الطارئ'
            }
    
    def access_with_emergency_code(self, emergency_code: str, requester_info: Dict) -> Dict:
        """
        الوصول باستخدام رمز الطوارئ
        
        Args:
            emergency_code: رمز الطوارئ
            requester_info: معلومات طالب الوصول
            
        Returns:
            Dict: معلومات البطاقة الطبية
        """
        try:
            # البحث عن رمز الطوارئ
            emergency_access = None
            for access in self.card_accesses.values():
                if (access.get('emergency_code') == emergency_code and
                    not access.get('used') and
                    datetime.now() <= access.get('expires_at')):
                    emergency_access = access
                    break
            
            if not emergency_access:
                return {
                    'success': False,
                    'error': 'رمز الطوارئ غير صالح أو منتهي الصلاحية'
                }
            
            # الحصول على البطاقة
            card_id = emergency_access['card_id']
            health_card = self.health_cards[card_id]
            
            # فلترة المعلومات للطوارئ
            emergency_info = self._get_emergency_info(health_card)
            
            # تسجيل الاستخدام
            emergency_access['used'] = True
            emergency_access['used_at'] = datetime.now()
            emergency_access['used_by'] = requester_info
            
            # تسجيل النشاط
            self._log_card_activity(
                card_id, 'emergency_system', 'emergency_access_used',
                f'تم استخدام رمز الطوارئ بواسطة {requester_info.get("name", "غير محدد")}'
            )
            
            # إشعار صاحب البطاقة
            self._notify_emergency_access_used(health_card, requester_info)
            
            return {
                'success': True,
                'emergency_info': emergency_info,
                'access_type': 'emergency',
                'accessed_at': datetime.now().isoformat(),
                'emergency_contacts': health_card.emergency_contacts,
                'important_notes': [
                    'هذه معلومات طوارئ فقط',
                    'للمعلومات الكاملة، اتصل بالطبيب المعالج',
                    'تم إشعار صاحب البطاقة بالوصول'
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الوصول برمز الطوارئ: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الوصول برمز الطوارئ'
            }
    
    def generate_qr_access_token(self, card_id: str, user_id: str, 
                                access_duration_minutes: int = 15) -> Dict:
        """
        إنشاء رمز QR للوصول المؤقت
        
        Args:
            card_id: معرف البطاقة
            user_id: معرف المستخدم
            access_duration_minutes: مدة الوصول بالدقائق
            
        Returns:
            Dict: رمز QR للوصول
        """
        try:
            # التحقق من وجود البطاقة
            if card_id not in self.health_cards:
                return {
                    'success': False,
                    'error': 'البطاقة غير موجودة'
                }
            
            health_card = self.health_cards[card_id]
            
            # التحقق من الصلاحية
            if health_card.user_id != user_id:
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية إنشاء رمز QR لهذه البطاقة'
                }
            
            # إنشاء رمز الوصول
            access_token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(minutes=access_duration_minutes)
            
            # بيانات رمز QR
            qr_data = {
                'token': access_token,
                'card_id': card_id,
                'expires_at': expires_at.isoformat(),
                'access_type': 'temporary',
                'app': 'sahty'
            }
            
            # إنشاء رمز QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_image = base64.b64encode(buffer.getvalue()).decode()
            
            # حفظ رمز الوصول
            self.qr_tokens[access_token] = {
                'card_id': card_id,
                'user_id': user_id,
                'created_at': datetime.now(),
                'expires_at': expires_at,
                'used': False
            }
            
            return {
                'success': True,
                'access_token': access_token,
                'qr_image': qr_image,
                'expires_at': expires_at.isoformat(),
                'expires_in_minutes': access_duration_minutes,
                'instructions': [
                    'اعرض هذا الرمز للطاقم الطبي',
                    'الرمز صالح لمدة محدودة فقط',
                    'لا تشارك الرمز مع أشخاص غير مخولين'
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء رمز QR للوصول: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء رمز QR'
            }
    
    def scan_qr_code(self, qr_token: str, scanner_info: Dict) -> Dict:
        """
        مسح رمز QR للوصول للبطاقة
        
        Args:
            qr_token: رمز QR
            scanner_info: معلومات الماسح
            
        Returns:
            Dict: معلومات البطاقة
        """
        try:
            # التحقق من صلاحية الرمز
            if qr_token not in self.qr_tokens:
                return {
                    'success': False,
                    'error': 'رمز QR غير صالح'
                }
            
            token_data = self.qr_tokens[qr_token]
            
            if token_data['used']:
                return {
                    'success': False,
                    'error': 'تم استخدام هذا الرمز مسبقاً'
                }
            
            if datetime.now() > token_data['expires_at']:
                return {
                    'success': False,
                    'error': 'انتهت صلاحية رمز QR'
                }
            
            # الحصول على البطاقة
            card_id = token_data['card_id']
            health_card = self.health_cards[card_id]
            
            # تحديد مستوى الوصول للماسح
            scanner_access_level = self._determine_scanner_access_level(scanner_info)
            
            # فلترة المعلومات
            filtered_info = self._filter_card_info(health_card, scanner_access_level)
            
            # تسجيل الاستخدام
            token_data['used'] = True
            token_data['used_at'] = datetime.now()
            token_data['scanner_info'] = scanner_info
            
            # تسجيل النشاط
            self._log_card_activity(
                card_id, scanner_info.get('user_id', 'unknown'), 'qr_scanned',
                f'تم مسح رمز QR بواسطة {scanner_info.get("name", "غير محدد")}'
            )
            
            # إشعار صاحب البطاقة
            self._notify_qr_access(health_card, scanner_info)
            
            return {
                'success': True,
                'card_info': filtered_info,
                'access_level': scanner_access_level,
                'scanned_at': datetime.now().isoformat(),
                'scanner_info': scanner_info
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في مسح رمز QR: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في مسح رمز QR'
            }
    
    def get_card_access_history(self, card_id: str, user_id: str, 
                               limit: int = 50, offset: int = 0) -> Dict:
        """
        الحصول على تاريخ الوصول للبطاقة
        
        Args:
            card_id: معرف البطاقة
            user_id: معرف المستخدم
            limit: عدد السجلات
            offset: الإزاحة
            
        Returns:
            Dict: تاريخ الوصول
        """
        try:
            # التحقق من وجود البطاقة
            if card_id not in self.health_cards:
                return {
                    'success': False,
                    'error': 'البطاقة غير موجودة'
                }
            
            health_card = self.health_cards[card_id]
            
            # التحقق من الصلاحية
            if health_card.user_id != user_id:
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية لعرض تاريخ هذه البطاقة'
                }
            
            # جمع سجلات الوصول
            access_history = self.card_activities.get(card_id, [])
            
            # ترتيب السجلات حسب التاريخ (الأحدث أولاً)
            sorted_history = sorted(
                access_history,
                key=lambda x: x['timestamp'],
                reverse=True
            )
            
            # تطبيق الحد والإزاحة
            paginated_history = sorted_history[offset:offset + limit]
            
            # تحليل الإحصائيات
            statistics = self._analyze_access_statistics(access_history)
            
            return {
                'success': True,
                'access_history': paginated_history,
                'total_records': len(access_history),
                'has_more': offset + limit < len(access_history),
                'statistics': statistics
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على تاريخ الوصول: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على تاريخ الوصول'
            }
    
    def backup_health_card(self, card_id: str, user_id: str) -> Dict:
        """
        إنشاء نسخة احتياطية من البطاقة الصحية
        
        Args:
            card_id: معرف البطاقة
            user_id: معرف المستخدم
            
        Returns:
            Dict: معلومات النسخة الاحتياطية
        """
        try:
            # التحقق من وجود البطاقة
            if card_id not in self.health_cards:
                return {
                    'success': False,
                    'error': 'البطاقة غير موجودة'
                }
            
            health_card = self.health_cards[card_id]
            
            # التحقق من الصلاحية
            if health_card.user_id != user_id:
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية لعمل نسخة احتياطية لهذه البطاقة'
                }
            
            # إنشاء النسخة الاحتياطية
            backup_data = {
                'card_id': health_card.card_id,
                'card_number': health_card.card_number,
                'card_type': health_card.card_type,
                'holder_info': health_card.holder_info,
                'medical_info': self._decrypt_sensitive_data(health_card.medical_info),
                'emergency_contacts': health_card.emergency_contacts,
                'insurance_info': self._decrypt_sensitive_data(health_card.insurance_info),
                'backup_created_at': datetime.now().isoformat(),
                'backup_version': '1.0'
            }
            
            # تشفير النسخة الاحتياطية
            encrypted_backup = self._encrypt_backup_data(backup_data)
            
            # إنشاء معرف النسخة الاحتياطية
            backup_id = str(uuid.uuid4())
            
            # حفظ النسخة الاحتياطية (في التطبيق الحقيقي ستكون في تخزين آمن)
            backup_info = {
                'backup_id': backup_id,
                'card_id': card_id,
                'user_id': user_id,
                'created_at': datetime.now(),
                'encrypted_data': encrypted_backup,
                'checksum': self._calculate_checksum(encrypted_backup)
            }
            
            # تسجيل النشاط
            self._log_card_activity(
                card_id, user_id, 'backup_created',
                'تم إنشاء نسخة احتياطية من البطاقة'
            )
            
            return {
                'success': True,
                'backup_id': backup_id,
                'created_at': backup_info['created_at'].isoformat(),
                'checksum': backup_info['checksum'],
                'message': 'تم إنشاء النسخة الاحتياطية بنجاح',
                'storage_info': {
                    'encrypted': True,
                    'secure_storage': True,
                    'retention_period': '5 سنوات'
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء النسخة الاحتياطية'
            }
    
    # الدوال المساعدة
    def _validate_card_data(self, holder_info: Dict, template: Dict) -> Dict:
        """التحقق من صحة بيانات البطاقة"""
        errors = []
        
        for field in template['required_fields']:
            if field not in holder_info or not holder_info[field]:
                errors.append(f'الحقل {field} مطلوب')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _generate_card_number(self, card_type: str) -> str:
        """إنشاء رقم البطاقة"""
        prefix_map = {
            CardType.PATIENT.value: 'PT',
            CardType.DOCTOR.value: 'DR',
            CardType.NURSE.value: 'NR',
            CardType.PHARMACIST.value: 'PH',
            CardType.EMERGENCY.value: 'EM'
        }
        
        prefix = prefix_map.get(card_type, 'GN')
        timestamp = int(datetime.now().timestamp())
        random_suffix = str(uuid.uuid4())[:8].upper()
        
        return f"{prefix}{timestamp}{random_suffix}"
    
    def _encrypt_sensitive_data(self, data: Dict) -> Dict:
        """تشفير البيانات الحساسة"""
        if not data:
            return {}
        
        encrypted_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                encrypted_value = self.cipher_suite.encrypt(value.encode()).decode()
                encrypted_data[key] = encrypted_value
            else:
                encrypted_data[key] = value
        
        return encrypted_data
    
    def _decrypt_sensitive_data(self, encrypted_data: Dict) -> Dict:
        """فك تشفير البيانات الحساسة"""
        if not encrypted_data:
            return {}
        
        decrypted_data = {}
        for key, value in encrypted_data.items():
            if isinstance(value, str):
                try:
                    decrypted_value = self.cipher_suite.decrypt(value.encode()).decode()
                    decrypted_data[key] = decrypted_value
                except:
                    decrypted_data[key] = value
            else:
                decrypted_data[key] = value
        
        return decrypted_data
    
    def _get_default_permissions(self, card_type: str) -> Dict:
        """الحصول على الصلاحيات الافتراضية"""
        template = self.card_templates.get(card_type, {})
        default_level = template.get('default_access_level', AccessLevel.MEDICAL_STAFF.value)
        return self.access_levels.get(default_level, {})
    
    def _initiate_verification(self, health_card: DigitalHealthCard, template: Dict) -> Dict:
        """بدء عملية التحقق"""
        verification_steps = []
        
        for field in template['verification_required']:
            verification_steps.append({
                'field': field,
                'status': 'pending',
                'required_documents': self._get_required_documents(field)
            })
        
        return {
            'verification_steps': verification_steps,
            'estimated_completion': '2-3 أيام عمل'
        }
    
    def _get_required_documents(self, field: str) -> List[str]:
        """الحصول على المستندات المطلوبة للتحقق"""
        document_map = {
            'national_id': ['صورة البطاقة الشخصية'],
            'medical_license': ['صورة رخصة مزاولة المهنة'],
            'phone': ['رمز التحقق عبر SMS'],
            'hospital_affiliation': ['خطاب من المستشفى']
        }
        
        return document_map.get(field, [])
    
    def _generate_card_qr_code(self, health_card: DigitalHealthCard) -> str:
        """إنشاء رمز QR للبطاقة"""
        qr_data = {
            'card_id': health_card.card_id,
            'card_number': health_card.card_number,
            'holder_name': health_card.holder_info.get('full_name'),
            'card_type': health_card.card_type,
            'app': 'sahty'
        }
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def _determine_access_level(self, health_card: DigitalHealthCard, 
                               requester_id: str, context: str) -> Optional[str]:
        """تحديد مستوى الوصول"""
        # صاحب البطاقة له وصول كامل
        if health_card.user_id == requester_id:
            return AccessLevel.FAMILY_ONLY.value
        
        # سياق الطوارئ
        if context == 'emergency':
            return AccessLevel.EMERGENCY_ONLY.value
        
        # سياق طبي
        if context == 'medical':
            return AccessLevel.MEDICAL_STAFF.value
        
        # الوصول العام
        return AccessLevel.PUBLIC.value
    
    def _filter_card_info(self, health_card: DigitalHealthCard, access_level: str) -> Dict:
        """فلترة معلومات البطاقة حسب مستوى الوصول"""
        permissions = self.access_levels.get(access_level, {})
        filtered_info = {
            'card_id': health_card.card_id,
            'card_number': health_card.card_number,
            'card_type': health_card.card_type,
            'status': health_card.status
        }
        
        if permissions.get('basic_info'):
            filtered_info['holder_info'] = health_card.holder_info
        
        if permissions.get('emergency_contacts'):
            filtered_info['emergency_contacts'] = health_card.emergency_contacts
        
        if permissions.get('medical_history'):
            filtered_info['medical_info'] = health_card.medical_info
        
        if permissions.get('insurance'):
            filtered_info['insurance_info'] = health_card.insurance_info
        
        return filtered_info
    
    def _generate_emergency_code(self) -> str:
        """إنشاء رمز طوارئ"""
        return str(uuid.uuid4())[:8].upper()
    
    def _get_emergency_info(self, health_card: DigitalHealthCard) -> Dict:
        """الحصول على معلومات الطوارئ"""
        medical_info = self._decrypt_sensitive_data(health_card.medical_info)
        
        return {
            'holder_name': health_card.holder_info.get('full_name'),
            'date_of_birth': health_card.holder_info.get('date_of_birth'),
            'blood_type': health_card.holder_info.get('blood_type'),
            'allergies': medical_info.get('allergies', []),
            'chronic_conditions': medical_info.get('chronic_conditions', []),
            'current_medications': medical_info.get('current_medications', []),
            'emergency_contacts': health_card.emergency_contacts
        }
    
    def _determine_scanner_access_level(self, scanner_info: Dict) -> str:
        """تحديد مستوى وصول الماسح"""
        scanner_type = scanner_info.get('type', 'public')
        
        if scanner_type == 'medical_staff':
            return AccessLevel.MEDICAL_STAFF.value
        elif scanner_type == 'emergency':
            return AccessLevel.EMERGENCY_ONLY.value
        else:
            return AccessLevel.PUBLIC.value
    
    def _analyze_access_statistics(self, access_history: List[Dict]) -> Dict:
        """تحليل إحصائيات الوصول"""
        total_accesses = len(access_history)
        
        # تحليل أنواع الوصول
        access_types = {}
        for record in access_history:
            access_type = record.get('activity_type', 'unknown')
            access_types[access_type] = access_types.get(access_type, 0) + 1
        
        # آخر وصول
        last_access = access_history[0] if access_history else None
        
        return {
            'total_accesses': total_accesses,
            'access_types': access_types,
            'last_access': last_access['timestamp'].isoformat() if last_access else None,
            'most_common_access': max(access_types.items(), key=lambda x: x[1])[0] if access_types else None
        }
    
    def _encrypt_backup_data(self, data: Dict) -> str:
        """تشفير بيانات النسخة الاحتياطية"""
        json_data = json.dumps(data)
        encrypted_data = self.cipher_suite.encrypt(json_data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def _calculate_checksum(self, data: str) -> str:
        """حساب checksum للبيانات"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _check_verification_needed(self, updates: Dict) -> bool:
        """فحص ما إذا كان التحقق مطلوب بعد التحديث"""
        sensitive_fields = ['national_id', 'medical_license', 'phone']
        
        for field in sensitive_fields:
            if field in updates.get('holder_info', {}):
                return True
        
        return False
    
    def _log_card_activity(self, card_id: str, user_id: str, activity_type: str, description: str):
        """تسجيل نشاط البطاقة"""
        if card_id not in self.card_activities:
            self.card_activities[card_id] = []
        
        activity = {
            'activity_id': str(uuid.uuid4()),
            'user_id': user_id,
            'activity_type': activity_type,
            'description': description,
            'timestamp': datetime.now(),
            'ip_address': 'unknown',  # في التطبيق الحقيقي سيتم الحصول على IP
            'user_agent': 'unknown'   # في التطبيق الحقيقي سيتم الحصول على User Agent
        }
        
        self.card_activities[card_id].append(activity)
    
    def _log_card_access(self, card_id: str, requester_id: str, access_level: str, context: str):
        """تسجيل وصول البطاقة"""
        self._log_card_activity(
            card_id, requester_id, 'card_accessed',
            f'تم الوصول للبطاقة بمستوى {access_level} في سياق {context}'
        )
    
    def _notify_card_access(self, health_card: DigitalHealthCard, requester_id: str, context: str):
        """إشعار صاحب البطاقة بالوصول"""
        # في التطبيق الحقيقي، سيتم إرسال إشعار
        current_app.logger.info(f"إشعار وصول البطاقة {health_card.card_id} بواسطة {requester_id}")
    
    def _notify_emergency_access_request(self, health_card: DigitalHealthCard, 
                                       requester_info: Dict, emergency_code: str):
        """إشعار طلب وصول طوارئ"""
        current_app.logger.info(f"طلب وصول طوارئ للبطاقة {health_card.card_id}")
    
    def _notify_emergency_access_used(self, health_card: DigitalHealthCard, requester_info: Dict):
        """إشعار استخدام وصول طوارئ"""
        current_app.logger.info(f"تم استخدام وصول طوارئ للبطاقة {health_card.card_id}")
    
    def _notify_qr_access(self, health_card: DigitalHealthCard, scanner_info: Dict):
        """إشعار مسح رمز QR"""
        current_app.logger.info(f"تم مسح رمز QR للبطاقة {health_card.card_id}")

