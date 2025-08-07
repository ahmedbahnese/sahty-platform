"""
خدمة بنك الدم المتقدمة مع إدارة التبرع والطلبات
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class BloodType(Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class DonationStatus(Enum):
    SCHEDULED = "مجدول"
    COMPLETED = "مكتمل"
    CANCELLED = "ملغي"
    IN_PROGRESS = "جاري"

class BloodComponentType(Enum):
    WHOLE_BLOOD = "دم كامل"
    RED_CELLS = "كريات حمراء"
    PLATELETS = "صفائح دموية"
    PLASMA = "بلازما"
    CRYOPRECIPITATE = "مركز التجلط"

@dataclass
class BloodUnit:
    unit_id: str
    blood_type: str
    component_type: str
    volume: float
    collection_date: datetime
    expiry_date: datetime
    donor_id: str
    status: str
    location: str

class BloodBankService:
    def __init__(self):
        """تهيئة خدمة بنك الدم"""
        
        # مراكز التبرع بالدم في مصر
        self.blood_centers = [
            {
                'center_id': 1,
                'name': 'بنك الدم المركزي - القاهرة',
                'address': 'شارع قصر العيني، القاهرة',
                'phone': '0225555555',
                'email': 'cairo.bloodbank@health.gov.eg',
                'working_hours': '8:00 AM - 8:00 PM',
                'services': ['تبرع', 'فحوصات', 'طوارئ'],
                'lat': 30.0444,
                'lng': 31.2357,
                'capacity': 1000,
                'current_stock': 750
            },
            {
                'center_id': 2,
                'name': 'بنك الدم - الإسكندرية',
                'address': 'شارع الحرية، الإسكندرية',
                'phone': '0334444444',
                'email': 'alex.bloodbank@health.gov.eg',
                'working_hours': '8:00 AM - 6:00 PM',
                'services': ['تبرع', 'فحوصات'],
                'lat': 31.2001,
                'lng': 29.9187,
                'capacity': 500,
                'current_stock': 320
            },
            {
                'center_id': 3,
                'name': 'بنك الدم - الجيزة',
                'address': 'شارع الهرم، الجيزة',
                'phone': '0233333333',
                'email': 'giza.bloodbank@health.gov.eg',
                'working_hours': '9:00 AM - 7:00 PM',
                'services': ['تبرع', 'طوارئ'],
                'lat': 30.0131,
                'lng': 31.2089,
                'capacity': 300,
                'current_stock': 180
            }
        ]
        
        # جدول توافق فصائل الدم
        self.compatibility_matrix = {
            BloodType.O_NEGATIVE.value: [bt.value for bt in BloodType],  # المتبرع العام
            BloodType.O_POSITIVE.value: [BloodType.O_POSITIVE.value, BloodType.A_POSITIVE.value, 
                                       BloodType.B_POSITIVE.value, BloodType.AB_POSITIVE.value],
            BloodType.A_NEGATIVE.value: [BloodType.A_NEGATIVE.value, BloodType.A_POSITIVE.value,
                                       BloodType.AB_NEGATIVE.value, BloodType.AB_POSITIVE.value],
            BloodType.A_POSITIVE.value: [BloodType.A_POSITIVE.value, BloodType.AB_POSITIVE.value],
            BloodType.B_NEGATIVE.value: [BloodType.B_NEGATIVE.value, BloodType.B_POSITIVE.value,
                                       BloodType.AB_NEGATIVE.value, BloodType.AB_POSITIVE.value],
            BloodType.B_POSITIVE.value: [BloodType.B_POSITIVE.value, BloodType.AB_POSITIVE.value],
            BloodType.AB_NEGATIVE.value: [BloodType.AB_NEGATIVE.value, BloodType.AB_POSITIVE.value],
            BloodType.AB_POSITIVE.value: [BloodType.AB_POSITIVE.value]  # المستقبل العام
        }
        
        # متطلبات التبرع
        self.donation_requirements = {
            'min_age': 18,
            'max_age': 65,
            'min_weight': 50,  # كيلوجرام
            'min_hemoglobin_male': 13.5,  # جم/دل
            'min_hemoglobin_female': 12.5,  # جم/دل
            'min_interval_days': 56,  # بين التبرعات
            'max_donations_per_year': 6
        }
    
    def register_donor(self, donor_info: Dict) -> Dict:
        """
        تسجيل متبرع جديد
        
        Args:
            donor_info: معلومات المتبرع
            
        Returns:
            Dict: نتيجة التسجيل
        """
        try:
            donor_id = str(uuid.uuid4())
            
            # التحقق من صحة البيانات
            validation_result = self._validate_donor_eligibility(donor_info)
            if not validation_result['eligible']:
                return {
                    'success': False,
                    'error': validation_result['reason']
                }
            
            # إنشاء ملف المتبرع
            donor_profile = {
                'donor_id': donor_id,
                'personal_info': {
                    'name': donor_info['name'],
                    'national_id': donor_info['national_id'],
                    'phone': donor_info['phone'],
                    'email': donor_info.get('email', ''),
                    'date_of_birth': donor_info['date_of_birth'],
                    'gender': donor_info['gender'],
                    'address': donor_info['address']
                },
                'medical_info': {
                    'blood_type': donor_info['blood_type'],
                    'weight': donor_info['weight'],
                    'height': donor_info.get('height', 0),
                    'medical_conditions': donor_info.get('medical_conditions', []),
                    'medications': donor_info.get('medications', []),
                    'allergies': donor_info.get('allergies', [])
                },
                'donation_history': [],
                'status': 'active',
                'registration_date': datetime.now().isoformat(),
                'last_donation_date': None,
                'total_donations': 0,
                'points_earned': 0,
                'preferred_center': donor_info.get('preferred_center'),
                'emergency_contact': donor_info.get('emergency_contact', {})
            }
            
            return {
                'success': True,
                'donor_profile': donor_profile,
                'message': 'تم تسجيل المتبرع بنجاح'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تسجيل المتبرع: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_donor_eligibility(self, donor_info: Dict) -> Dict:
        """التحقق من أهلية المتبرع"""
        # حساب العمر
        birth_date = datetime.fromisoformat(donor_info['date_of_birth'])
        age = (datetime.now() - birth_date).days // 365
        
        # فحص العمر
        if age < self.donation_requirements['min_age']:
            return {'eligible': False, 'reason': f'العمر أقل من {self.donation_requirements["min_age"]} سنة'}
        
        if age > self.donation_requirements['max_age']:
            return {'eligible': False, 'reason': f'العمر أكبر من {self.donation_requirements["max_age"]} سنة'}
        
        # فحص الوزن
        if donor_info['weight'] < self.donation_requirements['min_weight']:
            return {'eligible': False, 'reason': f'الوزن أقل من {self.donation_requirements["min_weight"]} كيلوجرام'}
        
        # فحص الحالات المرضية المانعة
        prohibited_conditions = ['hepatitis', 'hiv', 'heart_disease', 'cancer']
        medical_conditions = [condition.lower() for condition in donor_info.get('medical_conditions', [])]
        
        for condition in prohibited_conditions:
            if condition in medical_conditions:
                return {'eligible': False, 'reason': f'وجود حالة مرضية مانعة: {condition}'}
        
        return {'eligible': True, 'reason': 'مؤهل للتبرع'}
    
    def schedule_donation(self, donor_id: str, center_id: int, 
                         preferred_date: str, preferred_time: str) -> Dict:
        """
        جدولة موعد تبرع
        
        Args:
            donor_id: معرف المتبرع
            center_id: معرف المركز
            preferred_date: التاريخ المفضل
            preferred_time: الوقت المفضل
            
        Returns:
            Dict: تفاصيل الموعد
        """
        try:
            appointment_id = str(uuid.uuid4())
            
            # التحقق من توفر الموعد
            availability = self._check_appointment_availability(
                center_id, preferred_date, preferred_time
            )
            
            if not availability['available']:
                return {
                    'success': False,
                    'error': 'الموعد غير متاح',
                    'alternative_slots': availability['alternative_slots']
                }
            
            # التحقق من أهلية المتبرع للتبرع في هذا التاريخ
            eligibility = self._check_donation_eligibility(donor_id, preferred_date)
            if not eligibility['eligible']:
                return {
                    'success': False,
                    'error': eligibility['reason']
                }
            
            # إنشاء الموعد
            appointment = {
                'appointment_id': appointment_id,
                'donor_id': donor_id,
                'center_id': center_id,
                'date': preferred_date,
                'time': preferred_time,
                'status': DonationStatus.SCHEDULED.value,
                'created_at': datetime.now().isoformat(),
                'estimated_duration': 60,  # دقيقة
                'pre_donation_tests': [
                    'فحص الهيموجلوبين',
                    'قياس ضغط الدم',
                    'قياس النبض',
                    'فحص درجة الحرارة'
                ],
                'instructions': [
                    'تناول وجبة جيدة قبل التبرع',
                    'شرب كمية كافية من الماء',
                    'تجنب التدخين قبل التبرع بساعتين',
                    'إحضار بطاقة الهوية'
                ],
                'reminder_sent': False
            }
            
            return {
                'success': True,
                'appointment': appointment,
                'message': 'تم حجز الموعد بنجاح'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_appointment_availability(self, center_id: int, date: str, time: str) -> Dict:
        """فحص توفر الموعد"""
        # في التطبيق الحقيقي، سيتم فحص قاعدة البيانات
        # هنا محاكاة للتوفر
        
        # محاكاة مواعيد بديلة
        alternative_slots = [
            {'date': date, 'time': '10:00'},
            {'date': date, 'time': '14:00'},
            {'date': (datetime.fromisoformat(date) + timedelta(days=1)).date().isoformat(), 'time': time}
        ]
        
        return {
            'available': True,  # افتراض التوفر
            'alternative_slots': alternative_slots
        }
    
    def _check_donation_eligibility(self, donor_id: str, donation_date: str) -> Dict:
        """فحص أهلية المتبرع للتبرع في تاريخ معين"""
        # في التطبيق الحقيقي، سيتم فحص آخر تبرع من قاعدة البيانات
        # هنا محاكاة للفحص
        
        # افتراض آخر تبرع كان منذ 60 يوم
        last_donation_date = datetime.now() - timedelta(days=60)
        donation_date_obj = datetime.fromisoformat(donation_date)
        
        days_since_last = (donation_date_obj - last_donation_date).days
        
        if days_since_last < self.donation_requirements['min_interval_days']:
            return {
                'eligible': False,
                'reason': f'يجب الانتظار {self.donation_requirements["min_interval_days"] - days_since_last} يوم إضافي'
            }
        
        return {'eligible': True, 'reason': 'مؤهل للتبرع'}
    
    def process_donation(self, appointment_id: str, donation_data: Dict) -> Dict:
        """
        معالجة عملية التبرع
        
        Args:
            appointment_id: معرف الموعد
            donation_data: بيانات التبرع
            
        Returns:
            Dict: نتيجة التبرع
        """
        try:
            donation_id = str(uuid.uuid4())
            
            # فحوصات ما قبل التبرع
            pre_tests = self._perform_pre_donation_tests(donation_data)
            if not pre_tests['passed']:
                return {
                    'success': False,
                    'error': 'فشل في الفحوصات الأولية',
                    'test_results': pre_tests
                }
            
            # معالجة التبرع
            collection_time = datetime.now()
            
            # تحديد نوع المكون المتبرع به
            component_type = donation_data.get('component_type', BloodComponentType.WHOLE_BLOOD.value)
            volume = donation_data.get('volume', 450)  # مل
            
            # حساب تاريخ انتهاء الصلاحية
            expiry_date = self._calculate_expiry_date(component_type, collection_time)
            
            # إنشاء وحدة الدم
            blood_unit = BloodUnit(
                unit_id=str(uuid.uuid4()),
                blood_type=donation_data['blood_type'],
                component_type=component_type,
                volume=volume,
                collection_date=collection_time,
                expiry_date=expiry_date,
                donor_id=donation_data['donor_id'],
                status='available',
                location=f"center_{donation_data['center_id']}"
            )
            
            # سجل التبرع
            donation_record = {
                'donation_id': donation_id,
                'appointment_id': appointment_id,
                'donor_id': donation_data['donor_id'],
                'center_id': donation_data['center_id'],
                'blood_unit': blood_unit.__dict__,
                'pre_tests': pre_tests,
                'collection_time': collection_time.isoformat(),
                'staff_id': donation_data.get('staff_id'),
                'notes': donation_data.get('notes', ''),
                'adverse_reactions': [],
                'post_donation_care': {
                    'rest_time': 15,  # دقيقة
                    'refreshments_provided': True,
                    'instructions_given': True
                },
                'status': DonationStatus.COMPLETED.value
            }
            
            # تحديث نقاط المتبرع
            points_earned = self._calculate_donation_points(component_type, volume)
            
            return {
                'success': True,
                'donation_record': donation_record,
                'blood_unit': blood_unit.__dict__,
                'points_earned': points_earned,
                'message': 'تم التبرع بنجاح'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _perform_pre_donation_tests(self, donation_data: Dict) -> Dict:
        """إجراء فحوصات ما قبل التبرع"""
        tests = {
            'hemoglobin': {
                'value': donation_data.get('hemoglobin', 14.0),
                'normal_range': {'min': 12.5, 'max': 18.0},
                'passed': True
            },
            'blood_pressure': {
                'systolic': donation_data.get('systolic_bp', 120),
                'diastolic': donation_data.get('diastolic_bp', 80),
                'normal_range': {'systolic': {'min': 90, 'max': 180}, 'diastolic': {'min': 50, 'max': 100}},
                'passed': True
            },
            'pulse': {
                'value': donation_data.get('pulse', 72),
                'normal_range': {'min': 50, 'max': 100},
                'passed': True
            },
            'temperature': {
                'value': donation_data.get('temperature', 36.8),
                'normal_range': {'min': 36.1, 'max': 37.2},
                'passed': True
            }
        }
        
        # فحص النتائج
        all_passed = all(test['passed'] for test in tests.values())
        
        return {
            'passed': all_passed,
            'tests': tests,
            'conducted_by': donation_data.get('nurse_id'),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_expiry_date(self, component_type: str, collection_date: datetime) -> datetime:
        """حساب تاريخ انتهاء صلاحية مكونات الدم"""
        expiry_days = {
            BloodComponentType.WHOLE_BLOOD.value: 35,
            BloodComponentType.RED_CELLS.value: 42,
            BloodComponentType.PLATELETS.value: 5,
            BloodComponentType.PLASMA.value: 365,
            BloodComponentType.CRYOPRECIPITATE.value: 365
        }
        
        days = expiry_days.get(component_type, 35)
        return collection_date + timedelta(days=days)
    
    def _calculate_donation_points(self, component_type: str, volume: float) -> int:
        """حساب نقاط التبرع"""
        base_points = {
            BloodComponentType.WHOLE_BLOOD.value: 100,
            BloodComponentType.RED_CELLS.value: 80,
            BloodComponentType.PLATELETS.value: 150,
            BloodComponentType.PLASMA.value: 60,
            BloodComponentType.CRYOPRECIPITATE.value: 120
        }
        
        points = base_points.get(component_type, 100)
        
        # مكافأة إضافية للحجم الكبير
        if volume > 450:
            points += 20
        
        return points
    
    def search_blood_availability(self, blood_type: str, component_type: str = None,
                                 location: str = None, urgency: str = 'normal') -> Dict:
        """
        البحث عن توفر الدم
        
        Args:
            blood_type: فصيلة الدم المطلوبة
            component_type: نوع المكون
            location: الموقع
            urgency: مستوى الإلحاح
            
        Returns:
            Dict: نتائج البحث
        """
        try:
            # البحث في المخزون
            available_units = self._search_inventory(blood_type, component_type, location)
            
            # فحص التوافق
            compatible_types = self._get_compatible_blood_types(blood_type)
            
            # البحث في الأنواع المتوافقة إذا لم توجد الفصيلة المطلوبة
            if not available_units:
                for compatible_type in compatible_types:
                    compatible_units = self._search_inventory(compatible_type, component_type, location)
                    available_units.extend(compatible_units)
            
            # ترتيب النتائج حسب الأولوية
            sorted_units = self._prioritize_blood_units(available_units, blood_type, urgency)
            
            # إحصائيات التوفر
            availability_stats = {
                'total_units': len(sorted_units),
                'exact_match': len([u for u in sorted_units if u['blood_type'] == blood_type]),
                'compatible_units': len([u for u in sorted_units if u['blood_type'] != blood_type]),
                'centers_with_stock': len(set(u['location'] for u in sorted_units))
            }
            
            return {
                'success': True,
                'available_units': sorted_units,
                'availability_stats': availability_stats,
                'compatible_types': compatible_types,
                'search_criteria': {
                    'blood_type': blood_type,
                    'component_type': component_type,
                    'location': location,
                    'urgency': urgency
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _search_inventory(self, blood_type: str, component_type: str = None, location: str = None) -> List[Dict]:
        """البحث في مخزون الدم"""
        # في التطبيق الحقيقي، سيتم البحث في قاعدة البيانات
        # هنا محاكاة للمخزون
        
        mock_inventory = [
            {
                'unit_id': str(uuid.uuid4()),
                'blood_type': 'O+',
                'component_type': 'دم كامل',
                'volume': 450,
                'collection_date': '2024-01-10T10:00:00',
                'expiry_date': '2024-02-14T10:00:00',
                'location': 'center_1',
                'status': 'available'
            },
            {
                'unit_id': str(uuid.uuid4()),
                'blood_type': 'A+',
                'component_type': 'كريات حمراء',
                'volume': 300,
                'collection_date': '2024-01-12T14:00:00',
                'expiry_date': '2024-02-23T14:00:00',
                'location': 'center_1',
                'status': 'available'
            },
            {
                'unit_id': str(uuid.uuid4()),
                'blood_type': 'B+',
                'component_type': 'صفائح دموية',
                'volume': 200,
                'collection_date': '2024-01-14T09:00:00',
                'expiry_date': '2024-01-19T09:00:00',
                'location': 'center_2',
                'status': 'available'
            }
        ]
        
        # فلترة النتائج
        filtered_units = []
        for unit in mock_inventory:
            if blood_type and unit['blood_type'] != blood_type:
                continue
            if component_type and unit['component_type'] != component_type:
                continue
            if location and unit['location'] != location:
                continue
            
            filtered_units.append(unit)
        
        return filtered_units
    
    def _get_compatible_blood_types(self, blood_type: str) -> List[str]:
        """الحصول على فصائل الدم المتوافقة"""
        # البحث عن المتبرعين المتوافقين
        compatible_donors = []
        for donor_type, recipients in self.compatibility_matrix.items():
            if blood_type in recipients:
                compatible_donors.append(donor_type)
        
        return compatible_donors
    
    def _prioritize_blood_units(self, units: List[Dict], requested_type: str, urgency: str) -> List[Dict]:
        """ترتيب وحدات الدم حسب الأولوية"""
        def priority_score(unit):
            score = 0
            
            # أولوية للفصيلة المطابقة تماماً
            if unit['blood_type'] == requested_type:
                score += 100
            
            # أولوية للوحدات الأحدث
            collection_date = datetime.fromisoformat(unit['collection_date'])
            days_old = (datetime.now() - collection_date).days
            score += max(0, 30 - days_old)
            
            # أولوية للحجم الأكبر
            score += unit['volume'] / 10
            
            # أولوية إضافية للحالات العاجلة
            if urgency == 'emergency':
                score += 50
            
            return score
        
        return sorted(units, key=priority_score, reverse=True)
    
    def create_blood_request(self, hospital_id: str, patient_info: Dict, 
                           blood_requirements: Dict) -> Dict:
        """
        إنشاء طلب دم
        
        Args:
            hospital_id: معرف المستشفى
            patient_info: معلومات المريض
            blood_requirements: متطلبات الدم
            
        Returns:
            Dict: تفاصيل الطلب
        """
        try:
            request_id = str(uuid.uuid4())
            
            # التحقق من توفر الدم
            availability = self.search_blood_availability(
                blood_type=blood_requirements['blood_type'],
                component_type=blood_requirements.get('component_type'),
                urgency=blood_requirements.get('urgency', 'normal')
            )
            
            # إنشاء الطلب
            blood_request = {
                'request_id': request_id,
                'hospital_id': hospital_id,
                'patient_info': {
                    'name': patient_info['name'],
                    'national_id': patient_info.get('national_id'),
                    'age': patient_info['age'],
                    'gender': patient_info['gender'],
                    'blood_type': patient_info['blood_type'],
                    'medical_condition': patient_info.get('medical_condition')
                },
                'blood_requirements': blood_requirements,
                'availability_check': availability,
                'status': 'pending',
                'priority': blood_requirements.get('urgency', 'normal'),
                'created_at': datetime.now().isoformat(),
                'required_by': blood_requirements.get('required_by'),
                'estimated_fulfillment': self._estimate_fulfillment_time(availability, blood_requirements),
                'assigned_units': [],
                'total_cost': 0.0
            }
            
            # تخصيص الوحدات إذا كانت متوفرة
            if availability['success'] and availability['available_units']:
                assignment_result = self._assign_blood_units(request_id, availability['available_units'], blood_requirements)
                blood_request.update(assignment_result)
            
            return {
                'success': True,
                'blood_request': blood_request
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _estimate_fulfillment_time(self, availability: Dict, requirements: Dict) -> str:
        """تقدير وقت تلبية الطلب"""
        if availability['success'] and availability['available_units']:
            urgency = requirements.get('urgency', 'normal')
            if urgency == 'emergency':
                return '30 دقيقة'
            elif urgency == 'urgent':
                return '2 ساعة'
            else:
                return '24 ساعة'
        else:
            return '48-72 ساعة'  # يحتاج لتبرعات جديدة
    
    def _assign_blood_units(self, request_id: str, available_units: List[Dict], requirements: Dict) -> Dict:
        """تخصيص وحدات الدم للطلب"""
        required_volume = requirements.get('volume', 450)
        assigned_units = []
        total_volume = 0
        total_cost = 0
        
        # تخصيص الوحدات حسب الحاجة
        for unit in available_units:
            if total_volume >= required_volume:
                break
            
            assigned_units.append({
                'unit_id': unit['unit_id'],
                'blood_type': unit['blood_type'],
                'component_type': unit['component_type'],
                'volume': unit['volume'],
                'cost': 200.0,  # تكلفة وهمية
                'reserved_at': datetime.now().isoformat()
            })
            
            total_volume += unit['volume']
            total_cost += 200.0
        
        return {
            'assigned_units': assigned_units,
            'total_volume': total_volume,
            'total_cost': total_cost,
            'status': 'assigned' if total_volume >= required_volume else 'partial'
        }
    
    def get_donor_dashboard(self, donor_id: str) -> Dict:
        """الحصول على لوحة تحكم المتبرع"""
        try:
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            dashboard = {
                'donor_id': donor_id,
                'personal_stats': {
                    'total_donations': 8,
                    'total_volume': 3600,  # مل
                    'points_balance': 850,
                    'donor_level': 'ذهبي',
                    'next_eligible_date': (datetime.now() + timedelta(days=45)).date().isoformat()
                },
                'recent_donations': [
                    {
                        'date': '2024-01-01',
                        'center': 'بنك الدم المركزي - القاهرة',
                        'component': 'دم كامل',
                        'volume': 450,
                        'points_earned': 100
                    }
                ],
                'upcoming_appointments': [
                    {
                        'date': '2024-03-01',
                        'time': '10:00',
                        'center': 'بنك الدم المركزي - القاهرة'
                    }
                ],
                'health_status': {
                    'last_checkup': '2024-01-01',
                    'hemoglobin': 14.2,
                    'blood_pressure': '120/80',
                    'overall_health': 'ممتاز'
                },
                'achievements': [
                    {'title': 'متبرع منتظم', 'earned_date': '2023-12-01'},
                    {'title': 'منقذ الأرواح', 'earned_date': '2023-10-15'}
                ],
                'impact_statistics': {
                    'lives_potentially_saved': 24,  # كل تبرع ينقذ 3 أرواح
                    'hospitals_served': 5,
                    'emergency_donations': 2
                }
            }
            
            return {
                'success': True,
                'dashboard': dashboard
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_blood_center_info(self, center_id: int = None, location: Dict = None) -> Dict:
        """الحصول على معلومات مراكز التبرع"""
        try:
            if center_id:
                # البحث عن مركز محدد
                center = next((c for c in self.blood_centers if c['center_id'] == center_id), None)
                if not center:
                    return {'success': False, 'error': 'مركز غير موجود'}
                
                return {'success': True, 'center': center}
            
            # إرجاع جميع المراكز أو المراكز القريبة
            centers = self.blood_centers.copy()
            
            # إضافة معلومات إضافية لكل مركز
            for center in centers:
                center['current_needs'] = self._get_center_blood_needs(center['center_id'])
                center['donation_slots_available'] = self._get_available_slots(center['center_id'])
                
                # حساب المسافة إذا تم تحديد الموقع
                if location:
                    center['distance'] = self._calculate_distance(
                        location['lat'], location['lng'],
                        center['lat'], center['lng']
                    )
            
            # ترتيب حسب المسافة إذا تم تحديد الموقع
            if location:
                centers.sort(key=lambda x: x.get('distance', float('inf')))
            
            return {
                'success': True,
                'centers': centers,
                'total_centers': len(centers)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_center_blood_needs(self, center_id: int) -> Dict:
        """الحصول على احتياجات المركز من فصائل الدم"""
        # محاكاة الاحتياجات
        return {
            'O+': 'عالية',
            'O-': 'متوسطة',
            'A+': 'منخفضة',
            'A-': 'عالية',
            'B+': 'متوسطة',
            'B-': 'عالية',
            'AB+': 'منخفضة',
            'AB-': 'عالية'
        }
    
    def _get_available_slots(self, center_id: int) -> List[Dict]:
        """الحصول على المواعيد المتاحة"""
        # محاكاة المواعيد المتاحة
        slots = []
        for i in range(1, 8):  # الأسبوع القادم
            date = (datetime.now() + timedelta(days=i)).date()
            for hour in [9, 11, 14, 16]:
                slots.append({
                    'date': date.isoformat(),
                    'time': f'{hour:02d}:00',
                    'available': True
                })
        
        return slots[:10]  # أول 10 مواعيد
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """حساب المسافة بين نقطتين"""
        # استخدام معادلة Haversine المبسطة
        import math
        
        R = 6371  # نصف قطر الأرض بالكيلومتر
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) * math.sin(delta_lng / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return round(distance, 2)

