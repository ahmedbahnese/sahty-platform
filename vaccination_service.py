"""
خدمة التطعيمات وإدارة جدول التطعيمات
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class VaccineType(Enum):
    ROUTINE = "روتيني"
    TRAVEL = "سفر"
    OCCUPATIONAL = "مهني"
    EMERGENCY = "طوارئ"
    SEASONAL = "موسمي"

class VaccineStatus(Enum):
    SCHEDULED = "مجدول"
    COMPLETED = "مكتمل"
    MISSED = "فائت"
    CANCELLED = "ملغي"
    OVERDUE = "متأخر"

@dataclass
class VaccineRecord:
    record_id: str
    patient_id: str
    vaccine_name: str
    vaccine_type: str
    dose_number: int
    administered_date: datetime
    next_dose_date: Optional[datetime]
    administered_by: str
    location: str
    batch_number: str
    side_effects: List[str]

class VaccinationService:
    def __init__(self):
        """تهيئة خدمة التطعيمات"""
        
        # قاعدة بيانات التطعيمات المعتمدة في مصر
        self.vaccines_database = {
            # تطعيمات الأطفال الروتينية
            'bcg': {
                'name': 'لقاح السل (BCG)',
                'name_en': 'BCG',
                'type': VaccineType.ROUTINE.value,
                'target_age_groups': ['newborn'],
                'doses': [
                    {'dose_number': 1, 'age_months': 0, 'description': 'عند الولادة'}
                ],
                'protection_against': ['السل'],
                'side_effects': ['احمرار مكان الحقن', 'تورم خفيف'],
                'contraindications': ['نقص المناعة', 'الحمل'],
                'manufacturer': 'معهد المصل واللقاح',
                'storage_temp': '2-8°C'
            },
            'hepatitis_b': {
                'name': 'لقاح التهاب الكبد ب',
                'name_en': 'Hepatitis B',
                'type': VaccineType.ROUTINE.value,
                'target_age_groups': ['newborn', 'infant', 'adult'],
                'doses': [
                    {'dose_number': 1, 'age_months': 0, 'description': 'عند الولادة'},
                    {'dose_number': 2, 'age_months': 2, 'description': 'الشهر الثاني'},
                    {'dose_number': 3, 'age_months': 6, 'description': 'الشهر السادس'}
                ],
                'protection_against': ['التهاب الكبد الوبائي ب'],
                'side_effects': ['ألم مكان الحقن', 'حمى خفيفة'],
                'contraindications': ['حساسية شديدة للخميرة'],
                'manufacturer': 'GSK',
                'storage_temp': '2-8°C'
            },
            'polio': {
                'name': 'لقاح شلل الأطفال',
                'name_en': 'Polio (OPV/IPV)',
                'type': VaccineType.ROUTINE.value,
                'target_age_groups': ['infant', 'child'],
                'doses': [
                    {'dose_number': 1, 'age_months': 2, 'description': 'الشهر الثاني'},
                    {'dose_number': 2, 'age_months': 4, 'description': 'الشهر الرابع'},
                    {'dose_number': 3, 'age_months': 6, 'description': 'الشهر السادس'},
                    {'dose_number': 4, 'age_months': 18, 'description': 'الشهر الثامن عشر'}
                ],
                'protection_against': ['شلل الأطفال'],
                'side_effects': ['حمى خفيفة', 'إسهال نادر'],
                'contraindications': ['نقص المناعة الشديد'],
                'manufacturer': 'معهد المصل واللقاح',
                'storage_temp': '2-8°C'
            },
            'dtp': {
                'name': 'اللقاح الثلاثي (الدفتيريا والتيتانوس والسعال الديكي)',
                'name_en': 'DTP',
                'type': VaccineType.ROUTINE.value,
                'target_age_groups': ['infant', 'child'],
                'doses': [
                    {'dose_number': 1, 'age_months': 2, 'description': 'الشهر الثاني'},
                    {'dose_number': 2, 'age_months': 4, 'description': 'الشهر الرابع'},
                    {'dose_number': 3, 'age_months': 6, 'description': 'الشهر السادس'},
                    {'dose_number': 4, 'age_months': 18, 'description': 'الشهر الثامن عشر'}
                ],
                'protection_against': ['الدفتيريا', 'التيتانوس', 'السعال الديكي'],
                'side_effects': ['حمى', 'ألم مكان الحقن', 'هياج'],
                'contraindications': ['حمى شديدة', 'تشنجات سابقة'],
                'manufacturer': 'GSK',
                'storage_temp': '2-8°C'
            },
            'mmr': {
                'name': 'لقاح الحصبة والنكاف والحصبة الألمانية',
                'name_en': 'MMR',
                'type': VaccineType.ROUTINE.value,
                'target_age_groups': ['child'],
                'doses': [
                    {'dose_number': 1, 'age_months': 12, 'description': 'السنة الأولى'},
                    {'dose_number': 2, 'age_months': 18, 'description': 'الشهر الثامن عشر'}
                ],
                'protection_against': ['الحصبة', 'النكاف', 'الحصبة الألمانية'],
                'side_effects': ['حمى', 'طفح جلدي خفيف'],
                'contraindications': ['الحمل', 'نقص المناعة', 'حساسية الجيلاتين'],
                'manufacturer': 'Merck',
                'storage_temp': '2-8°C'
            },
            # تطعيمات البالغين
            'covid19': {
                'name': 'لقاح كوفيد-19',
                'name_en': 'COVID-19',
                'type': VaccineType.EMERGENCY.value,
                'target_age_groups': ['adult', 'elderly'],
                'doses': [
                    {'dose_number': 1, 'age_months': 216, 'description': 'الجرعة الأولى'},
                    {'dose_number': 2, 'age_months': 216, 'description': 'الجرعة الثانية بعد 3-4 أسابيع'},
                    {'dose_number': 3, 'age_months': 216, 'description': 'الجرعة المنشطة بعد 6 أشهر'}
                ],
                'protection_against': ['كوفيد-19'],
                'side_effects': ['ألم مكان الحقن', 'حمى', 'صداع', 'تعب'],
                'contraindications': ['حساسية شديدة لمكونات اللقاح'],
                'manufacturer': 'Pfizer/Sinovac/AstraZeneca',
                'storage_temp': '-70°C / 2-8°C'
            },
            'influenza': {
                'name': 'لقاح الإنفلونزا الموسمية',
                'name_en': 'Seasonal Influenza',
                'type': VaccineType.SEASONAL.value,
                'target_age_groups': ['child', 'adult', 'elderly'],
                'doses': [
                    {'dose_number': 1, 'age_months': 6, 'description': 'جرعة سنوية'}
                ],
                'protection_against': ['الإنفلونزا الموسمية'],
                'side_effects': ['ألم مكان الحقن', 'حمى خفيفة'],
                'contraindications': ['حساسية البيض الشديدة'],
                'manufacturer': 'Sanofi',
                'storage_temp': '2-8°C'
            },
            # تطعيمات السفر
            'yellow_fever': {
                'name': 'لقاح الحمى الصفراء',
                'name_en': 'Yellow Fever',
                'type': VaccineType.TRAVEL.value,
                'target_age_groups': ['adult'],
                'doses': [
                    {'dose_number': 1, 'age_months': 108, 'description': 'جرعة واحدة مدى الحياة'}
                ],
                'protection_against': ['الحمى الصفراء'],
                'side_effects': ['ألم مكان الحقن', 'حمى', 'صداع'],
                'contraindications': ['الحمل', 'نقص المناعة', 'حساسية البيض'],
                'manufacturer': 'Sanofi Pasteur',
                'storage_temp': '2-8°C',
                'required_for_countries': ['أفريقيا', 'أمريكا الجنوبية']
            },
            'meningitis': {
                'name': 'لقاح التهاب السحايا',
                'name_en': 'Meningococcal',
                'type': VaccineType.TRAVEL.value,
                'target_age_groups': ['adult'],
                'doses': [
                    {'dose_number': 1, 'age_months': 216, 'description': 'جرعة واحدة'}
                ],
                'protection_against': ['التهاب السحايا البكتيري'],
                'side_effects': ['ألم مكان الحقن', 'حمى'],
                'contraindications': ['حساسية شديدة'],
                'manufacturer': 'GSK',
                'storage_temp': '2-8°C',
                'required_for_countries': ['السعودية (الحج والعمرة)']
            }
        }
        
        # مراكز التطعيم المعتمدة
        self.vaccination_centers = [
            {
                'center_id': 1,
                'name': 'مركز التطعيمات - وزارة الصحة',
                'address': 'شارع قصر العيني، القاهرة',
                'phone': '0225555555',
                'working_hours': '8:00 AM - 4:00 PM',
                'available_vaccines': ['bcg', 'hepatitis_b', 'polio', 'dtp', 'mmr', 'covid19'],
                'appointment_required': True,
                'lat': 30.0444,
                'lng': 31.2357
            },
            {
                'center_id': 2,
                'name': 'مركز طب السفر - مطار القاهرة',
                'address': 'مطار القاهرة الدولي، الترمينال 3',
                'phone': '0226666666',
                'working_hours': '24/7',
                'available_vaccines': ['yellow_fever', 'meningitis', 'hepatitis_a', 'typhoid'],
                'appointment_required': False,
                'lat': 30.1219,
                'lng': 31.4056
            },
            {
                'center_id': 3,
                'name': 'مستشفى الأطفال - جامعة القاهرة',
                'address': 'شارع المنيل، القاهرة',
                'phone': '0223333333',
                'working_hours': '9:00 AM - 5:00 PM',
                'available_vaccines': ['bcg', 'hepatitis_b', 'polio', 'dtp', 'mmr'],
                'appointment_required': True,
                'lat': 30.0131,
                'lng': 31.2089
            }
        ]
        
        # جدول التطعيمات حسب العمر
        self.vaccination_schedule = {
            'newborn': {
                'age_range': '0-1 month',
                'vaccines': [
                    {'vaccine': 'bcg', 'timing': 'at_birth'},
                    {'vaccine': 'hepatitis_b', 'timing': 'at_birth'}
                ]
            },
            'infant_2m': {
                'age_range': '2 months',
                'vaccines': [
                    {'vaccine': 'hepatitis_b', 'dose': 2},
                    {'vaccine': 'polio', 'dose': 1},
                    {'vaccine': 'dtp', 'dose': 1}
                ]
            },
            'infant_4m': {
                'age_range': '4 months',
                'vaccines': [
                    {'vaccine': 'polio', 'dose': 2},
                    {'vaccine': 'dtp', 'dose': 2}
                ]
            },
            'infant_6m': {
                'age_range': '6 months',
                'vaccines': [
                    {'vaccine': 'hepatitis_b', 'dose': 3},
                    {'vaccine': 'polio', 'dose': 3},
                    {'vaccine': 'dtp', 'dose': 3}
                ]
            },
            'child_12m': {
                'age_range': '12 months',
                'vaccines': [
                    {'vaccine': 'mmr', 'dose': 1}
                ]
            },
            'child_18m': {
                'age_range': '18 months',
                'vaccines': [
                    {'vaccine': 'polio', 'dose': 4},
                    {'vaccine': 'dtp', 'dose': 4},
                    {'vaccine': 'mmr', 'dose': 2}
                ]
            }
        }
    
    def create_vaccination_schedule(self, patient_id: str, birth_date: str, 
                                  special_conditions: List[str] = None) -> Dict:
        """
        إنشاء جدول التطعيمات الشخصي
        
        Args:
            patient_id: معرف المريض
            birth_date: تاريخ الميلاد
            special_conditions: حالات خاصة
            
        Returns:
            Dict: جدول التطعيمات
        """
        try:
            birth_date_obj = datetime.fromisoformat(birth_date)
            current_age_months = self._calculate_age_months(birth_date_obj)
            
            # إنشاء الجدول الأساسي
            schedule = []
            schedule_id = str(uuid.uuid4())
            
            # تحديد التطعيمات المطلوبة حسب العمر
            for age_group, group_info in self.vaccination_schedule.items():
                vaccines_for_age = []
                
                for vaccine_info in group_info['vaccines']:
                    vaccine_code = vaccine_info['vaccine']
                    dose_number = vaccine_info.get('dose', 1)
                    
                    if vaccine_code in self.vaccines_database:
                        vaccine_data = self.vaccines_database[vaccine_code]
                        
                        # التحقق من موانع الاستعمال
                        if self._check_contraindications(vaccine_data, special_conditions):
                            continue
                        
                        # حساب تاريخ التطعيم المتوقع
                        target_age_months = vaccine_data['doses'][dose_number - 1]['age_months']
                        due_date = birth_date_obj + timedelta(days=target_age_months * 30)
                        
                        # تحديد الحالة
                        status = self._determine_vaccine_status(due_date, current_age_months, target_age_months)
                        
                        vaccine_entry = {
                            'vaccine_code': vaccine_code,
                            'vaccine_name': vaccine_data['name'],
                            'dose_number': dose_number,
                            'target_age_months': target_age_months,
                            'due_date': due_date.date().isoformat(),
                            'status': status,
                            'priority': self._calculate_priority(status, vaccine_data['type']),
                            'protection_against': vaccine_data['protection_against'],
                            'side_effects': vaccine_data['side_effects'],
                            'contraindications': vaccine_data['contraindications']
                        }
                        
                        vaccines_for_age.append(vaccine_entry)
                
                if vaccines_for_age:
                    schedule.append({
                        'age_group': age_group,
                        'age_range': group_info['age_range'],
                        'vaccines': vaccines_for_age
                    })
            
            # إضافة التطعيمات الموسمية والسفر إذا كان مناسباً
            if current_age_months >= 6:  # 6 أشهر فأكثر
                seasonal_vaccines = self._get_seasonal_vaccines(current_age_months)
                if seasonal_vaccines:
                    schedule.append({
                        'age_group': 'seasonal',
                        'age_range': 'حسب الموسم',
                        'vaccines': seasonal_vaccines
                    })
            
            vaccination_schedule = {
                'schedule_id': schedule_id,
                'patient_id': patient_id,
                'birth_date': birth_date,
                'current_age_months': current_age_months,
                'schedule': schedule,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'special_conditions': special_conditions or [],
                'next_due_vaccines': self._get_next_due_vaccines(schedule),
                'completion_rate': self._calculate_completion_rate(schedule)
            }
            
            return {
                'success': True,
                'vaccination_schedule': vaccination_schedule
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء جدول التطعيمات: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_age_months(self, birth_date: datetime) -> int:
        """حساب العمر بالأشهر"""
        today = datetime.now()
        months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
        return max(0, months)
    
    def _check_contraindications(self, vaccine_data: Dict, special_conditions: List[str]) -> bool:
        """فحص موانع الاستعمال"""
        if not special_conditions:
            return False
        
        contraindications = [c.lower() for c in vaccine_data.get('contraindications', [])]
        patient_conditions = [c.lower() for c in special_conditions]
        
        # فحص التداخل
        for condition in patient_conditions:
            for contraindication in contraindications:
                if condition in contraindication or contraindication in condition:
                    return True
        
        return False
    
    def _determine_vaccine_status(self, due_date: datetime, current_age_months: int, 
                                target_age_months: int) -> str:
        """تحديد حالة التطعيم"""
        today = datetime.now()
        
        if current_age_months < target_age_months:
            return VaccineStatus.SCHEDULED.value
        elif due_date.date() <= today.date():
            # فحص إذا كان متأخر أكثر من شهر
            if (today - due_date).days > 30:
                return VaccineStatus.OVERDUE.value
            else:
                return VaccineStatus.SCHEDULED.value
        else:
            return VaccineStatus.SCHEDULED.value
    
    def _calculate_priority(self, status: str, vaccine_type: str) -> str:
        """حساب أولوية التطعيم"""
        if status == VaccineStatus.OVERDUE.value:
            return 'عالية'
        elif vaccine_type == VaccineType.ROUTINE.value:
            return 'متوسطة'
        elif vaccine_type == VaccineType.EMERGENCY.value:
            return 'عالية'
        else:
            return 'منخفضة'
    
    def _get_seasonal_vaccines(self, age_months: int) -> List[Dict]:
        """الحصول على التطعيمات الموسمية"""
        seasonal_vaccines = []
        
        # لقاح الإنفلونزا للأطفال فوق 6 أشهر
        if age_months >= 6:
            influenza_data = self.vaccines_database['influenza']
            seasonal_vaccines.append({
                'vaccine_code': 'influenza',
                'vaccine_name': influenza_data['name'],
                'dose_number': 1,
                'target_age_months': age_months,
                'due_date': self._get_next_flu_season().isoformat(),
                'status': VaccineStatus.SCHEDULED.value,
                'priority': 'متوسطة',
                'protection_against': influenza_data['protection_against'],
                'side_effects': influenza_data['side_effects'],
                'contraindications': influenza_data['contraindications']
            })
        
        return seasonal_vaccines
    
    def _get_next_flu_season(self) -> datetime:
        """الحصول على موعد موسم الإنفلونزا القادم"""
        today = datetime.now()
        # موسم الإنفلونزا عادة من أكتوبر إلى مارس
        if today.month >= 10:
            return datetime(today.year, 10, 1)
        else:
            return datetime(today.year, 10, 1)
    
    def _get_next_due_vaccines(self, schedule: List[Dict]) -> List[Dict]:
        """الحصول على التطعيمات المستحقة التالية"""
        next_vaccines = []
        today = datetime.now().date()
        
        for age_group in schedule:
            for vaccine in age_group['vaccines']:
                due_date = datetime.fromisoformat(vaccine['due_date']).date()
                if (vaccine['status'] in [VaccineStatus.SCHEDULED.value, VaccineStatus.OVERDUE.value] and
                    due_date <= today + timedelta(days=30)):  # خلال الشهر القادم
                    next_vaccines.append(vaccine)
        
        # ترتيب حسب الأولوية والتاريخ
        next_vaccines.sort(key=lambda x: (
            0 if x['priority'] == 'عالية' else 1 if x['priority'] == 'متوسطة' else 2,
            x['due_date']
        ))
        
        return next_vaccines[:5]  # أول 5 تطعيمات
    
    def _calculate_completion_rate(self, schedule: List[Dict]) -> float:
        """حساب معدل إكمال التطعيمات"""
        total_vaccines = 0
        completed_vaccines = 0
        
        for age_group in schedule:
            for vaccine in age_group['vaccines']:
                total_vaccines += 1
                if vaccine['status'] == VaccineStatus.COMPLETED.value:
                    completed_vaccines += 1
        
        if total_vaccines == 0:
            return 0.0
        
        return round((completed_vaccines / total_vaccines) * 100, 1)
    
    def book_vaccination_appointment(self, patient_id: str, vaccine_code: str,
                                   center_id: int, preferred_date: str,
                                   preferred_time: str) -> Dict:
        """
        حجز موعد تطعيم
        
        Args:
            patient_id: معرف المريض
            vaccine_code: رمز التطعيم
            center_id: معرف المركز
            preferred_date: التاريخ المفضل
            preferred_time: الوقت المفضل
            
        Returns:
            Dict: تفاصيل الموعد
        """
        try:
            # التحقق من وجود التطعيم
            if vaccine_code not in self.vaccines_database:
                return {
                    'success': False,
                    'error': 'تطعيم غير موجود'
                }
            
            # التحقق من وجود المركز
            center = next((c for c in self.vaccination_centers 
                         if c['center_id'] == center_id), None)
            if not center:
                return {
                    'success': False,
                    'error': 'مركز غير موجود'
                }
            
            # التحقق من توفر التطعيم في المركز
            if vaccine_code not in center['available_vaccines']:
                return {
                    'success': False,
                    'error': 'التطعيم غير متوفر في هذا المركز'
                }
            
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
            
            # إنشاء الموعد
            appointment_id = str(uuid.uuid4())
            vaccine_data = self.vaccines_database[vaccine_code]
            
            appointment = {
                'appointment_id': appointment_id,
                'patient_id': patient_id,
                'vaccine_code': vaccine_code,
                'vaccine_name': vaccine_data['name'],
                'center_id': center_id,
                'center_name': center['name'],
                'center_address': center['address'],
                'date': preferred_date,
                'time': preferred_time,
                'status': 'confirmed',
                'created_at': datetime.now().isoformat(),
                'estimated_duration': 30,  # دقيقة
                'preparation_instructions': [
                    'إحضار بطاقة الهوية وكارت التطعيمات',
                    'إبلاغ الطبيب عن أي حساسية',
                    'تجنب الأدوية المثبطة للمناعة',
                    'الحضور قبل الموعد بـ 15 دقيقة'
                ],
                'post_vaccination_care': [
                    'البقاء في المركز لمدة 15 دقيقة للمراقبة',
                    'تجنب الأنشطة الشاقة لمدة 24 ساعة',
                    'وضع كمادات باردة على مكان الحقن إذا لزم الأمر',
                    'مراقبة أي أعراض جانبية'
                ],
                'emergency_contact': center['phone'],
                'cost': 0  # التطعيمات الروتينية مجانية في مصر
            }
            
            return {
                'success': True,
                'appointment': appointment,
                'vaccine_info': vaccine_data
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
        
        alternative_slots = [
            {'date': date, 'time': '09:00'},
            {'date': date, 'time': '11:00'},
            {'date': date, 'time': '14:00'},
            {'date': (datetime.fromisoformat(date) + timedelta(days=1)).date().isoformat(), 'time': time}
        ]
        
        return {
            'available': True,  # افتراض التوفر
            'alternative_slots': alternative_slots
        }
    
    def record_vaccination(self, appointment_id: str, vaccination_data: Dict) -> Dict:
        """
        تسجيل التطعيم المكتمل
        
        Args:
            appointment_id: معرف الموعد
            vaccination_data: بيانات التطعيم
            
        Returns:
            Dict: سجل التطعيم
        """
        try:
            record_id = str(uuid.uuid4())
            
            # إنشاء سجل التطعيم
            vaccination_record = VaccineRecord(
                record_id=record_id,
                patient_id=vaccination_data['patient_id'],
                vaccine_name=vaccination_data['vaccine_name'],
                vaccine_type=vaccination_data['vaccine_type'],
                dose_number=vaccination_data.get('dose_number', 1),
                administered_date=datetime.now(),
                next_dose_date=self._calculate_next_dose_date(
                    vaccination_data['vaccine_code'], 
                    vaccination_data.get('dose_number', 1)
                ),
                administered_by=vaccination_data['administered_by'],
                location=vaccination_data['location'],
                batch_number=vaccination_data['batch_number'],
                side_effects=vaccination_data.get('side_effects', [])
            )
            
            # تحديث جدول التطعيمات
            schedule_update = self._update_vaccination_schedule(
                vaccination_data['patient_id'],
                vaccination_data['vaccine_code'],
                vaccination_data.get('dose_number', 1)
            )
            
            # إنشاء شهادة التطعيم
            certificate = self._generate_vaccination_certificate(vaccination_record)
            
            return {
                'success': True,
                'vaccination_record': vaccination_record.__dict__,
                'certificate': certificate,
                'schedule_updated': schedule_update,
                'next_appointment_needed': vaccination_record.next_dose_date is not None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_next_dose_date(self, vaccine_code: str, current_dose: int) -> Optional[datetime]:
        """حساب تاريخ الجرعة التالية"""
        if vaccine_code not in self.vaccines_database:
            return None
        
        vaccine_data = self.vaccines_database[vaccine_code]
        doses = vaccine_data['doses']
        
        # إذا كانت هناك جرعة تالية
        if current_dose < len(doses):
            next_dose = doses[current_dose]  # الجرعة التالية (index = current_dose)
            
            # حساب الفترة بين الجرعات
            current_dose_data = doses[current_dose - 1]
            interval_months = next_dose['age_months'] - current_dose_data['age_months']
            
            return datetime.now() + timedelta(days=interval_months * 30)
        
        return None
    
    def _update_vaccination_schedule(self, patient_id: str, vaccine_code: str, dose_number: int) -> bool:
        """تحديث جدول التطعيمات"""
        try:
            # في التطبيق الحقيقي، سيتم تحديث قاعدة البيانات
            # هنا محاكاة للتحديث
            current_app.logger.info(f"تم تحديث جدول التطعيمات للمريض {patient_id}")
            return True
        except Exception as e:
            current_app.logger.error(f"خطأ في تحديث جدول التطعيمات: {str(e)}")
            return False
    
    def _generate_vaccination_certificate(self, record: VaccineRecord) -> Dict:
        """إنتاج شهادة التطعيم"""
        certificate = {
            'certificate_id': str(uuid.uuid4()),
            'patient_id': record.patient_id,
            'vaccine_name': record.vaccine_name,
            'dose_number': record.dose_number,
            'administration_date': record.administered_date.isoformat(),
            'administered_by': record.administered_by,
            'location': record.location,
            'batch_number': record.batch_number,
            'certificate_date': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=365)).isoformat(),
            'qr_code_data': f"VACCINE:{record.record_id}:{record.patient_id}:{record.vaccine_name}",
            'verification_url': f"https://sahty.zya.me/verify-certificate/{record.record_id}"
        }
        
        return certificate
    
    def get_travel_vaccination_requirements(self, destination_country: str) -> Dict:
        """
        الحصول على متطلبات التطعيم للسفر
        
        Args:
            destination_country: الدولة المقصودة
            
        Returns:
            Dict: متطلبات التطعيم
        """
        try:
            # قاعدة بيانات متطلبات السفر
            travel_requirements = {
                'saudi_arabia': {
                    'country_name': 'المملكة العربية السعودية',
                    'required_vaccines': [
                        {
                            'vaccine_code': 'meningitis',
                            'requirement_type': 'mandatory',
                            'valid_duration_years': 3,
                            'minimum_days_before_travel': 10,
                            'notes': 'مطلوب للحج والعمرة'
                        }
                    ],
                    'recommended_vaccines': [
                        {
                            'vaccine_code': 'influenza',
                            'requirement_type': 'recommended',
                            'notes': 'موصى به خاصة في موسم الحج'
                        }
                    ]
                },
                'brazil': {
                    'country_name': 'البرازيل',
                    'required_vaccines': [
                        {
                            'vaccine_code': 'yellow_fever',
                            'requirement_type': 'mandatory',
                            'valid_duration_years': 10,
                            'minimum_days_before_travel': 10,
                            'notes': 'مطلوب لدخول البلاد'
                        }
                    ],
                    'recommended_vaccines': [
                        {
                            'vaccine_code': 'hepatitis_a',
                            'requirement_type': 'recommended'
                        }
                    ]
                },
                'india': {
                    'country_name': 'الهند',
                    'required_vaccines': [],
                    'recommended_vaccines': [
                        {
                            'vaccine_code': 'hepatitis_a',
                            'requirement_type': 'recommended'
                        },
                        {
                            'vaccine_code': 'typhoid',
                            'requirement_type': 'recommended'
                        }
                    ]
                }
            }
            
            country_key = destination_country.lower().replace(' ', '_')
            
            if country_key not in travel_requirements:
                return {
                    'success': False,
                    'error': 'معلومات السفر غير متوفرة لهذه الدولة'
                }
            
            requirements = travel_requirements[country_key]
            
            # إضافة معلومات مفصلة عن كل تطعيم
            for vaccine_list in [requirements['required_vaccines'], requirements['recommended_vaccines']]:
                for vaccine in vaccine_list:
                    if vaccine['vaccine_code'] in self.vaccines_database:
                        vaccine_data = self.vaccines_database[vaccine['vaccine_code']]
                        vaccine.update({
                            'vaccine_name': vaccine_data['name'],
                            'protection_against': vaccine_data['protection_against'],
                            'side_effects': vaccine_data['side_effects'],
                            'contraindications': vaccine_data['contraindications']
                        })
            
            return {
                'success': True,
                'destination': requirements['country_name'],
                'requirements': requirements,
                'travel_health_tips': [
                    'استشر طبيب السفر قبل 4-6 أسابيع من السفر',
                    'احتفظ بشهادات التطعيم معك',
                    'تأكد من صحة معلومات التطعيم',
                    'احمل أدوية الطوارئ الشخصية'
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_vaccination_centers(self, location: Dict = None, vaccine_code: str = None) -> Dict:
        """
        الحصول على مراكز التطعيم
        
        Args:
            location: الموقع الحالي
            vaccine_code: رمز التطعيم المطلوب
            
        Returns:
            Dict: مراكز التطعيم
        """
        try:
            centers = self.vaccination_centers.copy()
            
            # فلترة حسب التطعيم المطلوب
            if vaccine_code:
                centers = [c for c in centers if vaccine_code in c['available_vaccines']]
            
            # إضافة معلومات إضافية
            for center in centers:
                center['available_slots'] = self._get_available_slots(center['center_id'])
                center['average_waiting_time'] = '15-30 دقيقة'
                
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
    
    def _get_available_slots(self, center_id: int) -> List[Dict]:
        """الحصول على المواعيد المتاحة"""
        # محاكاة المواعيد المتاحة
        slots = []
        for i in range(1, 8):  # الأسبوع القادم
            date = (datetime.now() + timedelta(days=i)).date()
            for hour in [9, 10, 11, 14, 15, 16]:
                slots.append({
                    'date': date.isoformat(),
                    'time': f'{hour:02d}:00',
                    'available': True
                })
        
        return slots[:15]  # أول 15 موعد
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """حساب المسافة بين نقطتين"""
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
    
    def send_vaccination_reminders(self, patient_id: str) -> Dict:
        """
        إرسال تذكيرات التطعيم
        
        Args:
            patient_id: معرف المريض
            
        Returns:
            Dict: نتيجة الإرسال
        """
        try:
            # الحصول على التطعيمات المستحقة
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            
            due_vaccines = [
                {
                    'vaccine_name': 'لقاح الإنفلونزا الموسمية',
                    'due_date': '2024-02-01',
                    'priority': 'متوسطة'
                }
            ]
            
            if not due_vaccines:
                return {
                    'success': True,
                    'message': 'لا توجد تطعيمات مستحقة حالياً'
                }
            
            # إرسال التذكيرات
            reminders_sent = []
            for vaccine in due_vaccines:
                reminder = {
                    'reminder_id': str(uuid.uuid4()),
                    'patient_id': patient_id,
                    'vaccine_name': vaccine['vaccine_name'],
                    'due_date': vaccine['due_date'],
                    'priority': vaccine['priority'],
                    'message': f"تذكير: حان موعد تطعيم {vaccine['vaccine_name']}",
                    'sent_at': datetime.now().isoformat(),
                    'channels': ['app_notification', 'sms', 'email']
                }
                reminders_sent.append(reminder)
            
            return {
                'success': True,
                'reminders_sent': reminders_sent,
                'total_reminders': len(reminders_sent)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_vaccination_statistics(self, patient_id: str = None, 
                                 center_id: int = None) -> Dict:
        """
        الحصول على إحصائيات التطعيم
        
        Args:
            patient_id: معرف المريض (للإحصائيات الشخصية)
            center_id: معرف المركز (لإحصائيات المركز)
            
        Returns:
            Dict: الإحصائيات
        """
        try:
            if patient_id:
                # إحصائيات المريض
                stats = {
                    'patient_id': patient_id,
                    'total_vaccines_received': 12,
                    'completion_rate': 85.7,
                    'next_due_vaccines': 2,
                    'overdue_vaccines': 0,
                    'last_vaccination_date': '2024-01-15',
                    'vaccine_history': [
                        {'vaccine': 'لقاح كوفيد-19', 'date': '2024-01-15', 'dose': 3},
                        {'vaccine': 'لقاح الإنفلونزا', 'date': '2023-10-01', 'dose': 1}
                    ],
                    'upcoming_vaccines': [
                        {'vaccine': 'لقاح الإنفلونزا', 'due_date': '2024-10-01'}
                    ]
                }
            elif center_id:
                # إحصائيات المركز
                stats = {
                    'center_id': center_id,
                    'total_vaccinations_today': 45,
                    'total_vaccinations_month': 1250,
                    'most_administered_vaccine': 'لقاح كوفيد-19',
                    'average_daily_vaccinations': 42,
                    'peak_hours': ['10:00-12:00', '14:00-16:00'],
                    'vaccine_distribution': {
                        'covid19': 35,
                        'influenza': 25,
                        'hepatitis_b': 20,
                        'others': 20
                    }
                }
            else:
                # إحصائيات عامة
                stats = {
                    'total_vaccinations_country': 125000,
                    'vaccination_coverage_rate': 78.5,
                    'most_popular_vaccine': 'لقاح كوفيد-19',
                    'active_vaccination_centers': len(self.vaccination_centers),
                    'vaccines_available': len(self.vaccines_database),
                    'monthly_trend': 'increasing',
                    'age_group_coverage': {
                        'infants': 92.3,
                        'children': 88.7,
                        'adults': 65.2,
                        'elderly': 82.1
                    }
                }
            
            return {
                'success': True,
                'statistics': stats,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

