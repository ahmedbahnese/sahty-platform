"""
خدمة دعم الحوامل ومتابعة الحمل
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, date
from flask import current_app
from dataclasses import dataclass
from enum import Enum
import calendar

class PregnancyStage(Enum):
    FIRST_TRIMESTER = "الثلث الأول"  # 1-12 أسبوع
    SECOND_TRIMESTER = "الثلث الثاني"  # 13-27 أسبوع
    THIRD_TRIMESTER = "الثلث الثالث"  # 28-40 أسبوع
    POSTPARTUM = "ما بعد الولادة"

class RiskLevel(Enum):
    LOW = "منخفض"
    MODERATE = "متوسط"
    HIGH = "عالي"
    CRITICAL = "حرج"

class AppointmentType(Enum):
    ROUTINE_CHECKUP = "فحص دوري"
    ULTRASOUND = "سونار"
    BLOOD_TEST = "تحليل دم"
    GLUCOSE_TEST = "فحص السكر"
    SPECIALIST_CONSULTATION = "استشارة متخصص"
    EMERGENCY = "طوارئ"

@dataclass
class PregnancyProfile:
    user_id: str
    pregnancy_id: str
    last_menstrual_period: date
    expected_due_date: date
    current_week: int
    current_trimester: str
    is_first_pregnancy: bool
    previous_pregnancies: int
    previous_complications: List[str]
    current_complications: List[str]
    blood_type: str
    allergies: List[str]
    medications: List[str]
    risk_level: str
    doctor_id: Optional[str]
    hospital_id: Optional[str]
    emergency_contact: Dict
    created_at: datetime
    last_updated: datetime

@dataclass
class PregnancyAppointment:
    appointment_id: str
    user_id: str
    appointment_type: str
    scheduled_date: datetime
    doctor_id: str
    hospital_id: str
    notes: str
    completed: bool
    results: Dict
    next_appointment_recommended: Optional[datetime]

@dataclass
class PregnancySymptom:
    symptom_id: str
    user_id: str
    symptom_name: str
    severity: int  # 1-10
    description: str
    date_reported: datetime
    week_of_pregnancy: int
    requires_attention: bool
    doctor_notified: bool

@dataclass
class BabyDevelopment:
    week: int
    size_description: str
    weight_grams: float
    length_cm: float
    development_milestones: List[str]
    organs_developing: List[str]
    mother_changes: List[str]
    tips_for_week: List[str]

class PregnancySupportService:
    def __init__(self):
        """تهيئة خدمة دعم الحوامل"""
        
        # إعدادات الخدمة
        self.service_settings = {
            'pregnancy_duration_weeks': 40,
            'high_risk_age_threshold': 35,
            'appointment_reminder_days': [7, 3, 1],
            'emergency_symptoms_threshold': 8,
            'weight_gain_limits': {
                'underweight': {'min': 12.5, 'max': 18},
                'normal': {'min': 11.5, 'max': 16},
                'overweight': {'min': 7, 'max': 11.5},
                'obese': {'min': 5, 'max': 9}
            },
            'vital_signs_ranges': {
                'blood_pressure_systolic': {'min': 90, 'max': 140},
                'blood_pressure_diastolic': {'min': 60, 'max': 90},
                'heart_rate': {'min': 60, 'max': 100},
                'temperature': {'min': 36.1, 'max': 37.2}
            }
        }
        
        # جدول تطور الجنين أسبوعياً
        self.baby_development_timeline = {
            4: BabyDevelopment(
                week=4,
                size_description="بحجم بذرة الخشخاش",
                weight_grams=0.1,
                length_cm=0.2,
                development_milestones=["بداية تكوين الجهاز العصبي", "تكوين القلب البدائي"],
                organs_developing=["الجهاز العصبي", "القلب"],
                mother_changes=["قد تشعرين بأعراض الحمل المبكرة", "تأخر الدورة الشهرية"],
                tips_for_week=["ابدئي بتناول حمض الفوليك", "تجنبي الكحول والتدخين"]
            ),
            8: BabyDevelopment(
                week=8,
                size_description="بحجم حبة التوت",
                weight_grams=1.0,
                length_cm=1.6,
                development_milestones=["تكوين الأطراف", "بداية تكوين الوجه"],
                organs_developing=["الأطراف", "الوجه", "الأعضاء الداخلية"],
                mother_changes=["غثيان الصباح", "تغيرات في الثدي"],
                tips_for_week=["تناولي وجبات صغيرة متكررة", "اشربي الكثير من الماء"]
            ),
            12: BabyDevelopment(
                week=12,
                size_description="بحجم حبة الليمون",
                weight_grams=14.0,
                length_cm=5.4,
                development_milestones=["تكوين الأظافر", "بداية حركة الجنين"],
                organs_developing=["الكلى", "الأمعاء", "العظام"],
                mother_changes=["تحسن الغثيان", "زيادة الطاقة"],
                tips_for_week=["موعد أول فحص سونار", "يمكن إخبار الآخرين بالحمل"]
            ),
            16: BabyDevelopment(
                week=16,
                size_description="بحجم حبة الأفوكادو",
                weight_grams=100.0,
                length_cm=11.6,
                development_milestones=["تطور السمع", "نمو الشعر"],
                organs_developing=["الجهاز السمعي", "الجهاز التناسلي"],
                mother_changes=["بداية الشعور بحركة الجنين", "نمو البطن"],
                tips_for_week=["ابدئي بتمارين الحمل الآمنة", "تناولي الكالسيوم"]
            ),
            20: BabyDevelopment(
                week=20,
                size_description="بحجم حبة الموز",
                weight_grams=300.0,
                length_cm=16.4,
                development_milestones=["تطور الحواس", "نمو الدماغ"],
                organs_developing=["الدماغ", "الرئتين", "الجهاز الهضمي"],
                mother_changes=["حركة الجنين واضحة", "تغيرات في الجلد"],
                tips_for_week=["فحص السونار التفصيلي", "يمكن معرفة جنس الجنين"]
            ),
            24: BabyDevelopment(
                week=24,
                size_description="بحجم كوز الذرة",
                weight_grams=600.0,
                length_cm=21.0,
                development_milestones=["تطور الرئتين", "استجابة للأصوات"],
                organs_developing=["الرئتين", "الجهاز المناعي"],
                mother_changes=["زيادة الوزن", "ضيق في التنفس أحياناً"],
                tips_for_week=["فحص السكر", "مراقبة ضغط الدم"]
            ),
            28: BabyDevelopment(
                week=28,
                size_description="بحجم الباذنجان",
                weight_grams=1000.0,
                length_cm=25.0,
                development_milestones=["فتح وإغلاق العينين", "تطور الذاكرة"],
                organs_developing=["العينين", "الدماغ", "الجهاز العصبي"],
                mother_changes=["صعوبة في النوم", "آلام الظهر"],
                tips_for_week=["ابدئي دروس الولادة", "تحضيري لإجازة الأمومة"]
            ),
            32: BabyDevelopment(
                week=32,
                size_description="بحجم جوز الهند",
                weight_grams=1700.0,
                length_cm=28.0,
                development_milestones=["تطور المناعة", "تراكم الدهون"],
                organs_developing=["الجهاز المناعي", "الجلد"],
                mother_changes=["ضيق التنفس", "حرقة المعدة"],
                tips_for_week=["مراقبة حركة الجنين", "تحضير حقيبة المستشفى"]
            ),
            36: BabyDevelopment(
                week=36,
                size_description="بحجم الخس الروماني",
                weight_grams=2600.0,
                length_cm=32.0,
                development_milestones=["اكتمال نمو الرئتين", "استعداد للولادة"],
                organs_developing=["الرئتين", "الكبد"],
                mother_changes=["نزول الجنين للحوض", "زيادة التبول"],
                tips_for_week=["فحوصات أسبوعية", "مراقبة علامات الولادة"]
            ),
            40: BabyDevelopment(
                week=40,
                size_description="بحجم البطيخ الصغير",
                weight_grams=3400.0,
                length_cm=36.0,
                development_milestones=["اكتمال النمو", "جاهز للولادة"],
                organs_developing=["جميع الأعضاء مكتملة"],
                mother_changes=["استعداد للولادة", "انقباضات منتظمة"],
                tips_for_week=["مراقبة علامات الولادة", "التوجه للمستشفى عند الحاجة"]
            )
        }
        
        # الأعراض الطبيعية والخطيرة
        self.pregnancy_symptoms = {
            'normal_symptoms': {
                'الثلث الأول': [
                    'غثيان الصباح', 'تعب وإرهاق', 'تغيرات في الثدي',
                    'كثرة التبول', 'تغيرات مزاجية', 'حساسية للروائح'
                ],
                'الثلث الثاني': [
                    'نمو البطن', 'حركة الجنين', 'حرقة المعدة',
                    'آلام الظهر الخفيفة', 'تورم خفيف في القدمين'
                ],
                'الثلث الثالث': [
                    'ضيق التنفس', 'صعوبة النوم', 'كثرة التبول',
                    'انقباضات براكستون هيكس', 'آلام الحوض'
                ]
            },
            'warning_symptoms': [
                'نزيف مهبلي', 'آلام شديدة في البطن', 'صداع شديد مستمر',
                'تورم مفاجئ في الوجه واليدين', 'قيء شديد مستمر',
                'حمى عالية', 'عدم الشعور بحركة الجنين', 'تسرب السائل الأمنيوسي',
                'تشنجات شديدة', 'اضطرابات في الرؤية'
            ]
        }
        
        # الفحوصات المطلوبة حسب الأسبوع
        self.required_tests = {
            6: ['فحص الحمل', 'تحليل دم شامل', 'فحص البول'],
            8: ['فحص الغدة الدرقية', 'فحص الأجسام المضادة'],
            12: ['سونار الثلث الأول', 'فحص الشفافية القفوية'],
            16: ['فحص الألفا فيتو بروتين', 'فحص التشوهات'],
            20: ['سونار تفصيلي', 'فحص تشوهات الجنين'],
            24: ['فحص السكر', 'تحليل دم شامل'],
            28: ['فحص الأجسام المضادة', 'حقنة الروجام إذا لزم'],
            32: ['سونار نمو الجنين', 'فحص ضغط الدم'],
            36: ['فحص البكتيريا العقدية', 'تقييم وضعية الجنين'],
            38: ['فحص عنق الرحم', 'مراقبة الجنين']
        }
        
        # النصائح الغذائية
        self.nutrition_guidelines = {
            'essential_nutrients': {
                'حمض الفوليك': {
                    'amount': '400-800 ميكروجرام يومياً',
                    'sources': ['الخضروات الورقية', 'البقوليات', 'الحبوب المدعمة'],
                    'importance': 'منع تشوهات الأنبوب العصبي'
                },
                'الحديد': {
                    'amount': '27 مجم يومياً',
                    'sources': ['اللحوم الحمراء', 'السبانخ', 'البقوليات'],
                    'importance': 'منع فقر الدم'
                },
                'الكالسيوم': {
                    'amount': '1000 مجم يومياً',
                    'sources': ['منتجات الألبان', 'السمسم', 'الخضروات الورقية'],
                    'importance': 'تطوير عظام وأسنان الجنين'
                },
                'أوميجا 3': {
                    'amount': '200-300 مجم يومياً',
                    'sources': ['الأسماك الدهنية', 'الجوز', 'بذور الكتان'],
                    'importance': 'تطوير دماغ وعيون الجنين'
                }
            },
            'foods_to_avoid': [
                'الأسماك عالية الزئبق', 'اللحوم النيئة أو غير المطبوخة جيداً',
                'البيض النيء', 'الأجبان الطرية غير المبسترة', 'الكحول',
                'الكافيين الزائد', 'الأطعمة المصنعة بكثرة'
            ],
            'safe_foods': [
                'الفواكه والخضروات المغسولة', 'اللحوم المطبوخة جيداً',
                'منتجات الألبان المبسترة', 'الحبوب الكاملة', 'المكسرات',
                'الأسماك قليلة الزئبق'
            ]
        }
        
        # تمارين الحمل الآمنة
        self.safe_exercises = {
            'الثلث الأول': [
                'المشي', 'السباحة', 'اليوجا المعدلة', 'تمارين التنفس',
                'تمارين الإطالة الخفيفة'
            ],
            'الثلث الثاني': [
                'المشي', 'السباحة', 'تمارين القوة الخفيفة',
                'تمارين الحوض', 'اليوجا للحوامل'
            ],
            'الثلث الثالث': [
                'المشي الخفيف', 'تمارين التنفس', 'تمارين كيجل',
                'تمارين الإطالة', 'تحضير للولادة'
            ]
        }
        
        # قاعدة بيانات الحوامل (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.pregnancy_profiles = {}
        self.pregnancy_appointments = {}
        self.pregnancy_symptoms_log = {}
        self.pregnancy_analytics = {}
    
    def create_pregnancy_profile(self, user_id: str, profile_data: Dict) -> Dict:
        """
        إنشاء ملف حمل جديد
        
        Args:
            user_id: معرف المستخدم
            profile_data: بيانات الحمل
            
        Returns:
            Dict: نتيجة الإنشاء
        """
        try:
            # التحقق من صحة البيانات
            required_fields = ['last_menstrual_period', 'blood_type']
            for field in required_fields:
                if field not in profile_data:
                    return {
                        'success': False,
                        'error': f'الحقل {field} مطلوب'
                    }
            
            # تحويل تاريخ آخر دورة شهرية
            lmp_str = profile_data['last_menstrual_period']
            lmp_date = datetime.strptime(lmp_str, '%Y-%m-%d').date()
            
            # حساب تاريخ الولادة المتوقع (280 يوم من آخر دورة)
            expected_due_date = lmp_date + timedelta(days=280)
            
            # حساب الأسبوع الحالي
            current_week = self._calculate_pregnancy_week(lmp_date)
            
            # تحديد الثلث الحالي
            current_trimester = self._determine_trimester(current_week)
            
            # تقييم مستوى الخطورة
            risk_level = self._assess_pregnancy_risk(profile_data, current_week)
            
            # إنشاء معرف الحمل
            pregnancy_id = str(uuid.uuid4())
            
            # إنشاء الملف
            pregnancy_profile = PregnancyProfile(
                user_id=user_id,
                pregnancy_id=pregnancy_id,
                last_menstrual_period=lmp_date,
                expected_due_date=expected_due_date,
                current_week=current_week,
                current_trimester=current_trimester,
                is_first_pregnancy=profile_data.get('is_first_pregnancy', True),
                previous_pregnancies=profile_data.get('previous_pregnancies', 0),
                previous_complications=profile_data.get('previous_complications', []),
                current_complications=profile_data.get('current_complications', []),
                blood_type=profile_data['blood_type'],
                allergies=profile_data.get('allergies', []),
                medications=profile_data.get('medications', []),
                risk_level=risk_level,
                doctor_id=profile_data.get('doctor_id'),
                hospital_id=profile_data.get('hospital_id'),
                emergency_contact=profile_data.get('emergency_contact', {}),
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            # حفظ الملف
            self.pregnancy_profiles[user_id] = pregnancy_profile
            
            # إنشاء جدول المواعيد الموصى بها
            recommended_appointments = self._generate_appointment_schedule(pregnancy_profile)
            
            # إنشاء خطة المتابعة
            follow_up_plan = self._create_follow_up_plan(pregnancy_profile)
            
            return {
                'success': True,
                'pregnancy_id': pregnancy_id,
                'current_week': current_week,
                'current_trimester': current_trimester,
                'expected_due_date': expected_due_date.isoformat(),
                'risk_level': risk_level,
                'recommended_appointments': recommended_appointments,
                'follow_up_plan': follow_up_plan,
                'message': 'تم إنشاء ملف الحمل بنجاح! مبروك على الحمل 🤱'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء ملف الحمل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء ملف الحمل'
            }
    
    def get_weekly_update(self, user_id: str) -> Dict:
        """
        الحصول على التحديث الأسبوعي للحمل
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: التحديث الأسبوعي
        """
        try:
            if user_id not in self.pregnancy_profiles:
                return {
                    'success': False,
                    'error': 'ملف الحمل غير موجود'
                }
            
            profile = self.pregnancy_profiles[user_id]
            current_week = self._calculate_pregnancy_week(profile.last_menstrual_period)
            
            # تحديث الأسبوع الحالي
            profile.current_week = current_week
            profile.current_trimester = self._determine_trimester(current_week)
            profile.last_updated = datetime.now()
            
            # الحصول على معلومات تطور الجنين
            baby_development = self._get_baby_development_info(current_week)
            
            # الحصول على النصائح الأسبوعية
            weekly_tips = self._get_weekly_tips(current_week, profile)
            
            # الحصول على الأعراض المتوقعة
            expected_symptoms = self._get_expected_symptoms(current_week)
            
            # الحصول على الفحوصات المطلوبة
            required_tests = self._get_required_tests(current_week)
            
            # حساب الأيام المتبقية
            days_remaining = (profile.expected_due_date - date.today()).days
            
            return {
                'success': True,
                'current_week': current_week,
                'current_trimester': profile.current_trimester,
                'days_remaining': days_remaining,
                'baby_development': baby_development,
                'weekly_tips': weekly_tips,
                'expected_symptoms': expected_symptoms,
                'required_tests': required_tests,
                'next_appointment': self._get_next_appointment(user_id)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على التحديث الأسبوعي: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على التحديث'
            }
    
    def log_symptom(self, user_id: str, symptom_data: Dict) -> Dict:
        """
        تسجيل عرض جديد
        
        Args:
            user_id: معرف المستخدم
            symptom_data: بيانات العرض
            
        Returns:
            Dict: نتيجة التسجيل
        """
        try:
            if user_id not in self.pregnancy_profiles:
                return {
                    'success': False,
                    'error': 'ملف الحمل غير موجود'
                }
            
            profile = self.pregnancy_profiles[user_id]
            
            # التحقق من صحة البيانات
            required_fields = ['symptom_name', 'severity']
            for field in required_fields:
                if field not in symptom_data:
                    return {
                        'success': False,
                        'error': f'الحقل {field} مطلوب'
                    }
            
            # إنشاء العرض
            symptom = PregnancySymptom(
                symptom_id=str(uuid.uuid4()),
                user_id=user_id,
                symptom_name=symptom_data['symptom_name'],
                severity=symptom_data['severity'],
                description=symptom_data.get('description', ''),
                date_reported=datetime.now(),
                week_of_pregnancy=profile.current_week,
                requires_attention=False,
                doctor_notified=False
            )
            
            # تقييم العرض
            assessment = self._assess_symptom(symptom, profile)
            symptom.requires_attention = assessment['requires_attention']
            
            # حفظ العرض
            if user_id not in self.pregnancy_symptoms_log:
                self.pregnancy_symptoms_log[user_id] = []
            self.pregnancy_symptoms_log[user_id].append(symptom)
            
            # إشعار الطبيب إذا لزم الأمر
            if assessment['requires_attention']:
                self._notify_doctor_about_symptom(user_id, symptom)
                symptom.doctor_notified = True
            
            return {
                'success': True,
                'symptom_id': symptom.symptom_id,
                'assessment': assessment,
                'recommendations': assessment['recommendations'],
                'requires_medical_attention': assessment['requires_attention']
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تسجيل العرض: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تسجيل العرض'
            }
    
    def schedule_appointment(self, user_id: str, appointment_data: Dict) -> Dict:
        """
        جدولة موعد طبي
        
        Args:
            user_id: معرف المستخدم
            appointment_data: بيانات الموعد
            
        Returns:
            Dict: نتيجة الجدولة
        """
        try:
            if user_id not in self.pregnancy_profiles:
                return {
                    'success': False,
                    'error': 'ملف الحمل غير موجود'
                }
            
            profile = self.pregnancy_profiles[user_id]
            
            # التحقق من صحة البيانات
            required_fields = ['appointment_type', 'scheduled_date']
            for field in required_fields:
                if field not in appointment_data:
                    return {
                        'success': False,
                        'error': f'الحقل {field} مطلوب'
                    }
            
            # تحويل التاريخ
            scheduled_date = datetime.fromisoformat(appointment_data['scheduled_date'])
            
            # إنشاء الموعد
            appointment = PregnancyAppointment(
                appointment_id=str(uuid.uuid4()),
                user_id=user_id,
                appointment_type=appointment_data['appointment_type'],
                scheduled_date=scheduled_date,
                doctor_id=appointment_data.get('doctor_id', profile.doctor_id),
                hospital_id=appointment_data.get('hospital_id', profile.hospital_id),
                notes=appointment_data.get('notes', ''),
                completed=False,
                results={},
                next_appointment_recommended=None
            )
            
            # حفظ الموعد
            if user_id not in self.pregnancy_appointments:
                self.pregnancy_appointments[user_id] = []
            self.pregnancy_appointments[user_id].append(appointment)
            
            # إنشاء تذكيرات
            reminders = self._create_appointment_reminders(appointment)
            
            # تحضير قائمة الفحوصات المطلوبة
            preparation_instructions = self._get_appointment_preparation(appointment.appointment_type)
            
            return {
                'success': True,
                'appointment_id': appointment.appointment_id,
                'scheduled_date': scheduled_date.isoformat(),
                'appointment_type': appointment.appointment_type,
                'reminders': reminders,
                'preparation_instructions': preparation_instructions,
                'message': 'تم حجز الموعد بنجاح!'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في جدولة الموعد: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في جدولة الموعد'
            }
    
    def get_nutrition_plan(self, user_id: str) -> Dict:
        """
        الحصول على خطة التغذية للحامل
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: خطة التغذية
        """
        try:
            if user_id not in self.pregnancy_profiles:
                return {
                    'success': False,
                    'error': 'ملف الحمل غير موجود'
                }
            
            profile = self.pregnancy_profiles[user_id]
            
            # خطة التغذية حسب الثلث
            nutrition_plan = {
                'essential_nutrients': self.nutrition_guidelines['essential_nutrients'],
                'daily_meal_plan': self._create_daily_meal_plan(profile),
                'foods_to_avoid': self.nutrition_guidelines['foods_to_avoid'],
                'safe_foods': self.nutrition_guidelines['safe_foods'],
                'hydration_guidelines': self._get_hydration_guidelines(profile),
                'weight_gain_targets': self._calculate_weight_gain_targets(profile),
                'supplements_recommended': self._get_recommended_supplements(profile)
            }
            
            # نصائح خاصة حسب الثلث
            trimester_specific_tips = self._get_trimester_nutrition_tips(profile.current_trimester)
            
            return {
                'success': True,
                'current_week': profile.current_week,
                'current_trimester': profile.current_trimester,
                'nutrition_plan': nutrition_plan,
                'trimester_specific_tips': trimester_specific_tips,
                'calorie_needs': self._calculate_calorie_needs(profile)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على خطة التغذية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على خطة التغذية'
            }
    
    def get_exercise_plan(self, user_id: str) -> Dict:
        """
        الحصول على خطة التمارين للحامل
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: خطة التمارين
        """
        try:
            if user_id not in self.pregnancy_profiles:
                return {
                    'success': False,
                    'error': 'ملف الحمل غير موجود'
                }
            
            profile = self.pregnancy_profiles[user_id]
            
            # التمارين الآمنة حسب الثلث
            safe_exercises = self.safe_exercises.get(profile.current_trimester, [])
            
            # خطة التمارين الأسبوعية
            weekly_exercise_plan = self._create_weekly_exercise_plan(profile)
            
            # تمارين خاصة للحمل
            pregnancy_specific_exercises = self._get_pregnancy_specific_exercises(profile.current_trimester)
            
            # تحذيرات وموانع
            exercise_warnings = self._get_exercise_warnings(profile)
            
            return {
                'success': True,
                'current_week': profile.current_week,
                'current_trimester': profile.current_trimester,
                'safe_exercises': safe_exercises,
                'weekly_exercise_plan': weekly_exercise_plan,
                'pregnancy_specific_exercises': pregnancy_specific_exercises,
                'exercise_warnings': exercise_warnings,
                'benefits': self._get_exercise_benefits()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على خطة التمارين: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على خطة التمارين'
            }
    
    def get_birth_preparation_info(self, user_id: str) -> Dict:
        """
        الحصول على معلومات التحضير للولادة
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: معلومات التحضير للولادة
        """
        try:
            if user_id not in self.pregnancy_profiles:
                return {
                    'success': False,
                    'error': 'ملف الحمل غير موجود'
                }
            
            profile = self.pregnancy_profiles[user_id]
            
            # معلومات التحضير حسب الأسبوع
            if profile.current_week < 28:
                preparation_stage = "مبكر"
            elif profile.current_week < 36:
                preparation_stage = "متوسط"
            else:
                preparation_stage = "متقدم"
            
            preparation_info = {
                'preparation_stage': preparation_stage,
                'birth_plan_checklist': self._get_birth_plan_checklist(profile),
                'hospital_bag_checklist': self._get_hospital_bag_checklist(),
                'labor_signs': self._get_labor_signs(),
                'breathing_techniques': self._get_breathing_techniques(),
                'pain_management_options': self._get_pain_management_options(),
                'postpartum_preparation': self._get_postpartum_preparation(),
                'breastfeeding_preparation': self._get_breastfeeding_preparation()
            }
            
            # دروس الولادة الموصى بها
            recommended_classes = self._get_recommended_birth_classes(profile)
            
            return {
                'success': True,
                'current_week': profile.current_week,
                'weeks_remaining': 40 - profile.current_week,
                'preparation_info': preparation_info,
                'recommended_classes': recommended_classes,
                'emergency_contacts': self._get_emergency_contacts(profile)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على معلومات التحضير للولادة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على المعلومات'
            }
    
    def assess_pregnancy_risk(self, user_id: str) -> Dict:
        """
        تقييم مخاطر الحمل
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: تقييم المخاطر
        """
        try:
            if user_id not in self.pregnancy_profiles:
                return {
                    'success': False,
                    'error': 'ملف الحمل غير موجود'
                }
            
            profile = self.pregnancy_profiles[user_id]
            
            # عوامل الخطر
            risk_factors = []
            risk_score = 0
            
            # العمر
            # في التطبيق الحقيقي، سنحصل على العمر من ملف المستخدم
            # age = self._get_user_age(user_id)
            # if age > 35:
            #     risk_factors.append('عمر أكبر من 35 سنة')
            #     risk_score += 2
            
            # التاريخ الطبي
            if profile.previous_complications:
                risk_factors.extend(profile.previous_complications)
                risk_score += len(profile.previous_complications)
            
            if profile.current_complications:
                risk_factors.extend(profile.current_complications)
                risk_score += len(profile.current_complications) * 2
            
            # الحمل المتعدد
            if profile.previous_pregnancies > 4:
                risk_factors.append('حمل متعدد سابق')
                risk_score += 1
            
            # الأعراض الحالية
            if user_id in self.pregnancy_symptoms_log:
                recent_symptoms = [s for s in self.pregnancy_symptoms_log[user_id] 
                                 if s.date_reported > datetime.now() - timedelta(days=7)]
                high_severity_symptoms = [s for s in recent_symptoms if s.severity >= 7]
                if high_severity_symptoms:
                    risk_factors.append('أعراض شديدة حديثة')
                    risk_score += len(high_severity_symptoms)
            
            # تحديد مستوى الخطر
            if risk_score == 0:
                risk_level = RiskLevel.LOW.value
            elif risk_score <= 3:
                risk_level = RiskLevel.MODERATE.value
            elif risk_score <= 6:
                risk_level = RiskLevel.HIGH.value
            else:
                risk_level = RiskLevel.CRITICAL.value
            
            # تحديث مستوى الخطر في الملف
            profile.risk_level = risk_level
            
            # توصيات حسب مستوى الخطر
            recommendations = self._get_risk_based_recommendations(risk_level, risk_factors)
            
            return {
                'success': True,
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'recommendations': recommendations,
                'monitoring_frequency': self._get_monitoring_frequency(risk_level),
                'specialist_referrals': self._get_specialist_referrals(risk_factors)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تقييم مخاطر الحمل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تقييم المخاطر'
            }
    
    # الدوال المساعدة
    def _calculate_pregnancy_week(self, lmp_date: date) -> int:
        """حساب أسبوع الحمل الحالي"""
        days_since_lmp = (date.today() - lmp_date).days
        return min(days_since_lmp // 7, 42)  # الحد الأقصى 42 أسبوع
    
    def _determine_trimester(self, week: int) -> str:
        """تحديد الثلث الحالي من الحمل"""
        if week <= 12:
            return PregnancyStage.FIRST_TRIMESTER.value
        elif week <= 27:
            return PregnancyStage.SECOND_TRIMESTER.value
        elif week <= 40:
            return PregnancyStage.THIRD_TRIMESTER.value
        else:
            return PregnancyStage.POSTPARTUM.value
    
    def _assess_pregnancy_risk(self, profile_data: Dict, current_week: int) -> str:
        """تقييم مستوى خطورة الحمل"""
        risk_score = 0
        
        # عوامل الخطر
        if profile_data.get('previous_complications'):
            risk_score += len(profile_data['previous_complications'])
        
        if profile_data.get('current_complications'):
            risk_score += len(profile_data['current_complications']) * 2
        
        if profile_data.get('previous_pregnancies', 0) > 4:
            risk_score += 1
        
        # تحديد مستوى الخطر
        if risk_score == 0:
            return RiskLevel.LOW.value
        elif risk_score <= 2:
            return RiskLevel.MODERATE.value
        elif risk_score <= 4:
            return RiskLevel.HIGH.value
        else:
            return RiskLevel.CRITICAL.value
    
    def _generate_appointment_schedule(self, profile: PregnancyProfile) -> List[Dict]:
        """إنشاء جدول المواعيد الموصى بها"""
        appointments = []
        
        # مواعيد الفحص الدوري
        routine_weeks = [8, 12, 16, 20, 24, 28, 32, 36, 38, 40]
        
        for week in routine_weeks:
            if week > profile.current_week:
                appointment_date = profile.last_menstrual_period + timedelta(weeks=week)
                appointments.append({
                    'week': week,
                    'type': AppointmentType.ROUTINE_CHECKUP.value,
                    'recommended_date': appointment_date.isoformat(),
                    'tests_included': self.required_tests.get(week, [])
                })
        
        return appointments
    
    def _create_follow_up_plan(self, profile: PregnancyProfile) -> Dict:
        """إنشاء خطة المتابعة"""
        return {
            'monitoring_frequency': self._get_monitoring_frequency(profile.risk_level),
            'key_milestones': self._get_pregnancy_milestones(profile.current_week),
            'important_dates': self._get_important_dates(profile),
            'emergency_signs': self.pregnancy_symptoms['warning_symptoms']
        }
    
    def _get_baby_development_info(self, week: int) -> Dict:
        """الحصول على معلومات تطور الجنين"""
        # البحث عن أقرب أسبوع متوفر
        available_weeks = sorted(self.baby_development_timeline.keys())
        closest_week = min(available_weeks, key=lambda x: abs(x - week))
        
        if closest_week in self.baby_development_timeline:
            development = self.baby_development_timeline[closest_week]
            return {
                'week': week,
                'size_description': development.size_description,
                'weight_grams': development.weight_grams,
                'length_cm': development.length_cm,
                'development_milestones': development.development_milestones,
                'organs_developing': development.organs_developing
            }
        
        return {
            'week': week,
            'message': 'معلومات التطور متوفرة للأسابيع الرئيسية'
        }
    
    def _get_weekly_tips(self, week: int, profile: PregnancyProfile) -> List[str]:
        """الحصول على النصائح الأسبوعية"""
        tips = []
        
        # نصائح عامة حسب الثلث
        trimester = self._determine_trimester(week)
        
        if trimester == PregnancyStage.FIRST_TRIMESTER.value:
            tips.extend([
                'تناولي حمض الفوليك يومياً',
                'تجنبي الكحول والتدخين',
                'احصلي على راحة كافية',
                'تناولي وجبات صغيرة متكررة'
            ])
        elif trimester == PregnancyStage.SECOND_TRIMESTER.value:
            tips.extend([
                'ابدئي بتمارين الحمل الآمنة',
                'تناولي الكالسيوم والحديد',
                'راقبي حركة الجنين',
                'احضري دروس التحضير للولادة'
            ])
        elif trimester == PregnancyStage.THIRD_TRIMESTER.value:
            tips.extend([
                'حضري حقيبة المستشفى',
                'مارسي تمارين التنفس',
                'راقبي علامات الولادة',
                'احصلي على راحة إضافية'
            ])
        
        # نصائح خاصة من تطور الجنين
        if week in self.baby_development_timeline:
            development = self.baby_development_timeline[week]
            tips.extend(development.tips_for_week)
        
        return tips
    
    def _get_expected_symptoms(self, week: int) -> List[str]:
        """الحصول على الأعراض المتوقعة"""
        trimester = self._determine_trimester(week)
        return self.pregnancy_symptoms['normal_symptoms'].get(trimester, [])
    
    def _get_required_tests(self, week: int) -> List[str]:
        """الحصول على الفحوصات المطلوبة"""
        return self.required_tests.get(week, [])
    
    def _get_next_appointment(self, user_id: str) -> Optional[Dict]:
        """الحصول على الموعد القادم"""
        if user_id not in self.pregnancy_appointments:
            return None
        
        appointments = self.pregnancy_appointments[user_id]
        upcoming_appointments = [
            apt for apt in appointments 
            if apt.scheduled_date > datetime.now() and not apt.completed
        ]
        
        if upcoming_appointments:
            next_apt = min(upcoming_appointments, key=lambda x: x.scheduled_date)
            return {
                'appointment_id': next_apt.appointment_id,
                'type': next_apt.appointment_type,
                'date': next_apt.scheduled_date.isoformat(),
                'doctor_id': next_apt.doctor_id
            }
        
        return None
    
    def _assess_symptom(self, symptom: PregnancySymptom, profile: PregnancyProfile) -> Dict:
        """تقييم العرض"""
        requires_attention = False
        recommendations = []
        
        # فحص الأعراض الخطيرة
        if symptom.symptom_name in self.pregnancy_symptoms['warning_symptoms']:
            requires_attention = True
            recommendations.append('راجعي الطبيب فوراً')
        
        # فحص شدة العرض
        elif symptom.severity >= self.service_settings['emergency_symptoms_threshold']:
            requires_attention = True
            recommendations.append('راجعي الطبيب في أقرب وقت')
        
        # نصائح عامة
        else:
            recommendations.extend([
                'راقبي العرض',
                'اشربي الكثير من الماء',
                'احصلي على راحة'
            ])
        
        return {
            'requires_attention': requires_attention,
            'recommendations': recommendations,
            'severity_assessment': self._get_severity_description(symptom.severity)
        }
    
    def _notify_doctor_about_symptom(self, user_id: str, symptom: PregnancySymptom):
        """إشعار الطبيب عن العرض"""
        # في التطبيق الحقيقي، سيتم إرسال إشعار للطبيب
        current_app.logger.info(f"إشعار طبيب عن عرض خطير للمستخدم {user_id}: {symptom.symptom_name}")
    
    def _create_appointment_reminders(self, appointment: PregnancyAppointment) -> List[Dict]:
        """إنشاء تذكيرات الموعد"""
        reminders = []
        
        for days_before in self.service_settings['appointment_reminder_days']:
            reminder_date = appointment.scheduled_date - timedelta(days=days_before)
            reminders.append({
                'reminder_date': reminder_date.isoformat(),
                'message': f'لديك موعد {appointment.appointment_type} خلال {days_before} أيام'
            })
        
        return reminders
    
    def _get_appointment_preparation(self, appointment_type: str) -> List[str]:
        """الحصول على تعليمات التحضير للموعد"""
        preparations = {
            AppointmentType.ROUTINE_CHECKUP.value: [
                'أحضري بطاقة الهوية وملف الحمل',
                'اكتبي قائمة بالأسئلة',
                'أحضري قائمة الأدوية الحالية'
            ],
            AppointmentType.ULTRASOUND.value: [
                'اشربي الكثير من الماء قبل الفحص',
                'ارتدي ملابس مريحة',
                'أحضري مرافق إذا رغبت'
            ],
            AppointmentType.BLOOD_TEST.value: [
                'صومي 8-12 ساعة إذا طُلب منك',
                'اشربي الماء',
                'أحضري طلب التحليل'
            ],
            AppointmentType.GLUCOSE_TEST.value: [
                'صومي 8 ساعات قبل الفحص',
                'تجنبي التمارين الشاقة',
                'أحضري كتاب أو مجلة للانتظار'
            ]
        }
        
        return preparations.get(appointment_type, ['أحضري بطاقة الهوية وملف الحمل'])
    
    def _create_daily_meal_plan(self, profile: PregnancyProfile) -> Dict:
        """إنشاء خطة الوجبات اليومية"""
        return {
            'breakfast': [
                'حبوب كاملة مع الحليب',
                'فاكهة طازجة',
                'عصير برتقال طبيعي'
            ],
            'morning_snack': [
                'مكسرات مشكلة',
                'زبادي طبيعي'
            ],
            'lunch': [
                'بروتين (دجاج، سمك، لحم)',
                'خضروات مطبوخة',
                'أرز أو خبز كامل',
                'سلطة خضراء'
            ],
            'afternoon_snack': [
                'فاكهة',
                'جبن قليل الدسم'
            ],
            'dinner': [
                'شوربة خضار',
                'بروتين خفيف',
                'خضروات مسلوقة'
            ],
            'evening_snack': [
                'كوب حليب دافئ',
                'بسكويت كامل'
            ]
        }
    
    def _get_hydration_guidelines(self, profile: PregnancyProfile) -> Dict:
        """الحصول على إرشادات الترطيب"""
        return {
            'daily_water_intake': '8-10 أكواب يومياً',
            'additional_fluids': ['عصائر طبيعية', 'شوربات', 'شاي الأعشاب الآمن'],
            'signs_of_dehydration': ['جفاف الفم', 'قلة التبول', 'دوخة'],
            'tips': [
                'اشربي الماء على مدار اليوم',
                'احملي زجاجة ماء معك',
                'تجنبي المشروبات المحتوية على كافيين'
            ]
        }
    
    def _calculate_weight_gain_targets(self, profile: PregnancyProfile) -> Dict:
        """حساب أهداف زيادة الوزن"""
        # في التطبيق الحقيقي، سنحصل على الوزن الأولي ومؤشر كتلة الجسم
        return {
            'total_target': '11.5-16 كيلو',
            'weekly_target': '0.4-0.5 كيلو في الأسبوع',
            'trimester_breakdown': {
                'first': '1-2 كيلو',
                'second': '5-7 كيلو',
                'third': '5-7 كيلو'
            }
        }
    
    def _get_recommended_supplements(self, profile: PregnancyProfile) -> List[Dict]:
        """الحصول على المكملات الموصى بها"""
        return [
            {
                'name': 'حمض الفوليك',
                'dosage': '400-800 ميكروجرام يومياً',
                'importance': 'منع تشوهات الأنبوب العصبي'
            },
            {
                'name': 'الحديد',
                'dosage': '27 مجم يومياً',
                'importance': 'منع فقر الدم'
            },
            {
                'name': 'الكالسيوم',
                'dosage': '1000 مجم يومياً',
                'importance': 'تطوير عظام الجنين'
            },
            {
                'name': 'فيتامين د',
                'dosage': '600 وحدة دولية يومياً',
                'importance': 'امتصاص الكالسيوم'
            }
        ]
    
    def _get_trimester_nutrition_tips(self, trimester: str) -> List[str]:
        """الحصول على نصائح التغذية حسب الثلث"""
        tips = {
            PregnancyStage.FIRST_TRIMESTER.value: [
                'تناولي وجبات صغيرة متكررة لتجنب الغثيان',
                'ركزي على حمض الفوليك',
                'تجنبي الأطعمة النيئة'
            ],
            PregnancyStage.SECOND_TRIMESTER.value: [
                'زيدي السعرات الحرارية بـ 300 سعرة',
                'ركزي على الكالسيوم والحديد',
                'تناولي الأسماك الآمنة'
            ],
            PregnancyStage.THIRD_TRIMESTER.value: [
                'تناولي وجبات أصغر وأكثر تكراراً',
                'ركزي على البروتين',
                'تجنبي الأطعمة المسببة للحرقة'
            ]
        }
        
        return tips.get(trimester, [])
    
    def _calculate_calorie_needs(self, profile: PregnancyProfile) -> Dict:
        """حساب احتياجات السعرات الحرارية"""
        base_calories = 2000  # في التطبيق الحقيقي، سيتم حسابها حسب الوزن والطول والعمر
        
        if profile.current_trimester == PregnancyStage.FIRST_TRIMESTER.value:
            additional_calories = 0
        elif profile.current_trimester == PregnancyStage.SECOND_TRIMESTER.value:
            additional_calories = 300
        else:  # الثلث الثالث
            additional_calories = 450
        
        return {
            'base_calories': base_calories,
            'additional_calories': additional_calories,
            'total_daily_calories': base_calories + additional_calories,
            'distribution': {
                'carbohydrates': '45-65%',
                'proteins': '10-35%',
                'fats': '20-35%'
            }
        }
    
    def _create_weekly_exercise_plan(self, profile: PregnancyProfile) -> Dict:
        """إنشاء خطة التمارين الأسبوعية"""
        return {
            'frequency': '3-4 مرات في الأسبوع',
            'duration': '20-30 دقيقة',
            'intensity': 'متوسطة',
            'weekly_schedule': {
                'monday': 'مشي لمدة 30 دقيقة',
                'wednesday': 'يوجا للحوامل',
                'friday': 'سباحة أو تمارين مائية',
                'sunday': 'تمارين إطالة وتنفس'
            }
        }
    
    def _get_pregnancy_specific_exercises(self, trimester: str) -> List[Dict]:
        """الحصول على التمارين الخاصة بالحمل"""
        exercises = {
            PregnancyStage.FIRST_TRIMESTER.value: [
                {
                    'name': 'تمارين التنفس العميق',
                    'description': 'تنفس عميق لمدة 5 دقائق',
                    'benefits': 'تقليل التوتر وتحسين الأكسجين'
                },
                {
                    'name': 'تمارين الإطالة الخفيفة',
                    'description': 'إطالة العضلات برفق',
                    'benefits': 'تحسين المرونة وتقليل التوتر'
                }
            ],
            PregnancyStage.SECOND_TRIMESTER.value: [
                {
                    'name': 'تمارين الحوض',
                    'description': 'تحريك الحوض بحركات دائرية',
                    'benefits': 'تقوية عضلات الحوض'
                },
                {
                    'name': 'تمارين كيجل',
                    'description': 'شد وإرخاء عضلات قاع الحوض',
                    'benefits': 'تقوية عضلات قاع الحوض'
                }
            ],
            PregnancyStage.THIRD_TRIMESTER.value: [
                {
                    'name': 'تمارين التنفس للولادة',
                    'description': 'تقنيات التنفس المختلفة',
                    'benefits': 'التحضير للولادة'
                },
                {
                    'name': 'تمارين القرفصاء المعدلة',
                    'description': 'قرفصاء خفيفة مع الدعم',
                    'benefits': 'تقوية عضلات الساقين والحوض'
                }
            ]
        }
        
        return exercises.get(trimester, [])
    
    def _get_exercise_warnings(self, profile: PregnancyProfile) -> List[str]:
        """الحصول على تحذيرات التمارين"""
        warnings = [
            'تجنبي التمارين الشاقة',
            'توقفي عند الشعور بالدوخة أو ضيق التنفس',
            'تجنبي الرياضات التي تتطلب احتكاك',
            'لا تمارسي التمارين في الطقس الحار',
            'اشربي الماء بكثرة'
        ]
        
        if profile.risk_level in [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]:
            warnings.append('استشيري الطبيب قبل ممارسة أي تمارين')
        
        return warnings
    
    def _get_exercise_benefits(self) -> List[str]:
        """الحصول على فوائد التمارين للحامل"""
        return [
            'تحسين الدورة الدموية',
            'تقليل آلام الظهر',
            'تحسين المزاج',
            'تسهيل الولادة',
            'تقوية العضلات',
            'تحسين النوم',
            'تقليل التورم',
            'التحكم في زيادة الوزن'
        ]
    
    def _get_birth_plan_checklist(self, profile: PregnancyProfile) -> List[Dict]:
        """الحصول على قائمة خطة الولادة"""
        return [
            {
                'category': 'مكان الولادة',
                'options': ['مستشفى حكومي', 'مستشفى خاص', 'مركز ولادة', 'منزل'],
                'recommendation': 'مستشفى مجهز بوحدة عناية مركزة للأطفال'
            },
            {
                'category': 'نوع الولادة',
                'options': ['ولادة طبيعية', 'قيصرية مخططة', 'حسب الحاجة'],
                'recommendation': 'ولادة طبيعية إذا لم توجد موانع'
            },
            {
                'category': 'إدارة الألم',
                'options': ['طبيعية', 'إبرة الظهر', 'مسكنات', 'تقنيات التنفس'],
                'recommendation': 'حسب تفضيلك وحالتك الطبية'
            },
            {
                'category': 'المرافق',
                'options': ['الزوج', 'الأم', 'أخت', 'صديقة', 'دولا'],
                'recommendation': 'شخص يوفر الدعم العاطفي'
            }
        ]
    
    def _get_hospital_bag_checklist(self) -> Dict:
        """الحصول على قائمة حقيبة المستشفى"""
        return {
            'for_mother': [
                'ملابس نوم مريحة',
                'ملابس داخلية قطنية',
                'حمالات صدر للرضاعة',
                'فوط صحية كبيرة',
                'أدوات النظافة الشخصية',
                'ملابس للخروج',
                'شبشب مريح',
                'هاتف وشاحن'
            ],
            'for_baby': [
                'ملابس حديثي الولادة',
                'حفاضات',
                'بطانيات',
                'قبعة وجوارب',
                'مقعد السيارة',
                'ملابس للخروج'
            ],
            'documents': [
                'بطاقة الهوية',
                'بطاقة التأمين',
                'ملف الحمل',
                'خطة الولادة',
                'أرقام الطوارئ'
            ]
        }
    
    def _get_labor_signs(self) -> List[Dict]:
        """الحصول على علامات الولادة"""
        return [
            {
                'sign': 'انقباضات منتظمة',
                'description': 'انقباضات كل 5 دقائق لمدة ساعة',
                'action': 'توجهي للمستشفى'
            },
            {
                'sign': 'نزول الماء',
                'description': 'تسرب أو تدفق السائل الأمنيوسي',
                'action': 'توجهي للمستشفى فوراً'
            },
            {
                'sign': 'نزيف',
                'description': 'نزيف أحمر فاتح',
                'action': 'اتصلي بالطوارئ فوراً'
            },
            {
                'sign': 'ضغط في الحوض',
                'description': 'شعور بضغط شديد في الحوض',
                'action': 'توجهي للمستشفى'
            }
        ]
    
    def _get_breathing_techniques(self) -> List[Dict]:
        """الحصول على تقنيات التنفس"""
        return [
            {
                'technique': 'التنفس البطيء العميق',
                'description': 'شهيق عميق من الأنف، زفير بطيء من الفم',
                'when_to_use': 'بداية المخاض'
            },
            {
                'technique': 'التنفس السريع الخفيف',
                'description': 'أنفاس قصيرة وسريعة',
                'when_to_use': 'ذروة الانقباضات'
            },
            {
                'technique': 'تنفس النفخ',
                'description': 'شهيق عميق، زفير كأنك تنفخين شمعة',
                'when_to_use': 'مرحلة الدفع'
            }
        ]
    
    def _get_pain_management_options(self) -> List[Dict]:
        """الحصول على خيارات إدارة الألم"""
        return [
            {
                'method': 'إبرة الظهر (Epidural)',
                'description': 'حقنة في العمود الفقري لتخدير النصف السفلي',
                'pros': ['تسكين فعال', 'تبقين واعية'],
                'cons': ['قد تطيل المخاض', 'آثار جانبية محتملة']
            },
            {
                'method': 'مسكنات الألم',
                'description': 'أدوية مسكنة عبر الوريد',
                'pros': ['سهولة الإعطاء', 'تسكين سريع'],
                'cons': ['قد تؤثر على الطفل', 'تسكين جزئي']
            },
            {
                'method': 'الطرق الطبيعية',
                'description': 'تقنيات التنفس، التدليك، الحمام الدافئ',
                'pros': ['آمنة', 'لا آثار جانبية'],
                'cons': ['تسكين محدود', 'تحتاج تدريب']
            }
        ]
    
    def _get_postpartum_preparation(self) -> List[str]:
        """الحصول على التحضير لما بعد الولادة"""
        return [
            'تحضير الدعم المنزلي',
            'تعلم أساسيات الرضاعة الطبيعية',
            'تحضير وجبات مجمدة',
            'ترتيب زيارات المتابعة',
            'تحضير مستلزمات الطفل',
            'التخطيط لفترة النقاهة',
            'تعلم علامات اكتئاب ما بعد الولادة'
        ]
    
    def _get_breastfeeding_preparation(self) -> List[str]:
        """الحصول على التحضير للرضاعة الطبيعية"""
        return [
            'تعلم وضعيات الرضاعة الصحيحة',
            'تحضير مكان مريح للرضاعة',
            'شراء حمالات صدر مناسبة',
            'تعلم علامات الجوع عند الطفل',
            'معرفة كيفية التعامل مع مشاكل الرضاعة',
            'تحضير مضخة الحليب إذا لزم',
            'تعلم تخزين حليب الأم'
        ]
    
    def _get_recommended_birth_classes(self, profile: PregnancyProfile) -> List[Dict]:
        """الحصول على دروس الولادة الموصى بها"""
        return [
            {
                'class': 'دروس التحضير للولادة',
                'timing': 'الأسبوع 28-32',
                'duration': '6-8 جلسات',
                'topics': ['مراحل المخاض', 'تقنيات التنفس', 'إدارة الألم']
            },
            {
                'class': 'دروس الرضاعة الطبيعية',
                'timing': 'الأسبوع 32-36',
                'duration': '2-3 جلسات',
                'topics': ['وضعيات الرضاعة', 'حل المشاكل', 'العودة للعمل']
            },
            {
                'class': 'دروس العناية بالطفل',
                'timing': 'الأسبوع 34-38',
                'duration': '2-4 جلسات',
                'topics': ['تغيير الحفاضات', 'الاستحمام', 'النوم الآمن']
            }
        ]
    
    def _get_emergency_contacts(self, profile: PregnancyProfile) -> Dict:
        """الحصول على جهات الاتصال الطارئة"""
        return {
            'primary_doctor': profile.doctor_id or 'غير محدد',
            'hospital': profile.hospital_id or 'غير محدد',
            'emergency_services': '123',
            'family_contact': profile.emergency_contact,
            'backup_hospital': 'مستشفى بديل',
            'lactation_consultant': 'استشاري الرضاعة'
        }
    
    def _get_monitoring_frequency(self, risk_level: str) -> str:
        """الحصول على تكرار المتابعة"""
        frequencies = {
            RiskLevel.LOW.value: 'كل 4 أسابيع حتى الأسبوع 28، ثم كل أسبوعين',
            RiskLevel.MODERATE.value: 'كل 3 أسابيع حتى الأسبوع 28، ثم أسبوعياً',
            RiskLevel.HIGH.value: 'كل أسبوعين حتى الأسبوع 28، ثم أسبوعياً',
            RiskLevel.CRITICAL.value: 'أسبوعياً أو حسب توجيه الطبيب'
        }
        
        return frequencies.get(risk_level, 'حسب توجيه الطبيب')
    
    def _get_pregnancy_milestones(self, current_week: int) -> List[Dict]:
        """الحصول على المعالم المهمة في الحمل"""
        milestones = [
            {'week': 12, 'milestone': 'انتهاء الثلث الأول - تقل مخاطر الإجهاض'},
            {'week': 20, 'milestone': 'فحص السونار التفصيلي - معرفة جنس الجنين'},
            {'week': 24, 'milestone': 'بداية قابلية الجنين للحياة خارج الرحم'},
            {'week': 28, 'milestone': 'بداية الثلث الثالث - نمو سريع للجنين'},
            {'week': 32, 'milestone': 'اكتمال نمو الرئتين تقريباً'},
            {'week': 36, 'milestone': 'الجنين مكتمل النمو - آمن للولادة'},
            {'week': 40, 'milestone': 'تاريخ الولادة المتوقع'}
        ]
        
        return [m for m in milestones if m['week'] > current_week]
    
    def _get_important_dates(self, profile: PregnancyProfile) -> Dict:
        """الحصول على التواريخ المهمة"""
        return {
            'conception_date': (profile.last_menstrual_period + timedelta(days=14)).isoformat(),
            'end_first_trimester': (profile.last_menstrual_period + timedelta(weeks=12)).isoformat(),
            'anatomy_scan': (profile.last_menstrual_period + timedelta(weeks=20)).isoformat(),
            'viability_date': (profile.last_menstrual_period + timedelta(weeks=24)).isoformat(),
            'third_trimester_start': (profile.last_menstrual_period + timedelta(weeks=28)).isoformat(),
            'full_term': (profile.last_menstrual_period + timedelta(weeks=37)).isoformat(),
            'due_date': profile.expected_due_date.isoformat()
        }
    
    def _get_severity_description(self, severity: int) -> str:
        """الحصول على وصف شدة العرض"""
        if severity <= 3:
            return 'خفيف'
        elif severity <= 6:
            return 'متوسط'
        elif severity <= 8:
            return 'شديد'
        else:
            return 'شديد جداً - يتطلب عناية طبية'
    
    def _get_risk_based_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """الحصول على التوصيات حسب مستوى الخطر"""
        recommendations = []
        
        if risk_level == RiskLevel.LOW.value:
            recommendations.extend([
                'متابعة دورية منتظمة',
                'نمط حياة صحي',
                'تمارين آمنة',
                'تغذية متوازنة'
            ])
        
        elif risk_level == RiskLevel.MODERATE.value:
            recommendations.extend([
                'متابعة أكثر تكراراً',
                'مراقبة الأعراض بعناية',
                'فحوصات إضافية قد تكون مطلوبة',
                'تجنب الأنشطة الشاقة'
            ])
        
        elif risk_level == RiskLevel.HIGH.value:
            recommendations.extend([
                'متابعة مع طبيب متخصص',
                'فحوصات متكررة',
                'راحة إضافية',
                'مراقبة دقيقة للأعراض'
            ])
        
        else:  # CRITICAL
            recommendations.extend([
                'متابعة فورية مع طبيب متخصص',
                'قد تحتاجين لدخول المستشفى',
                'مراقبة مستمرة',
                'تجنب أي مجهود'
            ])
        
        return recommendations
    
    def _get_specialist_referrals(self, risk_factors: List[str]) -> List[str]:
        """الحصول على التحويلات للمتخصصين"""
        referrals = []
        
        for factor in risk_factors:
            if 'سكري' in factor:
                referrals.append('طبيب غدد صماء')
            elif 'ضغط' in factor:
                referrals.append('طبيب قلب')
            elif 'كلى' in factor:
                referrals.append('طبيب كلى')
            elif 'قلب' in factor:
                referrals.append('طبيب قلب')
        
        return list(set(referrals))  # إزالة التكرارات

