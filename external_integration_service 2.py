"""
خدمة التكامل مع الخدمات الخارجية والأنظمة الطبية
"""

import os
import json
import uuid
import requests
import hashlib
import hmac
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET

class IntegrationType(Enum):
    HOSPITAL_SYSTEM = "نظام المستشفى"
    PHARMACY_SYSTEM = "نظام الصيدلية"
    INSURANCE_SYSTEM = "نظام التأمين"
    LAB_SYSTEM = "نظام المختبر"
    GOVERNMENT_SYSTEM = "النظام الحكومي"
    PAYMENT_GATEWAY = "بوابة الدفع"
    SMS_GATEWAY = "بوابة الرسائل"
    EMAIL_SERVICE = "خدمة البريد"
    MAPS_SERVICE = "خدمة الخرائط"
    WEATHER_SERVICE = "خدمة الطقس"
    SOCIAL_MEDIA = "وسائل التواصل"
    TELEMEDICINE = "الطب عن بُعد"
    MEDICAL_DEVICES = "الأجهزة الطبية"
    CLOUD_STORAGE = "التخزين السحابي"

class IntegrationStatus(Enum):
    ACTIVE = "نشط"
    INACTIVE = "غير نشط"
    PENDING = "في الانتظار"
    ERROR = "خطأ"
    MAINTENANCE = "صيانة"

class DataFormat(Enum):
    JSON = "JSON"
    XML = "XML"
    HL7 = "HL7"
    FHIR = "FHIR"
    CSV = "CSV"
    PDF = "PDF"

@dataclass
class ExternalService:
    service_id: str
    name: str
    type: str
    endpoint_url: str
    api_key: str
    secret_key: str
    data_format: str
    status: str
    last_sync: Optional[datetime]
    sync_frequency_hours: int
    rate_limit_per_hour: int
    timeout_seconds: int
    retry_attempts: int
    webhook_url: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class IntegrationLog:
    log_id: str
    service_id: str
    operation: str
    request_data: Dict
    response_data: Dict
    status_code: int
    success: bool
    error_message: Optional[str]
    execution_time_ms: int
    timestamp: datetime

class ExternalIntegrationService:
    def __init__(self):
        """تهيئة خدمة التكامل مع الخدمات الخارجية"""
        
        # إعدادات التكامل
        self.integration_settings = {
            'default_timeout_seconds': 30,
            'default_retry_attempts': 3,
            'default_rate_limit_per_hour': 1000,
            'enable_webhook_verification': True,
            'enable_request_logging': True,
            'enable_response_caching': True,
            'cache_duration_minutes': 15,
            'enable_circuit_breaker': True,
            'circuit_breaker_threshold': 5,
            'enable_data_encryption': True
        }
        
        # الخدمات المدعومة
        self.supported_services = {
            # أنظمة المستشفيات المصرية
            'ministry_of_health': {
                'name': 'وزارة الصحة المصرية',
                'type': IntegrationType.GOVERNMENT_SYSTEM.value,
                'endpoint': 'https://api.mohp.gov.eg/v1/',
                'data_format': DataFormat.JSON.value,
                'features': ['patient_records', 'appointments', 'prescriptions']
            },
            'cairo_university_hospitals': {
                'name': 'مستشفيات جامعة القاهرة',
                'type': IntegrationType.HOSPITAL_SYSTEM.value,
                'endpoint': 'https://api.cuh.edu.eg/v1/',
                'data_format': DataFormat.HL7.value,
                'features': ['appointments', 'lab_results', 'medical_records']
            },
            'ain_shams_hospitals': {
                'name': 'مستشفيات عين شمس',
                'type': IntegrationType.HOSPITAL_SYSTEM.value,
                'endpoint': 'https://api.asu.edu.eg/medical/v1/',
                'data_format': DataFormat.FHIR.value,
                'features': ['appointments', 'prescriptions', 'imaging']
            },
            
            # أنظمة الصيدليات
            'seif_pharmacy': {
                'name': 'صيدليات صيف',
                'type': IntegrationType.PHARMACY_SYSTEM.value,
                'endpoint': 'https://api.seifpharmacy.com/v1/',
                'data_format': DataFormat.JSON.value,
                'features': ['medication_availability', 'prescription_filling', 'delivery']
            },
            'ezaby_pharmacy': {
                'name': 'صيدليات العزبي',
                'type': IntegrationType.PHARMACY_SYSTEM.value,
                'endpoint': 'https://api.ezaby.com/v1/',
                'data_format': DataFormat.JSON.value,
                'features': ['medication_search', 'price_comparison', 'online_ordering']
            },
            
            # أنظمة التأمين
            'egyptian_insurance': {
                'name': 'الهيئة العامة للتأمين الصحي',
                'type': IntegrationType.INSURANCE_SYSTEM.value,
                'endpoint': 'https://api.hio.gov.eg/v1/',
                'data_format': DataFormat.XML.value,
                'features': ['coverage_verification', 'claim_submission', 'approval_status']
            },
            
            # أنظمة المختبرات
            'alfa_lab': {
                'name': 'مختبرات ألفا',
                'type': IntegrationType.LAB_SYSTEM.value,
                'endpoint': 'https://api.alfalab.com.eg/v1/',
                'data_format': DataFormat.JSON.value,
                'features': ['test_booking', 'result_retrieval', 'home_collection']
            },
            'el_borg_lab': {
                'name': 'مختبرات البرج',
                'type': IntegrationType.LAB_SYSTEM.value,
                'endpoint': 'https://api.elborg.com/v1/',
                'data_format': DataFormat.JSON.value,
                'features': ['test_scheduling', 'digital_reports', 'trend_analysis']
            },
            
            # بوابات الدفع
            'paymob': {
                'name': 'PayMob',
                'type': IntegrationType.PAYMENT_GATEWAY.value,
                'endpoint': 'https://api.paymob.com/v1/',
                'data_format': DataFormat.JSON.value,
                'features': ['payment_processing', 'refunds', 'installments']
            },
            'fawry': {
                'name': 'فوري',
                'type': IntegrationType.PAYMENT_GATEWAY.value,
                'endpoint': 'https://api.fawry.com/v1/',
                'data_format': DataFormat.JSON.value,
                'features': ['bill_payment', 'money_transfer', 'merchant_services']
            },
            
            # خدمات الرسائل
            'vodafone_sms': {
                'name': 'فودافون SMS',
                'type': IntegrationType.SMS_GATEWAY.value,
                'endpoint': 'https://api.vodafone.com.eg/sms/v1/',
                'data_format': DataFormat.JSON.value,
                'features': ['bulk_sms', 'delivery_reports', 'two_way_messaging']
            },
            
            # خدمات الخرائط
            'google_maps': {
                'name': 'خرائط جوجل',
                'type': IntegrationType.MAPS_SERVICE.value,
                'endpoint': 'https://maps.googleapis.com/maps/api/',
                'data_format': DataFormat.JSON.value,
                'features': ['geocoding', 'directions', 'places_search']
            },
            
            # الأجهزة الطبية الذكية
            'omron_devices': {
                'name': 'أجهزة أومرون',
                'type': IntegrationType.MEDICAL_DEVICES.value,
                'endpoint': 'https://api.omronhealthcare.com/v1/',
                'data_format': DataFormat.JSON.value,
                'features': ['blood_pressure_sync', 'weight_sync', 'activity_tracking']
            },
            'fitbit': {
                'name': 'فيت بت',
                'type': IntegrationType.MEDICAL_DEVICES.value,
                'endpoint': 'https://api.fitbit.com/1/',
                'data_format': DataFormat.JSON.value,
                'features': ['activity_data', 'sleep_data', 'heart_rate']
            },
            
            # التخزين السحابي
            'google_drive': {
                'name': 'جوجل درايف',
                'type': IntegrationType.CLOUD_STORAGE.value,
                'endpoint': 'https://www.googleapis.com/drive/v3/',
                'data_format': DataFormat.JSON.value,
                'features': ['file_storage', 'backup', 'sharing']
            }
        }
        
        # قاعدة بيانات الخدمات (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.active_services = {}
        self.integration_logs = {}
        self.cached_responses = {}
        self.circuit_breakers = {}
        
        # تهيئة الخدمات الافتراضية
        self._initialize_default_services()
    
    def register_service(self, service_data: Dict) -> Dict:
        """
        تسجيل خدمة خارجية جديدة
        
        Args:
            service_data: بيانات الخدمة
            
        Returns:
            Dict: نتيجة التسجيل
        """
        try:
            service_id = str(uuid.uuid4())
            
            # التحقق من صحة البيانات
            required_fields = ['name', 'type', 'endpoint_url', 'api_key']
            for field in required_fields:
                if field not in service_data:
                    return {
                        'success': False,
                        'error': f'الحقل {field} مطلوب'
                    }
            
            # إنشاء الخدمة
            service = ExternalService(
                service_id=service_id,
                name=service_data['name'],
                type=service_data['type'],
                endpoint_url=service_data['endpoint_url'],
                api_key=service_data['api_key'],
                secret_key=service_data.get('secret_key', ''),
                data_format=service_data.get('data_format', DataFormat.JSON.value),
                status=IntegrationStatus.PENDING.value,
                last_sync=None,
                sync_frequency_hours=service_data.get('sync_frequency_hours', 24),
                rate_limit_per_hour=service_data.get('rate_limit_per_hour', 
                                                   self.integration_settings['default_rate_limit_per_hour']),
                timeout_seconds=service_data.get('timeout_seconds', 
                                               self.integration_settings['default_timeout_seconds']),
                retry_attempts=service_data.get('retry_attempts', 
                                              self.integration_settings['default_retry_attempts']),
                webhook_url=service_data.get('webhook_url'),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # اختبار الاتصال
            connection_test = self._test_service_connection(service)
            
            if connection_test['success']:
                service.status = IntegrationStatus.ACTIVE.value
                self.active_services[service_id] = service
                
                return {
                    'success': True,
                    'service_id': service_id,
                    'message': 'تم تسجيل الخدمة بنجاح',
                    'connection_test': connection_test
                }
            else:
                service.status = IntegrationStatus.ERROR.value
                return {
                    'success': False,
                    'service_id': service_id,
                    'error': 'فشل في اختبار الاتصال',
                    'connection_test': connection_test
                }
                
        except Exception as e:
            current_app.logger.error(f"خطأ في تسجيل الخدمة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تسجيل الخدمة'
            }
    
    def sync_with_service(self, service_id: str, operation: str, data: Dict = None) -> Dict:
        """
        مزامنة البيانات مع خدمة خارجية
        
        Args:
            service_id: معرف الخدمة
            operation: نوع العملية
            data: البيانات المرسلة
            
        Returns:
            Dict: نتيجة المزامنة
        """
        try:
            # التحقق من وجود الخدمة
            if service_id not in self.active_services:
                return {
                    'success': False,
                    'error': 'الخدمة غير موجودة'
                }
            
            service = self.active_services[service_id]
            
            # فحص حالة الخدمة
            if service.status != IntegrationStatus.ACTIVE.value:
                return {
                    'success': False,
                    'error': f'الخدمة غير نشطة: {service.status}'
                }
            
            # فحص Circuit Breaker
            if self._is_circuit_breaker_open(service_id):
                return {
                    'success': False,
                    'error': 'الخدمة معطلة مؤقتاً بسبب أخطاء متكررة'
                }
            
            # فحص Rate Limiting
            if not self._check_rate_limit(service_id):
                return {
                    'success': False,
                    'error': 'تم تجاوز حد الطلبات المسموح'
                }
            
            # فحص Cache
            cache_key = f"{service_id}_{operation}_{hashlib.md5(str(data).encode()).hexdigest()}"
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return {
                    'success': True,
                    'data': cached_response,
                    'cached': True
                }
            
            # تنفيذ العملية
            start_time = datetime.now()
            result = self._execute_service_operation(service, operation, data)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # تسجيل العملية
            self._log_integration_operation(
                service_id, operation, data, result, execution_time
            )
            
            # تحديث Circuit Breaker
            self._update_circuit_breaker(service_id, result['success'])
            
            # حفظ في Cache إذا نجحت العملية
            if result['success'] and self.integration_settings['enable_response_caching']:
                self._cache_response(cache_key, result['data'])
            
            # تحديث آخر مزامنة
            service.last_sync = datetime.now()
            service.updated_at = datetime.now()
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"خطأ في مزامنة الخدمة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في المزامنة'
            }
    
    def get_hospital_appointments(self, hospital_id: str, patient_id: str) -> Dict:
        """
        الحصول على مواعيد المستشفى
        
        Args:
            hospital_id: معرف المستشفى
            patient_id: معرف المريض
            
        Returns:
            Dict: قائمة المواعيد
        """
        try:
            # تحديد الخدمة حسب المستشفى
            service_mapping = {
                'cairo_university': 'cairo_university_hospitals',
                'ain_shams': 'ain_shams_hospitals'
            }
            
            service_key = service_mapping.get(hospital_id)
            if not service_key:
                return {
                    'success': False,
                    'error': 'مستشفى غير مدعوم'
                }
            
            # البحث عن الخدمة المسجلة
            service_id = self._find_service_by_key(service_key)
            if not service_id:
                return {
                    'success': False,
                    'error': 'خدمة المستشفى غير مسجلة'
                }
            
            # طلب المواعيد
            operation_data = {
                'patient_id': patient_id,
                'date_from': datetime.now().isoformat(),
                'date_to': (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            result = self.sync_with_service(service_id, 'get_appointments', operation_data)
            
            if result['success']:
                # تحويل البيانات للتنسيق الموحد
                appointments = self._normalize_appointment_data(result['data'], hospital_id)
                
                return {
                    'success': True,
                    'appointments': appointments,
                    'hospital_id': hospital_id,
                    'total_count': len(appointments)
                }
            else:
                return result
                
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على مواعيد المستشفى: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على المواعيد'
            }
    
    def check_medication_availability(self, medication_name: str, location: str = None) -> Dict:
        """
        فحص توفر الدواء في الصيدليات
        
        Args:
            medication_name: اسم الدواء
            location: الموقع (اختياري)
            
        Returns:
            Dict: معلومات التوفر
        """
        try:
            pharmacy_services = ['seif_pharmacy', 'ezaby_pharmacy']
            availability_results = []
            
            for pharmacy_key in pharmacy_services:
                service_id = self._find_service_by_key(pharmacy_key)
                if service_id:
                    operation_data = {
                        'medication_name': medication_name,
                        'location': location
                    }
                    
                    result = self.sync_with_service(service_id, 'check_availability', operation_data)
                    
                    if result['success']:
                        pharmacy_data = self._normalize_pharmacy_data(result['data'], pharmacy_key)
                        availability_results.append(pharmacy_data)
            
            return {
                'success': True,
                'medication_name': medication_name,
                'availability': availability_results,
                'total_pharmacies': len(availability_results)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في فحص توفر الدواء: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في فحص التوفر'
            }
    
    def verify_insurance_coverage(self, patient_id: str, service_code: str) -> Dict:
        """
        التحقق من تغطية التأمين
        
        Args:
            patient_id: معرف المريض
            service_code: رمز الخدمة الطبية
            
        Returns:
            Dict: معلومات التغطية
        """
        try:
            service_id = self._find_service_by_key('egyptian_insurance')
            if not service_id:
                return {
                    'success': False,
                    'error': 'خدمة التأمين غير متاحة'
                }
            
            operation_data = {
                'patient_id': patient_id,
                'service_code': service_code,
                'request_date': datetime.now().isoformat()
            }
            
            result = self.sync_with_service(service_id, 'verify_coverage', operation_data)
            
            if result['success']:
                coverage_data = self._normalize_insurance_data(result['data'])
                
                return {
                    'success': True,
                    'patient_id': patient_id,
                    'service_code': service_code,
                    'coverage': coverage_data
                }
            else:
                return result
                
        except Exception as e:
            current_app.logger.error(f"خطأ في التحقق من تغطية التأمين: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في التحقق من التغطية'
            }
    
    def get_lab_results(self, patient_id: str, lab_name: str) -> Dict:
        """
        الحصول على نتائج المختبر
        
        Args:
            patient_id: معرف المريض
            lab_name: اسم المختبر
            
        Returns:
            Dict: نتائج المختبر
        """
        try:
            lab_mapping = {
                'alfa': 'alfa_lab',
                'elborg': 'el_borg_lab'
            }
            
            service_key = lab_mapping.get(lab_name.lower())
            if not service_key:
                return {
                    'success': False,
                    'error': 'مختبر غير مدعوم'
                }
            
            service_id = self._find_service_by_key(service_key)
            if not service_id:
                return {
                    'success': False,
                    'error': 'خدمة المختبر غير مسجلة'
                }
            
            operation_data = {
                'patient_id': patient_id,
                'date_from': (datetime.now() - timedelta(days=90)).isoformat(),
                'date_to': datetime.now().isoformat()
            }
            
            result = self.sync_with_service(service_id, 'get_results', operation_data)
            
            if result['success']:
                lab_results = self._normalize_lab_data(result['data'], lab_name)
                
                return {
                    'success': True,
                    'patient_id': patient_id,
                    'lab_name': lab_name,
                    'results': lab_results,
                    'total_tests': len(lab_results)
                }
            else:
                return result
                
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على نتائج المختبر: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على النتائج'
            }
    
    def process_payment(self, payment_data: Dict) -> Dict:
        """
        معالجة الدفع عبر البوابات الخارجية
        
        Args:
            payment_data: بيانات الدفع
            
        Returns:
            Dict: نتيجة الدفع
        """
        try:
            gateway = payment_data.get('gateway', 'paymob')
            amount = payment_data.get('amount')
            currency = payment_data.get('currency', 'EGP')
            
            service_id = self._find_service_by_key(gateway)
            if not service_id:
                return {
                    'success': False,
                    'error': 'بوابة الدفع غير متاحة'
                }
            
            operation_data = {
                'amount': amount,
                'currency': currency,
                'customer_data': payment_data.get('customer_data', {}),
                'order_id': payment_data.get('order_id'),
                'callback_url': payment_data.get('callback_url')
            }
            
            result = self.sync_with_service(service_id, 'process_payment', operation_data)
            
            if result['success']:
                payment_result = self._normalize_payment_data(result['data'], gateway)
                
                return {
                    'success': True,
                    'payment_id': payment_result.get('payment_id'),
                    'payment_url': payment_result.get('payment_url'),
                    'status': payment_result.get('status'),
                    'gateway': gateway
                }
            else:
                return result
                
        except Exception as e:
            current_app.logger.error(f"خطأ في معالجة الدفع: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في معالجة الدفع'
            }
    
    def send_sms_notification(self, phone_number: str, message: str) -> Dict:
        """
        إرسال إشعار SMS
        
        Args:
            phone_number: رقم الهاتف
            message: نص الرسالة
            
        Returns:
            Dict: نتيجة الإرسال
        """
        try:
            service_id = self._find_service_by_key('vodafone_sms')
            if not service_id:
                return {
                    'success': False,
                    'error': 'خدمة الرسائل غير متاحة'
                }
            
            operation_data = {
                'phone_number': phone_number,
                'message': message,
                'sender_name': 'صحتك في أمان'
            }
            
            result = self.sync_with_service(service_id, 'send_sms', operation_data)
            
            if result['success']:
                return {
                    'success': True,
                    'message_id': result['data'].get('message_id'),
                    'status': 'sent',
                    'phone_number': phone_number
                }
            else:
                return result
                
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال الرسالة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إرسال الرسالة'
            }
    
    def sync_device_data(self, device_type: str, user_id: str, auth_token: str) -> Dict:
        """
        مزامنة بيانات الأجهزة الطبية الذكية
        
        Args:
            device_type: نوع الجهاز
            user_id: معرف المستخدم
            auth_token: رمز المصادقة
            
        Returns:
            Dict: بيانات الجهاز
        """
        try:
            device_mapping = {
                'omron': 'omron_devices',
                'fitbit': 'fitbit'
            }
            
            service_key = device_mapping.get(device_type.lower())
            if not service_key:
                return {
                    'success': False,
                    'error': 'نوع جهاز غير مدعوم'
                }
            
            service_id = self._find_service_by_key(service_key)
            if not service_id:
                return {
                    'success': False,
                    'error': 'خدمة الجهاز غير مسجلة'
                }
            
            operation_data = {
                'user_id': user_id,
                'auth_token': auth_token,
                'date_from': (datetime.now() - timedelta(days=7)).isoformat(),
                'date_to': datetime.now().isoformat()
            }
            
            result = self.sync_with_service(service_id, 'sync_data', operation_data)
            
            if result['success']:
                device_data = self._normalize_device_data(result['data'], device_type)
                
                return {
                    'success': True,
                    'device_type': device_type,
                    'user_id': user_id,
                    'data': device_data,
                    'last_sync': datetime.now().isoformat()
                }
            else:
                return result
                
        except Exception as e:
            current_app.logger.error(f"خطأ في مزامنة بيانات الجهاز: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في مزامنة البيانات'
            }
    
    def get_service_status(self, service_id: str = None) -> Dict:
        """
        الحصول على حالة الخدمات
        
        Args:
            service_id: معرف خدمة محددة (اختياري)
            
        Returns:
            Dict: حالة الخدمات
        """
        try:
            if service_id:
                if service_id not in self.active_services:
                    return {
                        'success': False,
                        'error': 'الخدمة غير موجودة'
                    }
                
                service = self.active_services[service_id]
                status_info = self._get_detailed_service_status(service)
                
                return {
                    'success': True,
                    'service': status_info
                }
            else:
                # حالة جميع الخدمات
                services_status = []
                for sid, service in self.active_services.items():
                    status_info = self._get_detailed_service_status(service)
                    services_status.append(status_info)
                
                return {
                    'success': True,
                    'services': services_status,
                    'total_services': len(services_status),
                    'active_services': len([s for s in services_status if s['status'] == 'نشط']),
                    'inactive_services': len([s for s in services_status if s['status'] != 'نشط'])
                }
                
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على حالة الخدمات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الحالة'
            }
    
    def get_integration_analytics(self, period_days: int = 30) -> Dict:
        """
        الحصول على إحصائيات التكامل
        
        Args:
            period_days: فترة الإحصائيات بالأيام
            
        Returns:
            Dict: إحصائيات التكامل
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            
            # جمع السجلات من الفترة المحددة
            period_logs = []
            for service_id, logs in self.integration_logs.items():
                period_logs.extend([
                    log for log in logs 
                    if log.timestamp >= cutoff_date
                ])
            
            # تحليل الإحصائيات
            total_requests = len(period_logs)
            successful_requests = len([log for log in period_logs if log.success])
            failed_requests = total_requests - successful_requests
            
            # إحصائيات حسب الخدمة
            service_stats = {}
            for log in period_logs:
                if log.service_id not in service_stats:
                    service_stats[log.service_id] = {
                        'total': 0,
                        'successful': 0,
                        'failed': 0,
                        'avg_response_time': 0
                    }
                
                service_stats[log.service_id]['total'] += 1
                if log.success:
                    service_stats[log.service_id]['successful'] += 1
                else:
                    service_stats[log.service_id]['failed'] += 1
            
            # حساب متوسط وقت الاستجابة
            if period_logs:
                avg_response_time = sum(log.execution_time_ms for log in period_logs) / len(period_logs)
            else:
                avg_response_time = 0
            
            # أكثر العمليات استخداماً
            operation_counts = {}
            for log in period_logs:
                if log.operation not in operation_counts:
                    operation_counts[log.operation] = 0
                operation_counts[log.operation] += 1
            
            most_used_operations = sorted(
                operation_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return {
                'success': True,
                'period_days': period_days,
                'summary': {
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'failed_requests': failed_requests,
                    'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                    'avg_response_time_ms': avg_response_time
                },
                'service_stats': service_stats,
                'most_used_operations': most_used_operations,
                'active_services_count': len(self.active_services)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على إحصائيات التكامل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الإحصائيات'
            }
    
    # الدوال المساعدة
    def _initialize_default_services(self):
        """تهيئة الخدمات الافتراضية"""
        # في التطبيق الحقيقي، ستكون هذه البيانات في قاعدة البيانات
        # هنا نضع خدمات تجريبية للاختبار
        pass
    
    def _test_service_connection(self, service: ExternalService) -> Dict:
        """اختبار الاتصال بالخدمة"""
        try:
            # محاكاة اختبار الاتصال
            # في التطبيق الحقيقي، سيتم إرسال طلب فعلي للخدمة
            
            test_url = f"{service.endpoint_url}/health"
            headers = {
                'Authorization': f'Bearer {service.api_key}',
                'Content-Type': 'application/json'
            }
            
            # محاكاة الاستجابة
            return {
                'success': True,
                'response_time_ms': 150,
                'status_code': 200,
                'message': 'الاتصال ناجح'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_service_operation(self, service: ExternalService, operation: str, data: Dict) -> Dict:
        """تنفيذ عملية على الخدمة"""
        try:
            # بناء URL العملية
            operation_url = f"{service.endpoint_url}/{operation}"
            
            # إعداد Headers
            headers = {
                'Authorization': f'Bearer {service.api_key}',
                'Content-Type': f'application/{service.data_format.lower()}'
            }
            
            # إضافة التوقيع إذا كان مطلوباً
            if service.secret_key:
                signature = self._generate_signature(data, service.secret_key)
                headers['X-Signature'] = signature
            
            # محاكاة الاستجابة حسب نوع العملية
            mock_response = self._generate_mock_response(operation, data)
            
            return {
                'success': True,
                'data': mock_response,
                'status_code': 200
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }
    
    def _generate_signature(self, data: Dict, secret_key: str) -> str:
        """إنشاء توقيع للطلب"""
        data_string = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            secret_key.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _generate_mock_response(self, operation: str, data: Dict) -> Dict:
        """إنشاء استجابة تجريبية"""
        if operation == 'get_appointments':
            return {
                'appointments': [
                    {
                        'id': 'apt_001',
                        'doctor_name': 'د. أحمد محمد',
                        'specialty': 'باطنة',
                        'date': '2024-01-15',
                        'time': '10:00',
                        'status': 'confirmed'
                    }
                ]
            }
        elif operation == 'check_availability':
            return {
                'available': True,
                'price': 25.50,
                'pharmacy_name': 'صيدلية النور',
                'address': 'شارع الجمهورية، القاهرة'
            }
        elif operation == 'verify_coverage':
            return {
                'covered': True,
                'coverage_percentage': 80,
                'copay_amount': 50.0,
                'authorization_required': False
            }
        elif operation == 'get_results':
            return {
                'tests': [
                    {
                        'test_name': 'تحليل دم شامل',
                        'date': '2024-01-10',
                        'results': {
                            'hemoglobin': '14.2 g/dl',
                            'white_cells': '7500 /ul'
                        },
                        'status': 'normal'
                    }
                ]
            }
        elif operation == 'process_payment':
            return {
                'payment_id': 'pay_' + str(uuid.uuid4()),
                'payment_url': 'https://payment.gateway.com/pay/12345',
                'status': 'pending'
            }
        elif operation == 'send_sms':
            return {
                'message_id': 'msg_' + str(uuid.uuid4()),
                'status': 'sent',
                'delivery_time': datetime.now().isoformat()
            }
        elif operation == 'sync_data':
            return {
                'readings': [
                    {
                        'type': 'blood_pressure',
                        'systolic': 120,
                        'diastolic': 80,
                        'timestamp': datetime.now().isoformat()
                    }
                ]
            }
        else:
            return {'message': 'عملية غير مدعومة'}
    
    def _is_circuit_breaker_open(self, service_id: str) -> bool:
        """فحص حالة Circuit Breaker"""
        if service_id not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[service_id]
        
        # إذا كان مفتوحاً، فحص إذا كان الوقت قد حان لإعادة المحاولة
        if breaker['state'] == 'open':
            if datetime.now() > breaker['next_attempt']:
                breaker['state'] = 'half_open'
                return False
            return True
        
        return False
    
    def _update_circuit_breaker(self, service_id: str, success: bool):
        """تحديث حالة Circuit Breaker"""
        if service_id not in self.circuit_breakers:
            self.circuit_breakers[service_id] = {
                'state': 'closed',
                'failure_count': 0,
                'next_attempt': None
            }
        
        breaker = self.circuit_breakers[service_id]
        
        if success:
            breaker['failure_count'] = 0
            breaker['state'] = 'closed'
        else:
            breaker['failure_count'] += 1
            
            if breaker['failure_count'] >= self.integration_settings['circuit_breaker_threshold']:
                breaker['state'] = 'open'
                breaker['next_attempt'] = datetime.now() + timedelta(minutes=5)
    
    def _check_rate_limit(self, service_id: str) -> bool:
        """فحص حد الطلبات"""
        # في التطبيق الحقيقي، سيتم فحص عدد الطلبات في الساعة الماضية
        return True
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """الحصول على استجابة محفوظة"""
        if not self.integration_settings['enable_response_caching']:
            return None
        
        if cache_key in self.cached_responses:
            cached_item = self.cached_responses[cache_key]
            
            # فحص انتهاء الصلاحية
            if datetime.now() < cached_item['expires_at']:
                return cached_item['data']
            else:
                del self.cached_responses[cache_key]
        
        return None
    
    def _cache_response(self, cache_key: str, data: Dict):
        """حفظ الاستجابة في Cache"""
        if self.integration_settings['enable_response_caching']:
            expires_at = datetime.now() + timedelta(
                minutes=self.integration_settings['cache_duration_minutes']
            )
            
            self.cached_responses[cache_key] = {
                'data': data,
                'expires_at': expires_at
            }
    
    def _log_integration_operation(self, service_id: str, operation: str, 
                                 request_data: Dict, response: Dict, execution_time: float):
        """تسجيل عملية التكامل"""
        if not self.integration_settings['enable_request_logging']:
            return
        
        log_entry = IntegrationLog(
            log_id=str(uuid.uuid4()),
            service_id=service_id,
            operation=operation,
            request_data=request_data or {},
            response_data=response.get('data', {}),
            status_code=response.get('status_code', 0),
            success=response.get('success', False),
            error_message=response.get('error'),
            execution_time_ms=int(execution_time),
            timestamp=datetime.now()
        )
        
        if service_id not in self.integration_logs:
            self.integration_logs[service_id] = []
        
        self.integration_logs[service_id].append(log_entry)
        
        # الحفاظ على آخر 1000 سجل لكل خدمة
        if len(self.integration_logs[service_id]) > 1000:
            self.integration_logs[service_id] = self.integration_logs[service_id][-1000:]
    
    def _find_service_by_key(self, service_key: str) -> Optional[str]:
        """البحث عن الخدمة بالمفتاح"""
        for service_id, service in self.active_services.items():
            if service_key in service.name.lower() or service_key in service.endpoint_url:
                return service_id
        return None
    
    def _get_detailed_service_status(self, service: ExternalService) -> Dict:
        """الحصول على حالة مفصلة للخدمة"""
        # حساب إحصائيات الخدمة
        service_logs = self.integration_logs.get(service.service_id, [])
        recent_logs = [
            log for log in service_logs 
            if log.timestamp >= datetime.now() - timedelta(hours=24)
        ]
        
        success_rate = 0
        avg_response_time = 0
        
        if recent_logs:
            successful_logs = [log for log in recent_logs if log.success]
            success_rate = (len(successful_logs) / len(recent_logs)) * 100
            avg_response_time = sum(log.execution_time_ms for log in recent_logs) / len(recent_logs)
        
        return {
            'service_id': service.service_id,
            'name': service.name,
            'type': service.type,
            'status': service.status,
            'last_sync': service.last_sync.isoformat() if service.last_sync else None,
            'success_rate_24h': success_rate,
            'avg_response_time_ms': avg_response_time,
            'total_requests_24h': len(recent_logs),
            'endpoint_url': service.endpoint_url,
            'data_format': service.data_format
        }
    
    # دوال تحويل البيانات
    def _normalize_appointment_data(self, raw_data: Dict, hospital_id: str) -> List[Dict]:
        """تحويل بيانات المواعيد للتنسيق الموحد"""
        appointments = raw_data.get('appointments', [])
        normalized = []
        
        for apt in appointments:
            normalized.append({
                'id': apt.get('id'),
                'doctor_name': apt.get('doctor_name'),
                'specialty': apt.get('specialty'),
                'date': apt.get('date'),
                'time': apt.get('time'),
                'status': apt.get('status'),
                'hospital_id': hospital_id,
                'location': apt.get('location', ''),
                'notes': apt.get('notes', '')
            })
        
        return normalized
    
    def _normalize_pharmacy_data(self, raw_data: Dict, pharmacy_key: str) -> Dict:
        """تحويل بيانات الصيدلية للتنسيق الموحد"""
        return {
            'pharmacy_name': raw_data.get('pharmacy_name'),
            'available': raw_data.get('available', False),
            'price': raw_data.get('price'),
            'address': raw_data.get('address'),
            'phone': raw_data.get('phone'),
            'pharmacy_key': pharmacy_key,
            'last_updated': datetime.now().isoformat()
        }
    
    def _normalize_insurance_data(self, raw_data: Dict) -> Dict:
        """تحويل بيانات التأمين للتنسيق الموحد"""
        return {
            'covered': raw_data.get('covered', False),
            'coverage_percentage': raw_data.get('coverage_percentage', 0),
            'copay_amount': raw_data.get('copay_amount', 0),
            'authorization_required': raw_data.get('authorization_required', False),
            'policy_number': raw_data.get('policy_number'),
            'expiry_date': raw_data.get('expiry_date'),
            'notes': raw_data.get('notes', '')
        }
    
    def _normalize_lab_data(self, raw_data: Dict, lab_name: str) -> List[Dict]:
        """تحويل بيانات المختبر للتنسيق الموحد"""
        tests = raw_data.get('tests', [])
        normalized = []
        
        for test in tests:
            normalized.append({
                'test_name': test.get('test_name'),
                'date': test.get('date'),
                'results': test.get('results', {}),
                'status': test.get('status'),
                'reference_ranges': test.get('reference_ranges', {}),
                'lab_name': lab_name,
                'doctor_notes': test.get('doctor_notes', ''),
                'report_url': test.get('report_url')
            })
        
        return normalized
    
    def _normalize_payment_data(self, raw_data: Dict, gateway: str) -> Dict:
        """تحويل بيانات الدفع للتنسيق الموحد"""
        return {
            'payment_id': raw_data.get('payment_id'),
            'payment_url': raw_data.get('payment_url'),
            'status': raw_data.get('status'),
            'gateway': gateway,
            'transaction_id': raw_data.get('transaction_id'),
            'created_at': datetime.now().isoformat()
        }
    
    def _normalize_device_data(self, raw_data: Dict, device_type: str) -> List[Dict]:
        """تحويل بيانات الأجهزة للتنسيق الموحد"""
        readings = raw_data.get('readings', [])
        normalized = []
        
        for reading in readings:
            normalized.append({
                'type': reading.get('type'),
                'value': reading.get('value'),
                'unit': reading.get('unit'),
                'timestamp': reading.get('timestamp'),
                'device_type': device_type,
                'device_id': reading.get('device_id'),
                'notes': reading.get('notes', '')
            })
        
        return normalized

