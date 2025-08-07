"""
خدمة الطوارئ الطبية والاستجابة السريعة
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum
import math

class EmergencyType(Enum):
    CARDIAC = "طوارئ قلبية"
    RESPIRATORY = "طوارئ تنفسية"
    NEUROLOGICAL = "طوارئ عصبية"
    TRAUMA = "إصابات وحوادث"
    POISONING = "تسمم"
    ALLERGIC_REACTION = "حساسية شديدة"
    DIABETIC = "طوارئ السكري"
    OBSTETRIC = "طوارئ الولادة"
    PSYCHIATRIC = "طوارئ نفسية"
    GENERAL = "طوارئ عامة"

class UrgencyLevel(Enum):
    CRITICAL = "حرج - دقائق"
    URGENT = "عاجل - ساعة"
    SEMI_URGENT = "شبه عاجل - ساعات"
    NON_URGENT = "غير عاجل"

class EmergencyStatus(Enum):
    REPORTED = "تم الإبلاغ"
    DISPATCHED = "تم الإرسال"
    ON_SCENE = "في الموقع"
    TRANSPORTING = "في الطريق للمستشفى"
    COMPLETED = "مكتمل"
    CANCELLED = "ملغي"

@dataclass
class EmergencyCall:
    call_id: str
    patient_id: str
    emergency_type: str
    urgency_level: str
    location: Dict
    symptoms: List[str]
    vital_signs: Dict
    caller_info: Dict
    timestamp: datetime
    status: str

class EmergencyService:
    def __init__(self):
        """تهيئة خدمة الطوارئ"""
        
        # قاعدة بيانات أعراض الطوارئ
        self.emergency_symptoms = {
            EmergencyType.CARDIAC.value: {
                'critical_symptoms': [
                    'ألم شديد في الصدر',
                    'ضيق تنفس شديد',
                    'فقدان الوعي',
                    'عدم انتظام ضربات القلب الشديد',
                    'تعرق بارد مع ألم الصدر'
                ],
                'warning_signs': [
                    'ألم في الذراع الأيسر',
                    'غثيان مع ألم الصدر',
                    'دوخة شديدة',
                    'ضعف عام مفاجئ'
                ],
                'first_aid': [
                    'اتصل بالإسعاف فوراً (123)',
                    'ساعد المريض على الجلوس',
                    'فك الملابس الضيقة',
                    'أعط أسبرين إذا لم يكن لديه حساسية',
                    'راقب التنفس والنبض'
                ]
            },
            EmergencyType.RESPIRATORY.value: {
                'critical_symptoms': [
                    'عدم القدرة على التنفس',
                    'ازرقاق الشفاه أو الأظافر',
                    'فقدان الوعي',
                    'صوت صفير عالي عند التنفس',
                    'سعال دموي'
                ],
                'warning_signs': [
                    'ضيق تنفس شديد',
                    'ألم في الصدر عند التنفس',
                    'تنفس سريع جداً',
                    'عدم القدرة على الكلام'
                ],
                'first_aid': [
                    'اتصل بالإسعاف فوراً',
                    'ساعد المريض على الجلوس منتصباً',
                    'فتح النوافذ للهواء النقي',
                    'فك الملابس الضيقة',
                    'تهدئة المريض'
                ]
            },
            EmergencyType.NEUROLOGICAL.value: {
                'critical_symptoms': [
                    'فقدان الوعي المفاجئ',
                    'تشنجات',
                    'شلل مفاجئ في الوجه أو الأطراف',
                    'فقدان القدرة على الكلام',
                    'صداع شديد مفاجئ'
                ],
                'warning_signs': [
                    'دوخة شديدة',
                    'تنميل في الوجه أو الأطراف',
                    'تشويش في الرؤية',
                    'صعوبة في البلع'
                ],
                'first_aid': [
                    'اتصل بالإسعاف فوراً',
                    'ضع المريض في وضع الإفاقة',
                    'لا تعط أي طعام أو شراب',
                    'راقب التنفس',
                    'سجل وقت بداية الأعراض'
                ]
            },
            EmergencyType.TRAUMA.value: {
                'critical_symptoms': [
                    'نزيف شديد',
                    'كسور مفتوحة',
                    'إصابة في الرأس أو الرقبة',
                    'عدم القدرة على الحركة',
                    'ألم شديد في البطن'
                ],
                'warning_signs': [
                    'ألم شديد',
                    'تورم كبير',
                    'تشوه في الأطراف',
                    'دوخة أو غثيان'
                ],
                'first_aid': [
                    'اتصل بالإسعاف فوراً',
                    'لا تحرك المريض إذا كانت إصابة الرقبة محتملة',
                    'أوقف النزيف بالضغط المباشر',
                    'حافظ على دفء المريض',
                    'راقب العلامات الحيوية'
                ]
            },
            EmergencyType.POISONING.value: {
                'critical_symptoms': [
                    'فقدان الوعي',
                    'صعوبة في التنفس',
                    'تشنجات',
                    'قيء دموي',
                    'حروق في الفم أو الحلق'
                ],
                'warning_signs': [
                    'غثيان وقيء شديد',
                    'إسهال',
                    'ألم في البطن',
                    'دوخة'
                ],
                'first_aid': [
                    'اتصل بمركز السموم (16123)',
                    'احتفظ بعينة من المادة السامة',
                    'لا تحفز القيء إلا بتوجيه طبي',
                    'أعط الماء إذا كان المريض واعياً',
                    'راقب التنفس'
                ]
            },
            EmergencyType.ALLERGIC_REACTION.value: {
                'critical_symptoms': [
                    'صعوبة في التنفس',
                    'تورم في الوجه أو الحلق',
                    'انخفاض ضغط الدم',
                    'فقدان الوعي',
                    'طفح جلدي منتشر'
                ],
                'warning_signs': [
                    'حكة شديدة',
                    'تورم في الشفاه',
                    'غثيان',
                    'دوخة'
                ],
                'first_aid': [
                    'اتصل بالإسعاف فوراً',
                    'أعط حقنة الإبينفرين إذا متوفرة',
                    'ساعد المريض على الجلوس',
                    'أزل المسبب إذا كان معروفاً',
                    'راقب التنفس'
                ]
            },
            EmergencyType.DIABETIC.value: {
                'critical_symptoms': [
                    'فقدان الوعي',
                    'تشنجات',
                    'تنفس سريع وعميق',
                    'رائحة الأسيتون في النفس',
                    'جفاف شديد'
                ],
                'warning_signs': [
                    'تشويش ذهني',
                    'عطش شديد',
                    'كثرة التبول',
                    'ضعف عام'
                ],
                'first_aid': [
                    'اتصل بالإسعاف',
                    'إذا كان المريض واعياً وسكره منخفض، أعط سكر',
                    'إذا كان فاقد الوعي، لا تعط أي شيء بالفم',
                    'ضعه في وضع الإفاقة',
                    'راقب العلامات الحيوية'
                ]
            }
        }
        
        # مراكز الطوارئ في مصر
        self.emergency_centers = [
            {
                'center_id': 1,
                'name': 'مستشفى قصر العيني - طوارئ',
                'address': 'شارع قصر العيني، القاهرة',
                'phone': '0223654321',
                'emergency_phone': '123',
                'specialties': ['طوارئ عامة', 'قلب', 'مخ وأعصاب', 'جراحة'],
                'capacity': 50,
                'current_load': 35,
                'average_wait_time': 15,  # دقيقة
                'lat': 30.0444,
                'lng': 31.2357,
                'available_24h': True
            },
            {
                'center_id': 2,
                'name': 'مستشفى عين شمس - طوارئ',
                'address': 'شارع رمسيس، القاهرة',
                'phone': '0224567890',
                'emergency_phone': '123',
                'specialties': ['طوارئ عامة', 'أطفال', 'نساء وولادة'],
                'capacity': 40,
                'current_load': 28,
                'average_wait_time': 20,
                'lat': 30.0626,
                'lng': 31.2497,
                'available_24h': True
            },
            {
                'center_id': 3,
                'name': 'مستشفى الإسكندرية الجامعي - طوارئ',
                'address': 'شارع الحرية، الإسكندرية',
                'phone': '0334567890',
                'emergency_phone': '123',
                'specialties': ['طوارئ عامة', 'حروق', 'سموم'],
                'capacity': 35,
                'current_load': 20,
                'average_wait_time': 10,
                'lat': 31.2001,
                'lng': 29.9187,
                'available_24h': True
            },
            {
                'center_id': 4,
                'name': 'مستشفى أسوان الجامعي - طوارئ',
                'address': 'شارع الكورنيش، أسوان',
                'phone': '0973456789',
                'emergency_phone': '123',
                'specialties': ['طوارئ عامة', 'جراحة'],
                'capacity': 25,
                'current_load': 15,
                'average_wait_time': 8,
                'lat': 24.0889,
                'lng': 32.8998,
                'available_24h': True
            }
        ]
        
        # أرقام الطوارئ في مصر
        self.emergency_numbers = {
            'ambulance': '123',
            'police': '122',
            'fire': '180',
            'poison_control': '16123',
            'gas_emergency': '129',
            'electricity_emergency': '121',
            'tourist_police': '126'
        }
        
        # بروتوكولات الإسعافات الأولية
        self.first_aid_protocols = {
            'cpr': {
                'name': 'الإنعاش القلبي الرئوي',
                'when_to_use': 'عند توقف التنفس أو القلب',
                'steps': [
                    'تأكد من سلامة المكان',
                    'تحقق من استجابة المريض',
                    'اتصل بالإسعاف (123)',
                    'ضع المريض على سطح صلب',
                    'ضع يديك على وسط الصدر',
                    'اضغط بقوة وسرعة 100-120 ضغطة/دقيقة',
                    'اترك الصدر يرتفع تماماً بين الضغطات',
                    'استمر حتى وصول الإسعاف'
                ],
                'video_url': 'https://example.com/cpr-video'
            },
            'choking': {
                'name': 'الاختناق',
                'when_to_use': 'عند انسداد مجرى التنفس',
                'steps': [
                    'اسأل "هل تختنق؟"',
                    'إذا كان يستطيع الكلام، شجعه على السعال',
                    'إذا لم يستطع الكلام:',
                    'قف خلف المريض',
                    'ضع ذراعيك حول خصره',
                    'ضع قبضتك فوق السرة',
                    'اضغط بقوة وسرعة للأعلى',
                    'كرر حتى خروج الجسم الغريب'
                ],
                'video_url': 'https://example.com/choking-video'
            },
            'bleeding': {
                'name': 'النزيف',
                'when_to_use': 'عند حدوث نزيف خارجي',
                'steps': [
                    'ارتد قفازات إذا متوفرة',
                    'اضغط مباشرة على الجرح بقطعة قماش نظيفة',
                    'ارفع العضو المصاب إذا أمكن',
                    'لا تزل الضمادة الأولى',
                    'أضف ضمادات إضافية إذا لزم الأمر',
                    'اربط الضمادة بإحكام',
                    'راقب علامات الصدمة',
                    'اطلب المساعدة الطبية'
                ],
                'video_url': 'https://example.com/bleeding-video'
            },
            'burns': {
                'name': 'الحروق',
                'when_to_use': 'عند حدوث حروق',
                'steps': [
                    'أزل المريض من مصدر الحرق',
                    'برد المنطقة المحروقة بالماء البارد لمدة 20 دقيقة',
                    'أزل المجوهرات والملابس الفضفاضة',
                    'لا تزل الملابس الملتصقة بالجلد',
                    'غط الحرق بضمادة نظيفة',
                    'لا تضع الثلج أو الزبدة',
                    'أعط مسكنات الألم إذا لزم الأمر',
                    'اطلب المساعدة الطبية للحروق الكبيرة'
                ],
                'video_url': 'https://example.com/burns-video'
            }
        }
        
        # مستويات الطوارئ حسب الأعراض
        self.triage_system = {
            'level_1_critical': {
                'color': 'أحمر',
                'description': 'خطر على الحياة - تدخل فوري',
                'max_wait_time': 0,
                'symptoms': [
                    'توقف القلب أو التنفس',
                    'فقدان الوعي',
                    'نزيف شديد',
                    'صدمة',
                    'حروق شديدة'
                ]
            },
            'level_2_urgent': {
                'color': 'برتقالي',
                'description': 'حالة خطيرة - تدخل خلال 10 دقائق',
                'max_wait_time': 10,
                'symptoms': [
                    'ألم صدر شديد',
                    'ضيق تنفس شديد',
                    'إصابات خطيرة',
                    'تشنجات',
                    'حساسية شديدة'
                ]
            },
            'level_3_semi_urgent': {
                'color': 'أصفر',
                'description': 'حالة مهمة - تدخل خلال 30 دقيقة',
                'max_wait_time': 30,
                'symptoms': [
                    'ألم شديد',
                    'حمى عالية',
                    'قيء مستمر',
                    'إصابات متوسطة'
                ]
            },
            'level_4_less_urgent': {
                'color': 'أخضر',
                'description': 'حالة أقل إلحاحاً - تدخل خلال ساعة',
                'max_wait_time': 60,
                'symptoms': [
                    'ألم متوسط',
                    'جروح بسيطة',
                    'أعراض باردة شديدة'
                ]
            },
            'level_5_non_urgent': {
                'color': 'أزرق',
                'description': 'حالة غير عاجلة - يمكن الانتظار',
                'max_wait_time': 120,
                'symptoms': [
                    'أعراض مزمنة',
                    'فحوصات روتينية',
                    'استشارات'
                ]
            }
        }
    
    def report_emergency(self, emergency_data: Dict) -> Dict:
        """
        الإبلاغ عن حالة طوارئ
        
        Args:
            emergency_data: بيانات الطوارئ
            
        Returns:
            Dict: معلومات الاستجابة
        """
        try:
            call_id = str(uuid.uuid4())
            
            # تحليل الأعراض وتحديد نوع الطوارئ
            emergency_analysis = self._analyze_emergency_symptoms(
                emergency_data.get('symptoms', []),
                emergency_data.get('vital_signs', {})
            )
            
            # تحديد مستوى الإلحاح
            urgency_level = self._determine_urgency_level(
                emergency_analysis['emergency_type'],
                emergency_data.get('symptoms', []),
                emergency_data.get('vital_signs', {})
            )
            
            # إنشاء سجل الطوارئ
            emergency_call = EmergencyCall(
                call_id=call_id,
                patient_id=emergency_data.get('patient_id'),
                emergency_type=emergency_analysis['emergency_type'],
                urgency_level=urgency_level,
                location=emergency_data.get('location', {}),
                symptoms=emergency_data.get('symptoms', []),
                vital_signs=emergency_data.get('vital_signs', {}),
                caller_info=emergency_data.get('caller_info', {}),
                timestamp=datetime.now(),
                status=EmergencyStatus.REPORTED.value
            )
            
            # العثور على أقرب مركز طوارئ
            nearest_centers = self._find_nearest_emergency_centers(
                emergency_data.get('location', {}),
                emergency_analysis['emergency_type']
            )
            
            # إنشاء خطة الاستجابة
            response_plan = self._create_response_plan(
                emergency_call, emergency_analysis, nearest_centers
            )
            
            # إرسال التنبيهات
            alerts_sent = self._send_emergency_alerts(emergency_call, response_plan)
            
            return {
                'success': True,
                'emergency_call': emergency_call.__dict__,
                'analysis': emergency_analysis,
                'urgency_level': urgency_level,
                'nearest_centers': nearest_centers,
                'response_plan': response_plan,
                'alerts_sent': alerts_sent,
                'estimated_arrival_time': response_plan.get('estimated_arrival_time'),
                'immediate_instructions': self._get_immediate_instructions(emergency_analysis)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الإبلاغ عن الطوارئ: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_emergency_symptoms(self, symptoms: List[str], vital_signs: Dict) -> Dict:
        """تحليل أعراض الطوارئ"""
        emergency_scores = {}
        
        # تحليل الأعراض
        for emergency_type, type_data in self.emergency_symptoms.items():
            score = 0
            matching_symptoms = []
            
            # فحص الأعراض الحرجة
            for symptom in symptoms:
                if symptom in type_data['critical_symptoms']:
                    score += 10
                    matching_symptoms.append(symptom)
                elif symptom in type_data['warning_signs']:
                    score += 5
                    matching_symptoms.append(symptom)
            
            emergency_scores[emergency_type] = {
                'score': score,
                'matching_symptoms': matching_symptoms
            }
        
        # تحليل العلامات الحيوية
        vital_signs_analysis = self._analyze_vital_signs(vital_signs)
        
        # تحديد نوع الطوارئ الأكثر احتمالاً
        if emergency_scores:
            most_likely = max(emergency_scores.items(), key=lambda x: x[1]['score'])
            emergency_type = most_likely[0] if most_likely[1]['score'] > 0 else EmergencyType.GENERAL.value
        else:
            emergency_type = EmergencyType.GENERAL.value
        
        return {
            'emergency_type': emergency_type,
            'confidence_score': emergency_scores.get(emergency_type, {}).get('score', 0),
            'matching_symptoms': emergency_scores.get(emergency_type, {}).get('matching_symptoms', []),
            'vital_signs_analysis': vital_signs_analysis,
            'all_scores': emergency_scores
        }
    
    def _analyze_vital_signs(self, vital_signs: Dict) -> Dict:
        """تحليل العلامات الحيوية"""
        analysis = {
            'abnormal_signs': [],
            'critical_signs': [],
            'severity_score': 0
        }
        
        # تحليل ضغط الدم
        if 'blood_pressure' in vital_signs:
            bp = vital_signs['blood_pressure']
            if isinstance(bp, dict):
                systolic = bp.get('systolic', 0)
                diastolic = bp.get('diastolic', 0)
                
                if systolic > 180 or diastolic > 110:
                    analysis['critical_signs'].append('ضغط دم مرتفع خطير')
                    analysis['severity_score'] += 3
                elif systolic < 90 or diastolic < 60:
                    analysis['critical_signs'].append('ضغط دم منخفض خطير')
                    analysis['severity_score'] += 3
                elif systolic > 140 or diastolic > 90:
                    analysis['abnormal_signs'].append('ضغط دم مرتفع')
                    analysis['severity_score'] += 1
        
        # تحليل معدل النبض
        if 'pulse' in vital_signs:
            pulse = vital_signs['pulse']
            if pulse > 120:
                analysis['abnormal_signs'].append('نبض سريع')
                analysis['severity_score'] += 1
                if pulse > 150:
                    analysis['critical_signs'].append('نبض سريع خطير')
                    analysis['severity_score'] += 2
            elif pulse < 60:
                analysis['abnormal_signs'].append('نبض بطيء')
                analysis['severity_score'] += 1
                if pulse < 40:
                    analysis['critical_signs'].append('نبض بطيء خطير')
                    analysis['severity_score'] += 2
        
        # تحليل معدل التنفس
        if 'respiratory_rate' in vital_signs:
            resp_rate = vital_signs['respiratory_rate']
            if resp_rate > 24:
                analysis['abnormal_signs'].append('تنفس سريع')
                analysis['severity_score'] += 1
                if resp_rate > 30:
                    analysis['critical_signs'].append('تنفس سريع خطير')
                    analysis['severity_score'] += 2
            elif resp_rate < 12:
                analysis['abnormal_signs'].append('تنفس بطيء')
                analysis['severity_score'] += 1
                if resp_rate < 8:
                    analysis['critical_signs'].append('تنفس بطيء خطير')
                    analysis['severity_score'] += 3
        
        # تحليل درجة الحرارة
        if 'temperature' in vital_signs:
            temp = vital_signs['temperature']
            if temp > 39:
                analysis['abnormal_signs'].append('حمى عالية')
                analysis['severity_score'] += 1
                if temp > 41:
                    analysis['critical_signs'].append('حمى خطيرة')
                    analysis['severity_score'] += 3
            elif temp < 35:
                analysis['critical_signs'].append('انخفاض درجة الحرارة خطير')
                analysis['severity_score'] += 2
        
        # تحليل مستوى الأكسجين
        if 'oxygen_saturation' in vital_signs:
            o2_sat = vital_signs['oxygen_saturation']
            if o2_sat < 95:
                analysis['abnormal_signs'].append('انخفاض الأكسجين')
                analysis['severity_score'] += 2
                if o2_sat < 90:
                    analysis['critical_signs'].append('انخفاض الأكسجين خطير')
                    analysis['severity_score'] += 3
        
        return analysis
    
    def _determine_urgency_level(self, emergency_type: str, symptoms: List[str], vital_signs: Dict) -> str:
        """تحديد مستوى الإلحاح"""
        # فحص الأعراض الحرجة
        if emergency_type in self.emergency_symptoms:
            type_data = self.emergency_symptoms[emergency_type]
            critical_symptoms = type_data['critical_symptoms']
            
            for symptom in symptoms:
                if symptom in critical_symptoms:
                    return UrgencyLevel.CRITICAL.value
        
        # فحص العلامات الحيوية الحرجة
        vital_analysis = self._analyze_vital_signs(vital_signs)
        if vital_analysis['critical_signs']:
            return UrgencyLevel.CRITICAL.value
        elif vital_analysis['severity_score'] >= 3:
            return UrgencyLevel.URGENT.value
        elif vital_analysis['severity_score'] >= 1:
            return UrgencyLevel.SEMI_URGENT.value
        
        # تحديد الإلحاح بناءً على نوع الطوارئ
        high_priority_types = [
            EmergencyType.CARDIAC.value,
            EmergencyType.RESPIRATORY.value,
            EmergencyType.NEUROLOGICAL.value
        ]
        
        if emergency_type in high_priority_types:
            return UrgencyLevel.URGENT.value
        
        return UrgencyLevel.SEMI_URGENT.value
    
    def _find_nearest_emergency_centers(self, location: Dict, emergency_type: str) -> List[Dict]:
        """العثور على أقرب مراكز الطوارئ"""
        if not location or 'lat' not in location or 'lng' not in location:
            # إرجاع جميع المراكز إذا لم يتم تحديد الموقع
            return sorted(self.emergency_centers, key=lambda x: x['current_load'])
        
        user_lat = location['lat']
        user_lng = location['lng']
        
        # حساب المسافة لكل مركز
        centers_with_distance = []
        for center in self.emergency_centers:
            distance = self._calculate_distance(
                user_lat, user_lng, center['lat'], center['lng']
            )
            
            # فحص التخصصات المناسبة
            specialty_match = self._check_specialty_match(center['specialties'], emergency_type)
            
            center_info = center.copy()
            center_info.update({
                'distance_km': distance,
                'estimated_travel_time': self._estimate_travel_time(distance),
                'specialty_match': specialty_match,
                'availability_score': self._calculate_availability_score(center),
                'priority_score': self._calculate_priority_score(
                    distance, center['current_load'], center['capacity'], specialty_match
                )
            })
            
            centers_with_distance.append(center_info)
        
        # ترتيب المراكز حسب الأولوية
        sorted_centers = sorted(centers_with_distance, 
                              key=lambda x: x['priority_score'], reverse=True)
        
        return sorted_centers[:3]  # أفضل 3 مراكز
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """حساب المسافة بين نقطتين"""
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
    
    def _estimate_travel_time(self, distance_km: float) -> int:
        """تقدير وقت السفر بالدقائق"""
        # افتراض سرعة متوسطة 40 كم/ساعة في المدينة
        average_speed = 40
        time_hours = distance_km / average_speed
        time_minutes = time_hours * 60
        return max(5, int(time_minutes))  # الحد الأدنى 5 دقائق
    
    def _check_specialty_match(self, center_specialties: List[str], emergency_type: str) -> bool:
        """فحص تطابق التخصصات"""
        specialty_mapping = {
            EmergencyType.CARDIAC.value: ['قلب', 'طوارئ عامة'],
            EmergencyType.NEUROLOGICAL.value: ['مخ وأعصاب', 'طوارئ عامة'],
            EmergencyType.OBSTETRIC.value: ['نساء وولادة', 'طوارئ عامة'],
            EmergencyType.TRAUMA.value: ['جراحة', 'طوارئ عامة'],
            EmergencyType.POISONING.value: ['سموم', 'طوارئ عامة']
        }
        
        required_specialties = specialty_mapping.get(emergency_type, ['طوارئ عامة'])
        
        return any(specialty in center_specialties for specialty in required_specialties)
    
    def _calculate_availability_score(self, center: Dict) -> float:
        """حساب نقاط التوفر"""
        load_percentage = center['current_load'] / center['capacity']
        return 1 - load_percentage  # كلما قل الحمل، زادت النقاط
    
    def _calculate_priority_score(self, distance: float, current_load: int, 
                                capacity: int, specialty_match: bool) -> float:
        """حساب نقاط الأولوية"""
        # نقاط المسافة (كلما قلت المسافة، زادت النقاط)
        distance_score = max(0, 10 - distance)  # الحد الأقصى 10 نقاط
        
        # نقاط التوفر
        availability_score = ((capacity - current_load) / capacity) * 5
        
        # نقاط التخصص
        specialty_score = 3 if specialty_match else 0
        
        return distance_score + availability_score + specialty_score
    
    def _create_response_plan(self, emergency_call: EmergencyCall, 
                            analysis: Dict, nearest_centers: List[Dict]) -> Dict:
        """إنشاء خطة الاستجابة"""
        best_center = nearest_centers[0] if nearest_centers else None
        
        response_plan = {
            'plan_id': str(uuid.uuid4()),
            'emergency_call_id': emergency_call.call_id,
            'response_type': self._determine_response_type(emergency_call.urgency_level),
            'assigned_center': best_center,
            'estimated_arrival_time': best_center['estimated_travel_time'] if best_center else 30,
            'response_team': self._assign_response_team(analysis['emergency_type']),
            'equipment_needed': self._determine_equipment_needed(analysis['emergency_type']),
            'transport_method': self._determine_transport_method(emergency_call.urgency_level),
            'hospital_notification': best_center is not None,
            'created_at': datetime.now().isoformat()
        }
        
        return response_plan
    
    def _determine_response_type(self, urgency_level: str) -> str:
        """تحديد نوع الاستجابة"""
        if urgency_level == UrgencyLevel.CRITICAL.value:
            return 'استجابة طوارئ فورية'
        elif urgency_level == UrgencyLevel.URGENT.value:
            return 'استجابة عاجلة'
        else:
            return 'استجابة عادية'
    
    def _assign_response_team(self, emergency_type: str) -> List[str]:
        """تحديد فريق الاستجابة"""
        team_assignments = {
            EmergencyType.CARDIAC.value: ['طبيب طوارئ', 'ممرض متخصص', 'فني إسعاف'],
            EmergencyType.RESPIRATORY.value: ['طبيب طوارئ', 'أخصائي تنفس', 'فني إسعاف'],
            EmergencyType.NEUROLOGICAL.value: ['طبيب أعصاب', 'ممرض متخصص', 'فني إسعاف'],
            EmergencyType.TRAUMA.value: ['جراح طوارئ', 'ممرض جراحة', 'فني إسعاف'],
            EmergencyType.OBSTETRIC.value: ['طبيب نساء وولادة', 'قابلة', 'فني إسعاف']
        }
        
        return team_assignments.get(emergency_type, ['طبيب طوارئ', 'فني إسعاف'])
    
    def _determine_equipment_needed(self, emergency_type: str) -> List[str]:
        """تحديد المعدات المطلوبة"""
        equipment_mapping = {
            EmergencyType.CARDIAC.value: ['جهاز صدمات', 'أدوية قلبية', 'أكسجين', 'مراقب قلب'],
            EmergencyType.RESPIRATORY.value: ['جهاز تنفس صناعي', 'أكسجين', 'أدوية موسعة شعب'],
            EmergencyType.NEUROLOGICAL.value: ['مراقب أعصاب', 'أدوية أعصاب', 'مثبت رقبة'],
            EmergencyType.TRAUMA.value: ['مثبتات كسور', 'ضمادات', 'سوائل وريدية', 'مسكنات'],
            EmergencyType.POISONING.value: ['فحم نشط', 'مضادات سموم', 'غسيل معدة']
        }
        
        return equipment_mapping.get(emergency_type, ['معدات إسعاف أساسية'])
    
    def _determine_transport_method(self, urgency_level: str) -> str:
        """تحديد وسيلة النقل"""
        if urgency_level == UrgencyLevel.CRITICAL.value:
            return 'إسعاف متقدم مع طبيب'
        elif urgency_level == UrgencyLevel.URGENT.value:
            return 'إسعاف عادي'
        else:
            return 'نقل طبي عادي'
    
    def _send_emergency_alerts(self, emergency_call: EmergencyCall, 
                             response_plan: Dict) -> Dict:
        """إرسال تنبيهات الطوارئ"""
        alerts_sent = {
            'ambulance_dispatch': False,
            'hospital_notification': False,
            'family_notification': False,
            'doctor_notification': False
        }
        
        try:
            # إرسال تنبيه لمركز الإسعاف
            if response_plan['assigned_center']:
                alerts_sent['ambulance_dispatch'] = True
                current_app.logger.info(f"تم إرسال تنبيه الإسعاف للمركز {response_plan['assigned_center']['name']}")
            
            # إرسال تنبيه للمستشفى
            if response_plan['hospital_notification']:
                alerts_sent['hospital_notification'] = True
                current_app.logger.info("تم إرسال تنبيه للمستشفى")
            
            # إرسال تنبيه للعائلة (إذا توفرت معلومات الاتصال)
            if emergency_call.caller_info.get('emergency_contact'):
                alerts_sent['family_notification'] = True
                current_app.logger.info("تم إرسال تنبيه للعائلة")
            
            # إرسال تنبيه للطبيب المعالج (إذا توفر)
            if emergency_call.patient_id:
                alerts_sent['doctor_notification'] = True
                current_app.logger.info("تم إرسال تنبيه للطبيب المعالج")
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال التنبيهات: {str(e)}")
        
        return alerts_sent
    
    def _get_immediate_instructions(self, analysis: Dict) -> List[str]:
        """الحصول على التعليمات الفورية"""
        emergency_type = analysis['emergency_type']
        
        if emergency_type in self.emergency_symptoms:
            return self.emergency_symptoms[emergency_type]['first_aid']
        
        # تعليمات عامة
        return [
            'حافظ على هدوئك',
            'تأكد من سلامة المكان',
            'لا تحرك المريض إلا إذا كان في خطر',
            'راقب التنفس والنبض',
            'ابق مع المريض حتى وصول الإسعاف'
        ]
    
    def get_first_aid_guide(self, emergency_type: str = None, symptom: str = None) -> Dict:
        """
        الحصول على دليل الإسعافات الأولية
        
        Args:
            emergency_type: نوع الطوارئ
            symptom: العرض المحدد
            
        Returns:
            Dict: دليل الإسعافات الأولية
        """
        try:
            if emergency_type and emergency_type in self.emergency_symptoms:
                emergency_data = self.emergency_symptoms[emergency_type]
                
                return {
                    'success': True,
                    'emergency_type': emergency_type,
                    'critical_symptoms': emergency_data['critical_symptoms'],
                    'warning_signs': emergency_data['warning_signs'],
                    'first_aid_steps': emergency_data['first_aid'],
                    'when_to_call_911': 'فوراً عند ظهور أي من الأعراض الحرجة',
                    'what_not_to_do': self._get_what_not_to_do(emergency_type)
                }
            
            elif symptom:
                # البحث عن العرض في جميع أنواع الطوارئ
                matching_emergencies = []
                for emer_type, data in self.emergency_symptoms.items():
                    if (symptom in data['critical_symptoms'] or 
                        symptom in data['warning_signs']):
                        matching_emergencies.append({
                            'emergency_type': emer_type,
                            'first_aid': data['first_aid'],
                            'severity': 'حرج' if symptom in data['critical_symptoms'] else 'تحذيري'
                        })
                
                return {
                    'success': True,
                    'symptom': symptom,
                    'matching_emergencies': matching_emergencies,
                    'general_advice': 'إذا كان العرض شديداً، اتصل بالإسعاف فوراً'
                }
            
            else:
                # إرجاع دليل عام
                return {
                    'success': True,
                    'general_first_aid': self.first_aid_protocols,
                    'emergency_numbers': self.emergency_numbers,
                    'general_principles': [
                        'تأكد من سلامة المكان أولاً',
                        'اتصل بالإسعاف إذا كانت الحالة خطيرة',
                        'لا تحرك المصاب إلا إذا كان في خطر',
                        'حافظ على هدوئك وطمئن المصاب',
                        'راقب العلامات الحيوية'
                    ]
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_what_not_to_do(self, emergency_type: str) -> List[str]:
        """ما يجب تجنبه في كل نوع طوارئ"""
        what_not_to_do = {
            EmergencyType.CARDIAC.value: [
                'لا تترك المريض وحده',
                'لا تعط الماء أو الطعام',
                'لا تجعل المريض يمشي'
            ],
            EmergencyType.RESPIRATORY.value: [
                'لا تضع المريض مستلقياً',
                'لا تعط أي أدوية بدون وصفة',
                'لا تترك المريض وحده'
            ],
            EmergencyType.NEUROLOGICAL.value: [
                'لا تحرك الرأس أو الرقبة',
                'لا تعط أي طعام أو شراب',
                'لا تضع أي شيء في فم المريض أثناء التشنج'
            ],
            EmergencyType.TRAUMA.value: [
                'لا تحرك المصاب إلا إذا كان في خطر',
                'لا تزل الأجسام الغريبة من الجروح العميقة',
                'لا تعط مسكنات بدون استشارة طبية'
            ],
            EmergencyType.POISONING.value: [
                'لا تحفز القيء بدون توجيه طبي',
                'لا تعط اللبن أو الزيت',
                'لا تترك المريض وحده'
            ]
        }
        
        return what_not_to_do.get(emergency_type, ['اتبع التعليمات الطبية'])
    
    def track_emergency_status(self, call_id: str) -> Dict:
        """
        تتبع حالة الطوارئ
        
        Args:
            call_id: معرف استدعاء الطوارئ
            
        Returns:
            Dict: حالة الطوارئ
        """
        try:
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            # هنا محاكاة لتتبع الحالة
            
            status_updates = [
                {
                    'timestamp': datetime.now() - timedelta(minutes=10),
                    'status': EmergencyStatus.REPORTED.value,
                    'description': 'تم استلام البلاغ وتحليل الحالة',
                    'location': 'مركز الطوارئ'
                },
                {
                    'timestamp': datetime.now() - timedelta(minutes=8),
                    'status': EmergencyStatus.DISPATCHED.value,
                    'description': 'تم إرسال سيارة الإسعاف',
                    'location': 'في الطريق',
                    'estimated_arrival': '5 دقائق'
                },
                {
                    'timestamp': datetime.now() - timedelta(minutes=3),
                    'status': EmergencyStatus.ON_SCENE.value,
                    'description': 'وصل فريق الإسعاف للموقع',
                    'location': 'موقع الحادث'
                }
            ]
            
            current_status = status_updates[-1]
            
            return {
                'success': True,
                'call_id': call_id,
                'current_status': current_status['status'],
                'last_update': current_status['timestamp'].isoformat(),
                'description': current_status['description'],
                'location': current_status['location'],
                'estimated_arrival': current_status.get('estimated_arrival'),
                'status_history': status_updates,
                'next_expected_update': 'خلال 5 دقائق'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_emergency_statistics(self, period_days: int = 30) -> Dict:
        """
        الحصول على إحصائيات الطوارئ
        
        Args:
            period_days: فترة الإحصائيات بالأيام
            
        Returns:
            Dict: إحصائيات الطوارئ
        """
        try:
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            # هنا محاكاة للإحصائيات
            
            statistics = {
                'period': {
                    'start_date': (datetime.now() - timedelta(days=period_days)).date().isoformat(),
                    'end_date': datetime.now().date().isoformat(),
                    'days': period_days
                },
                'total_calls': 1250,
                'calls_by_urgency': {
                    UrgencyLevel.CRITICAL.value: 125,
                    UrgencyLevel.URGENT.value: 375,
                    UrgencyLevel.SEMI_URGENT.value: 500,
                    UrgencyLevel.NON_URGENT.value: 250
                },
                'calls_by_type': {
                    EmergencyType.CARDIAC.value: 200,
                    EmergencyType.RESPIRATORY.value: 150,
                    EmergencyType.TRAUMA.value: 300,
                    EmergencyType.NEUROLOGICAL.value: 100,
                    EmergencyType.GENERAL.value: 500
                },
                'response_times': {
                    'average_response_time': 8.5,  # دقائق
                    'median_response_time': 7.0,
                    'fastest_response': 3.0,
                    'slowest_response': 25.0
                },
                'outcomes': {
                    'successful_interventions': 1180,
                    'transported_to_hospital': 950,
                    'treated_on_scene': 230,
                    'false_alarms': 70
                },
                'busiest_hours': [
                    {'hour': '14:00-15:00', 'calls': 85},
                    {'hour': '20:00-21:00', 'calls': 78},
                    {'hour': '10:00-11:00', 'calls': 72}
                ],
                'busiest_days': [
                    {'day': 'الجمعة', 'calls': 220},
                    {'day': 'السبت', 'calls': 200},
                    {'day': 'الأحد', 'calls': 180}
                ],
                'center_performance': [
                    {
                        'center_name': 'مستشفى قصر العيني',
                        'calls_handled': 450,
                        'average_response_time': 7.2,
                        'success_rate': 96.5
                    },
                    {
                        'center_name': 'مستشفى عين شمس',
                        'calls_handled': 380,
                        'average_response_time': 8.8,
                        'success_rate': 94.8
                    }
                ]
            }
            
            return {
                'success': True,
                'statistics': statistics,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

