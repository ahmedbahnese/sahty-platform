"""
خدمة إدارة الأدوية والعلاجات
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, time
from flask import current_app
import uuid
from dataclasses import dataclass
from enum import Enum

class MedicationFrequency(Enum):
    ONCE_DAILY = "مرة واحدة يومياً"
    TWICE_DAILY = "مرتين يومياً"
    THREE_TIMES_DAILY = "ثلاث مرات يومياً"
    FOUR_TIMES_DAILY = "أربع مرات يومياً"
    EVERY_8_HOURS = "كل 8 ساعات"
    EVERY_12_HOURS = "كل 12 ساعة"
    AS_NEEDED = "عند الحاجة"
    WEEKLY = "أسبوعياً"
    MONTHLY = "شهرياً"

class MedicationType(Enum):
    TABLET = "قرص"
    CAPSULE = "كبسولة"
    SYRUP = "شراب"
    INJECTION = "حقنة"
    DROPS = "نقط"
    CREAM = "كريم"
    INHALER = "بخاخ"
    PATCH = "لصقة"

@dataclass
class MedicationDose:
    time: str
    amount: str
    taken: bool = False
    taken_at: Optional[datetime] = None
    notes: Optional[str] = None

class MedicationService:
    def __init__(self):
        """تهيئة خدمة إدارة الأدوية"""
        # قاعدة بيانات الأدوية المصرية
        self.medication_database = {
            'paracetamol': {
                'name_ar': 'باراسيتامول',
                'name_en': 'Paracetamol',
                'generic_name': 'أسيتامينوفين',
                'category': 'مسكن وخافض حرارة',
                'manufacturer': 'شركة الإسكندرية للأدوية',
                'strength': ['500mg', '1000mg'],
                'forms': ['قرص', 'شراب', 'تحاميل'],
                'indications': ['ألم', 'حمى', 'صداع'],
                'contraindications': ['حساسية للمادة الفعالة', 'أمراض الكبد الشديدة'],
                'side_effects': ['غثيان نادر', 'طفح جلدي نادر'],
                'interactions': ['وارفارين', 'كاربامازيبين'],
                'dosage': {
                    'adult': '500-1000mg كل 4-6 ساعات',
                    'child': '10-15mg/kg كل 4-6 ساعات'
                },
                'max_daily_dose': '4000mg',
                'pregnancy_category': 'B',
                'price_range': '5-15 جنيه'
            },
            'amoxicillin': {
                'name_ar': 'أموكسيسيلين',
                'name_en': 'Amoxicillin',
                'generic_name': 'أموكسيسيلين',
                'category': 'مضاد حيوي',
                'manufacturer': 'شركة ممفيس للأدوية',
                'strength': ['250mg', '500mg', '1000mg'],
                'forms': ['كبسولة', 'شراب', 'حقن'],
                'indications': ['التهابات بكتيرية', 'التهاب الحلق', 'التهاب الأذن'],
                'contraindications': ['حساسية البنسلين', 'عدد كريات الدم البيضاء الوحيدة'],
                'side_effects': ['إسهال', 'غثيان', 'طفح جلدي'],
                'interactions': ['وارفارين', 'حبوب منع الحمل'],
                'dosage': {
                    'adult': '250-500mg كل 8 ساعات',
                    'child': '20-40mg/kg يومياً مقسمة على جرعات'
                },
                'max_daily_dose': '3000mg',
                'pregnancy_category': 'B',
                'price_range': '15-35 جنيه'
            },
            'metformin': {
                'name_ar': 'ميتفورمين',
                'name_en': 'Metformin',
                'generic_name': 'ميتفورمين هيدروكلوريد',
                'category': 'مضاد السكري',
                'manufacturer': 'شركة سيديكو للأدوية',
                'strength': ['500mg', '850mg', '1000mg'],
                'forms': ['قرص', 'قرص ممتد المفعول'],
                'indications': ['السكري النوع الثاني', 'متلازمة تكيس المبايض'],
                'contraindications': ['أمراض الكلى الشديدة', 'فشل القلب', 'الحماض الكيتوني'],
                'side_effects': ['إسهال', 'غثيان', 'طعم معدني في الفم'],
                'interactions': ['الكحول', 'مدرات البول', 'الكورتيزون'],
                'dosage': {
                    'adult': '500mg مرتين يومياً مع الطعام',
                    'child': 'غير مناسب للأطفال'
                },
                'max_daily_dose': '2550mg',
                'pregnancy_category': 'B',
                'price_range': '20-45 جنيه'
            }
        }
        
        # الصيدليات المتاحة
        self.pharmacies = [
            {
                'id': 1,
                'name': 'صيدلية العزبي',
                'address': 'شارع الجامعة، الجيزة',
                'phone': '0233334444',
                'delivery': True,
                'online_ordering': True,
                'working_hours': '8:00 AM - 12:00 AM'
            },
            {
                'id': 2,
                'name': 'صيدلية سيف',
                'address': 'مدينة نصر، القاهرة',
                'phone': '0225555555',
                'delivery': True,
                'online_ordering': True,
                'working_hours': '24/7'
            }
        ]
    
    def create_medication_plan(self, patient_id: str, medications: List[Dict]) -> Dict:
        """
        إنشاء خطة دوائية للمريض
        
        Args:
            patient_id: معرف المريض
            medications: قائمة الأدوية والجرعات
            
        Returns:
            Dict: خطة الأدوية
        """
        try:
            plan_id = str(uuid.uuid4())
            
            medication_schedule = []
            
            for med in medications:
                # البحث عن معلومات الدواء
                med_info = self._get_medication_info(med['name'])
                
                # إنشاء جدول الجرعات
                doses = self._calculate_dose_schedule(
                    frequency=med['frequency'],
                    start_time=med.get('start_time', '08:00'),
                    duration_days=med.get('duration_days', 7)
                )
                
                # فحص التفاعلات الدوائية
                interactions = self._check_drug_interactions(med['name'], medications)
                
                medication_entry = {
                    'medication_id': str(uuid.uuid4()),
                    'name': med['name'],
                    'dosage': med['dosage'],
                    'frequency': med['frequency'],
                    'duration_days': med.get('duration_days', 7),
                    'instructions': med.get('instructions', ''),
                    'with_food': med.get('with_food', False),
                    'medication_info': med_info,
                    'dose_schedule': doses,
                    'interactions': interactions,
                    'start_date': med.get('start_date', datetime.now().date().isoformat()),
                    'end_date': (datetime.now().date() + timedelta(days=med.get('duration_days', 7))).isoformat(),
                    'status': 'active'
                }
                
                medication_schedule.append(medication_entry)
            
            # إنشاء الخطة الدوائية
            medication_plan = {
                'plan_id': plan_id,
                'patient_id': patient_id,
                'medications': medication_schedule,
                'created_at': datetime.now().isoformat(),
                'created_by': 'system',  # أو معرف الطبيب
                'status': 'active',
                'total_medications': len(medication_schedule),
                'adherence_score': 0.0,
                'next_dose_time': self._get_next_dose_time(medication_schedule)
            }
            
            return {
                'success': True,
                'medication_plan': medication_plan
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء الخطة الدوائية: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_medication_info(self, medication_name: str) -> Dict:
        """الحصول على معلومات الدواء من قاعدة البيانات"""
        # البحث في قاعدة البيانات
        for key, med_info in self.medication_database.items():
            if (medication_name.lower() in med_info['name_ar'].lower() or
                medication_name.lower() in med_info['name_en'].lower()):
                return med_info
        
        # إذا لم يتم العثور على الدواء، إرجاع معلومات افتراضية
        return {
            'name_ar': medication_name,
            'name_en': medication_name,
            'category': 'غير محدد',
            'manufacturer': 'غير محدد',
            'indications': [],
            'side_effects': [],
            'interactions': [],
            'pregnancy_category': 'غير محدد'
        }
    
    def _calculate_dose_schedule(self, frequency: str, start_time: str, duration_days: int) -> List[Dict]:
        """حساب جدول الجرعات"""
        doses = []
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        
        # تحديد أوقات الجرعات حسب التكرار
        if frequency == MedicationFrequency.ONCE_DAILY.value:
            times = [start_time_obj]
        elif frequency == MedicationFrequency.TWICE_DAILY.value:
            times = [
                start_time_obj,
                (datetime.combine(datetime.today(), start_time_obj) + timedelta(hours=12)).time()
            ]
        elif frequency == MedicationFrequency.THREE_TIMES_DAILY.value:
            times = [
                start_time_obj,
                (datetime.combine(datetime.today(), start_time_obj) + timedelta(hours=8)).time(),
                (datetime.combine(datetime.today(), start_time_obj) + timedelta(hours=16)).time()
            ]
        elif frequency == MedicationFrequency.FOUR_TIMES_DAILY.value:
            times = [
                start_time_obj,
                (datetime.combine(datetime.today(), start_time_obj) + timedelta(hours=6)).time(),
                (datetime.combine(datetime.today(), start_time_obj) + timedelta(hours=12)).time(),
                (datetime.combine(datetime.today(), start_time_obj) + timedelta(hours=18)).time()
            ]
        else:
            times = [start_time_obj]  # افتراضي
        
        # إنشاء الجدول لكل يوم
        for day in range(duration_days):
            date = datetime.now().date() + timedelta(days=day)
            for time_obj in times:
                dose_datetime = datetime.combine(date, time_obj)
                doses.append({
                    'dose_id': str(uuid.uuid4()),
                    'date': date.isoformat(),
                    'time': time_obj.strftime('%H:%M'),
                    'datetime': dose_datetime.isoformat(),
                    'taken': False,
                    'taken_at': None,
                    'notes': None,
                    'reminder_sent': False
                })
        
        return doses
    
    def _check_drug_interactions(self, medication_name: str, all_medications: List[Dict]) -> List[Dict]:
        """فحص التفاعلات الدوائية"""
        interactions = []
        
        # الحصول على معلومات الدواء الحالي
        current_med_info = self._get_medication_info(medication_name)
        current_interactions = current_med_info.get('interactions', [])
        
        # فحص التفاعلات مع الأدوية الأخرى
        for other_med in all_medications:
            if other_med['name'] != medication_name:
                other_med_info = self._get_medication_info(other_med['name'])
                
                # فحص إذا كان هناك تفاعل
                for interaction in current_interactions:
                    if (interaction.lower() in other_med_info['name_ar'].lower() or
                        interaction.lower() in other_med_info['name_en'].lower()):
                        interactions.append({
                            'medication': other_med['name'],
                            'interaction_type': 'تفاعل دوائي',
                            'severity': 'متوسط',  # يمكن تحديدها بدقة أكثر
                            'description': f'قد يحدث تفاعل بين {medication_name} و {other_med["name"]}',
                            'recommendation': 'استشر الطبيب أو الصيدلي'
                        })
        
        return interactions
    
    def _get_next_dose_time(self, medication_schedule: List[Dict]) -> Optional[str]:
        """الحصول على وقت الجرعة التالية"""
        now = datetime.now()
        next_doses = []
        
        for medication in medication_schedule:
            for dose in medication['dose_schedule']:
                dose_datetime = datetime.fromisoformat(dose['datetime'])
                if dose_datetime > now and not dose['taken']:
                    next_doses.append(dose_datetime)
        
        if next_doses:
            return min(next_doses).isoformat()
        return None
    
    def record_dose_taken(self, patient_id: str, dose_id: str, taken_at: datetime = None, notes: str = None) -> Dict:
        """تسجيل تناول الجرعة"""
        try:
            taken_time = taken_at or datetime.now()
            
            # في التطبيق الحقيقي، سيتم تحديث قاعدة البيانات
            dose_record = {
                'dose_id': dose_id,
                'patient_id': patient_id,
                'taken': True,
                'taken_at': taken_time.isoformat(),
                'notes': notes,
                'recorded_at': datetime.now().isoformat()
            }
            
            # حساب الالتزام
            adherence_score = self._calculate_adherence(patient_id)
            
            return {
                'success': True,
                'dose_record': dose_record,
                'adherence_score': adherence_score,
                'message': 'تم تسجيل تناول الجرعة بنجاح'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_adherence(self, patient_id: str) -> float:
        """حساب معدل الالتزام بالأدوية"""
        # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
        # هنا محاكاة للحساب
        total_doses = 100
        taken_doses = 85
        
        adherence_score = (taken_doses / total_doses) * 100
        return round(adherence_score, 2)
    
    def get_medication_reminders(self, patient_id: str, date: str = None) -> List[Dict]:
        """الحصول على تذكيرات الأدوية لليوم"""
        try:
            target_date = date or datetime.now().date().isoformat()
            
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            # هنا محاكاة للتذكيرات
            reminders = [
                {
                    'reminder_id': str(uuid.uuid4()),
                    'medication_name': 'باراسيتامول',
                    'dosage': '500mg',
                    'time': '08:00',
                    'instructions': 'مع الطعام',
                    'status': 'pending'
                },
                {
                    'reminder_id': str(uuid.uuid4()),
                    'medication_name': 'أموكسيسيلين',
                    'dosage': '250mg',
                    'time': '14:00',
                    'instructions': 'قبل الطعام بساعة',
                    'status': 'pending'
                },
                {
                    'reminder_id': str(uuid.uuid4()),
                    'medication_name': 'ميتفورمين',
                    'dosage': '500mg',
                    'time': '20:00',
                    'instructions': 'مع العشاء',
                    'status': 'pending'
                }
            ]
            
            return reminders
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على التذكيرات: {str(e)}")
            return []
    
    def search_medications(self, query: str, category: str = None) -> List[Dict]:
        """البحث عن الأدوية"""
        try:
            results = []
            
            for key, med_info in self.medication_database.items():
                # البحث في الاسم العربي والإنجليزي
                if (query.lower() in med_info['name_ar'].lower() or
                    query.lower() in med_info['name_en'].lower() or
                    query.lower() in med_info['generic_name'].lower()):
                    
                    # فلترة حسب الفئة إذا تم تحديدها
                    if category and category.lower() not in med_info['category'].lower():
                        continue
                    
                    results.append({
                        'id': key,
                        'name_ar': med_info['name_ar'],
                        'name_en': med_info['name_en'],
                        'category': med_info['category'],
                        'manufacturer': med_info['manufacturer'],
                        'strength': med_info['strength'],
                        'forms': med_info['forms'],
                        'price_range': med_info['price_range']
                    })
            
            return results
            
        except Exception as e:
            current_app.logger.error(f"خطأ في البحث عن الأدوية: {str(e)}")
            return []
    
    def check_medication_availability(self, medication_name: str, location: Dict = None) -> List[Dict]:
        """فحص توفر الدواء في الصيدليات"""
        try:
            availability = []
            
            for pharmacy in self.pharmacies:
                # محاكاة فحص التوفر
                is_available = True  # في التطبيق الحقيقي، سيتم فحص المخزون
                price = 25.0  # سعر وهمي
                
                if is_available:
                    availability.append({
                        'pharmacy_id': pharmacy['id'],
                        'pharmacy_name': pharmacy['name'],
                        'address': pharmacy['address'],
                        'phone': pharmacy['phone'],
                        'available': True,
                        'price': price,
                        'delivery_available': pharmacy['delivery'],
                        'online_ordering': pharmacy['online_ordering'],
                        'estimated_delivery': '30-60 دقيقة' if pharmacy['delivery'] else None
                    })
            
            return availability
            
        except Exception as e:
            current_app.logger.error(f"خطأ في فحص توفر الدواء: {str(e)}")
            return []
    
    def create_medication_order(self, patient_id: str, pharmacy_id: int, 
                              medications: List[Dict], delivery_address: str = None) -> Dict:
        """إنشاء طلب أدوية"""
        try:
            order_id = str(uuid.uuid4())
            
            # حساب التكلفة الإجمالية
            total_cost = sum(med.get('price', 0) * med.get('quantity', 1) for med in medications)
            delivery_fee = 10.0 if delivery_address else 0.0
            
            order = {
                'order_id': order_id,
                'patient_id': patient_id,
                'pharmacy_id': pharmacy_id,
                'medications': medications,
                'subtotal': total_cost,
                'delivery_fee': delivery_fee,
                'total_amount': total_cost + delivery_fee,
                'delivery_address': delivery_address,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'estimated_delivery': datetime.now() + timedelta(hours=1) if delivery_address else None
            }
            
            return {
                'success': True,
                'order': order,
                'message': 'تم إنشاء الطلب بنجاح'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_medication_history(self, patient_id: str, start_date: str = None, end_date: str = None) -> Dict:
        """الحصول على تاريخ الأدوية للمريض"""
        try:
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            # هنا محاكاة للتاريخ
            
            history = {
                'patient_id': patient_id,
                'period': {
                    'start_date': start_date or (datetime.now() - timedelta(days=30)).date().isoformat(),
                    'end_date': end_date or datetime.now().date().isoformat()
                },
                'medications': [
                    {
                        'name': 'باراسيتامول',
                        'dosage': '500mg',
                        'frequency': 'مرتين يومياً',
                        'start_date': '2024-01-01',
                        'end_date': '2024-01-07',
                        'prescribed_by': 'د. أحمد محمد',
                        'adherence_rate': 95.0,
                        'total_doses': 14,
                        'taken_doses': 13
                    },
                    {
                        'name': 'أموكسيسيلين',
                        'dosage': '250mg',
                        'frequency': 'ثلاث مرات يومياً',
                        'start_date': '2024-01-05',
                        'end_date': '2024-01-12',
                        'prescribed_by': 'د. فاطمة علي',
                        'adherence_rate': 88.0,
                        'total_doses': 21,
                        'taken_doses': 18
                    }
                ],
                'overall_adherence': 91.5,
                'total_medications': 2
            }
            
            return {
                'success': True,
                'history': history
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

