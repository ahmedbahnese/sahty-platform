"""
خدمة الصحة النفسية والدعم النفسي
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class MoodLevel(Enum):
    VERY_LOW = 1
    LOW = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5

class AnxietyLevel(Enum):
    NONE = 0
    MILD = 1
    MODERATE = 2
    SEVERE = 3
    PANIC = 4

class TherapyType(Enum):
    CBT = "العلاج المعرفي السلوكي"
    MINDFULNESS = "العلاج بالوعي الذهني"
    PSYCHOTHERAPY = "العلاج النفسي"
    GROUP_THERAPY = "العلاج الجماعي"
    FAMILY_THERAPY = "العلاج الأسري"

@dataclass
class MentalHealthAssessment:
    assessment_id: str
    patient_id: str
    assessment_type: str
    questions: List[Dict]
    responses: List[Dict]
    score: float
    interpretation: str
    recommendations: List[str]
    created_at: datetime

class MentalHealthService:
    def __init__(self):
        """تهيئة خدمة الصحة النفسية"""
        
        # استبيانات التقييم النفسي
        self.assessment_questionnaires = {
            'depression_phq9': {
                'name': 'مقياس الاكتئاب PHQ-9',
                'description': 'مقياس معياري لتقييم أعراض الاكتئاب',
                'questions': [
                    {
                        'id': 1,
                        'text': 'قلة الاهتمام أو المتعة في القيام بالأشياء',
                        'type': 'scale',
                        'scale': ['لا على الإطلاق', 'عدة أيام', 'أكثر من نصف الأيام', 'كل يوم تقريباً']
                    },
                    {
                        'id': 2,
                        'text': 'الشعور بالإحباط أو الاكتئاب أو اليأس',
                        'type': 'scale',
                        'scale': ['لا على الإطلاق', 'عدة أيام', 'أكثر من نصف الأيام', 'كل يوم تقريباً']
                    },
                    {
                        'id': 3,
                        'text': 'صعوبة في النوم أو البقاء نائماً أو النوم أكثر من اللازم',
                        'type': 'scale',
                        'scale': ['لا على الإطلاق', 'عدة أيام', 'أكثر من نصف الأيام', 'كل يوم تقريباً']
                    },
                    {
                        'id': 4,
                        'text': 'الشعور بالتعب أو قلة الطاقة',
                        'type': 'scale',
                        'scale': ['لا على الإطلاق', 'عدة أيام', 'أكثر من نصف الأيام', 'كل يوم تقريباً']
                    },
                    {
                        'id': 5,
                        'text': 'ضعف الشهية أو الإفراط في الأكل',
                        'type': 'scale',
                        'scale': ['لا على الإطلاق', 'عدة أيام', 'أكثر من نصف الأيام', 'كل يوم تقريباً']
                    }
                ],
                'scoring': {
                    'min': 0,
                    'max': 20,
                    'interpretation': {
                        '0-4': 'لا توجد أعراض اكتئاب',
                        '5-9': 'أعراض اكتئاب خفيفة',
                        '10-14': 'أعراض اكتئاب متوسطة',
                        '15-19': 'أعراض اكتئاب شديدة',
                        '20': 'أعراض اكتئاب شديدة جداً'
                    }
                }
            },
            'anxiety_gad7': {
                'name': 'مقياس القلق GAD-7',
                'description': 'مقياس معياري لتقييم اضطراب القلق العام',
                'questions': [
                    {
                        'id': 1,
                        'text': 'الشعور بالعصبية أو القلق أو التوتر',
                        'type': 'scale',
                        'scale': ['لا على الإطلاق', 'عدة أيام', 'أكثر من نصف الأيام', 'كل يوم تقريباً']
                    },
                    {
                        'id': 2,
                        'text': 'عدم القدرة على التوقف عن القلق أو السيطرة عليه',
                        'type': 'scale',
                        'scale': ['لا على الإطلاق', 'عدة أيام', 'أكثر من نصف الأيام', 'كل يوم تقريباً']
                    },
                    {
                        'id': 3,
                        'text': 'القلق المفرط حول أشياء مختلفة',
                        'type': 'scale',
                        'scale': ['لا على الإطلاق', 'عدة أيام', 'أكثر من نصف الأيام', 'كل يوم تقريباً']
                    },
                    {
                        'id': 4,
                        'text': 'صعوبة في الاسترخاء',
                        'type': 'scale',
                        'scale': ['لا على الإطلاق', 'عدة أيام', 'أكثر من نصف الأيام', 'كل يوم تقريباً']
                    }
                ],
                'scoring': {
                    'min': 0,
                    'max': 21,
                    'interpretation': {
                        '0-4': 'لا يوجد قلق',
                        '5-9': 'قلق خفيف',
                        '10-14': 'قلق متوسط',
                        '15-21': 'قلق شديد'
                    }
                }
            },
            'stress_pss': {
                'name': 'مقياس الضغط النفسي PSS',
                'description': 'مقياس لتقييم مستوى الضغط النفسي المدرك',
                'questions': [
                    {
                        'id': 1,
                        'text': 'كم مرة شعرت بالانزعاج بسبب شيء حدث بشكل غير متوقع؟',
                        'type': 'scale',
                        'scale': ['أبداً', 'نادراً', 'أحياناً', 'غالباً', 'دائماً']
                    },
                    {
                        'id': 2,
                        'text': 'كم مرة شعرت أنك غير قادر على السيطرة على الأشياء المهمة في حياتك؟',
                        'type': 'scale',
                        'scale': ['أبداً', 'نادراً', 'أحياناً', 'غالباً', 'دائماً']
                    },
                    {
                        'id': 3,
                        'text': 'كم مرة شعرت بالعصبية والتوتر؟',
                        'type': 'scale',
                        'scale': ['أبداً', 'نادراً', 'أحياناً', 'غالباً', 'دائماً']
                    }
                ],
                'scoring': {
                    'min': 0,
                    'max': 40,
                    'interpretation': {
                        '0-13': 'ضغط نفسي منخفض',
                        '14-26': 'ضغط نفسي متوسط',
                        '27-40': 'ضغط نفسي مرتفع'
                    }
                }
            }
        }
        
        # تمارين الاسترخاء والتأمل
        self.relaxation_exercises = [
            {
                'id': 1,
                'name': 'تنفس عميق',
                'description': 'تمرين التنفس العميق للاسترخاء',
                'duration': 5,  # دقائق
                'instructions': [
                    'اجلس في مكان هادئ ومريح',
                    'أغلق عينيك وركز على تنفسك',
                    'تنفس ببطء من الأنف لمدة 4 ثوان',
                    'احبس النفس لمدة 4 ثوان',
                    'أخرج النفس من الفم لمدة 6 ثوان',
                    'كرر هذه العملية لمدة 5 دقائق'
                ],
                'benefits': ['تقليل التوتر', 'تحسين التركيز', 'خفض ضغط الدم']
            },
            {
                'id': 2,
                'name': 'استرخاء العضلات التدريجي',
                'description': 'تمرين لاسترخاء جميع عضلات الجسم',
                'duration': 15,
                'instructions': [
                    'استلق على ظهرك في مكان مريح',
                    'ابدأ بأصابع القدمين - شدها لمدة 5 ثوان ثم استرخ',
                    'انتقل تدريجياً إلى عضلات الساقين',
                    'استمر في الصعود حتى تصل لعضلات الوجه',
                    'اشعر بالاسترخاء الكامل لمدة دقيقتين'
                ],
                'benefits': ['تخفيف التوتر العضلي', 'تحسين النوم', 'تقليل القلق']
            },
            {
                'id': 3,
                'name': 'التأمل الذهني',
                'description': 'تمرين التأمل والوعي الذهني',
                'duration': 10,
                'instructions': [
                    'اجلس في وضعية مريحة',
                    'ركز على اللحظة الحالية',
                    'لاحظ أفكارك دون إصدار أحكام',
                    'عد إلى التركيز على التنفس عند التشتت',
                    'استمر لمدة 10 دقائق'
                ],
                'benefits': ['زيادة الوعي الذاتي', 'تحسين المزاج', 'تقليل الضغط النفسي']
            }
        ]
        
        # الأخصائيين النفسيين المتاحين
        self.mental_health_professionals = [
            {
                'id': 1,
                'name': 'د. سارة أحمد',
                'specialization': 'طب نفسي',
                'qualifications': ['دكتوراه في الطب النفسي', 'زمالة العلاج المعرفي السلوكي'],
                'experience_years': 12,
                'languages': ['العربية', 'الإنجليزية'],
                'therapy_types': [TherapyType.CBT.value, TherapyType.PSYCHOTHERAPY.value],
                'rating': 4.8,
                'consultation_fee': 300,
                'available_times': ['09:00-17:00'],
                'contact': {
                    'phone': '01234567890',
                    'email': 'dr.sara@mentalhealth.com'
                }
            },
            {
                'id': 2,
                'name': 'د. محمد علي',
                'specialization': 'علم النفس الإكلينيكي',
                'qualifications': ['ماجستير علم النفس الإكلينيكي', 'دبلوم العلاج الأسري'],
                'experience_years': 8,
                'languages': ['العربية'],
                'therapy_types': [TherapyType.FAMILY_THERAPY.value, TherapyType.GROUP_THERAPY.value],
                'rating': 4.6,
                'consultation_fee': 250,
                'available_times': ['14:00-20:00'],
                'contact': {
                    'phone': '01234567891',
                    'email': 'dr.mohamed@mentalhealth.com'
                }
            }
        ]
        
        # مصادر التثقيف النفسي
        self.educational_resources = [
            {
                'id': 1,
                'title': 'فهم الاكتئاب',
                'type': 'article',
                'content': 'دليل شامل لفهم أعراض الاكتئاب وطرق العلاج',
                'reading_time': 10,
                'tags': ['اكتئاب', 'صحة نفسية', 'علاج']
            },
            {
                'id': 2,
                'title': 'إدارة القلق والتوتر',
                'type': 'video',
                'content': 'تقنيات عملية للتعامل مع القلق اليومي',
                'duration': 15,
                'tags': ['قلق', 'توتر', 'تقنيات']
            },
            {
                'id': 3,
                'title': 'تحسين جودة النوم',
                'type': 'guide',
                'content': 'نصائح علمية لتحسين نوعية النوم',
                'reading_time': 8,
                'tags': ['نوم', 'صحة', 'نصائح']
            }
        ]
    
    def conduct_mental_health_assessment(self, patient_id: str, assessment_type: str, 
                                       responses: List[Dict]) -> Dict:
        """
        إجراء تقييم الصحة النفسية
        
        Args:
            patient_id: معرف المريض
            assessment_type: نوع التقييم
            responses: إجابات المريض
            
        Returns:
            Dict: نتائج التقييم
        """
        try:
            if assessment_type not in self.assessment_questionnaires:
                raise Exception('نوع تقييم غير مدعوم')
            
            questionnaire = self.assessment_questionnaires[assessment_type]
            assessment_id = str(uuid.uuid4())
            
            # حساب النتيجة
            total_score = sum(response.get('score', 0) for response in responses)
            
            # تفسير النتيجة
            interpretation = self._interpret_assessment_score(
                assessment_type, total_score, questionnaire['scoring']
            )
            
            # إنتاج التوصيات
            recommendations = self._generate_mental_health_recommendations(
                assessment_type, total_score, interpretation
            )
            
            # إنشاء سجل التقييم
            assessment = MentalHealthAssessment(
                assessment_id=assessment_id,
                patient_id=patient_id,
                assessment_type=assessment_type,
                questions=questionnaire['questions'],
                responses=responses,
                score=total_score,
                interpretation=interpretation,
                recommendations=recommendations,
                created_at=datetime.now()
            )
            
            # تحديد مستوى الخطورة
            risk_level = self._assess_risk_level(assessment_type, total_score)
            
            # إرسال تنبيه إذا كان هناك خطر
            if risk_level in ['high', 'critical']:
                self._send_mental_health_alert(patient_id, assessment, risk_level)
            
            return {
                'success': True,
                'assessment': assessment.__dict__,
                'risk_level': risk_level,
                'next_steps': self._get_next_steps(risk_level, assessment_type)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في التقييم النفسي: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _interpret_assessment_score(self, assessment_type: str, score: float, scoring_info: Dict) -> str:
        """تفسير نتيجة التقييم"""
        interpretation_ranges = scoring_info['interpretation']
        
        for score_range, interpretation in interpretation_ranges.items():
            if '-' in score_range:
                min_score, max_score = map(int, score_range.split('-'))
                if min_score <= score <= max_score:
                    return interpretation
            else:
                if score == int(score_range):
                    return interpretation
        
        return 'نتيجة غير محددة'
    
    def _generate_mental_health_recommendations(self, assessment_type: str, 
                                              score: float, interpretation: str) -> List[str]:
        """إنتاج توصيات الصحة النفسية"""
        recommendations = []
        
        if assessment_type == 'depression_phq9':
            if score <= 4:
                recommendations = [
                    'الحفاظ على نمط حياة صحي',
                    'ممارسة الرياضة بانتظام',
                    'الحفاظ على علاقات اجتماعية إيجابية'
                ]
            elif score <= 9:
                recommendations = [
                    'ممارسة تمارين الاسترخاء يومياً',
                    'تحسين جودة النوم',
                    'التحدث مع الأصدقاء والعائلة',
                    'النظر في استشارة نفسية'
                ]
            elif score <= 14:
                recommendations = [
                    'استشارة أخصائي نفسي في أقرب وقت',
                    'ممارسة العلاج المعرفي السلوكي',
                    'تجنب العزلة الاجتماعية',
                    'مراقبة الأعراض يومياً'
                ]
            else:
                recommendations = [
                    'طلب المساعدة الطبية فوراً',
                    'استشارة طبيب نفسي',
                    'النظر في العلاج الدوائي',
                    'الحصول على دعم عائلي قوي',
                    'تجنب اتخاذ قرارات مهمة'
                ]
        
        elif assessment_type == 'anxiety_gad7':
            if score <= 4:
                recommendations = [
                    'الحفاظ على روتين يومي منتظم',
                    'ممارسة تقنيات التنفس العميق',
                    'تجنب الكافيين الزائد'
                ]
            elif score <= 9:
                recommendations = [
                    'تعلم تقنيات إدارة القلق',
                    'ممارسة التأمل والاسترخاء',
                    'تحديد مصادر القلق والتعامل معها',
                    'النظر في استشارة نفسية'
                ]
            else:
                recommendations = [
                    'استشارة أخصائي نفسي فوراً',
                    'تعلم تقنيات العلاج المعرفي السلوكي',
                    'تجنب المواقف المثيرة للقلق مؤقتاً',
                    'النظر في العلاج الدوائي'
                ]
        
        return recommendations
    
    def _assess_risk_level(self, assessment_type: str, score: float) -> str:
        """تقييم مستوى الخطورة"""
        if assessment_type == 'depression_phq9':
            if score <= 4:
                return 'low'
            elif score <= 9:
                return 'mild'
            elif score <= 14:
                return 'moderate'
            elif score <= 19:
                return 'high'
            else:
                return 'critical'
        
        elif assessment_type == 'anxiety_gad7':
            if score <= 4:
                return 'low'
            elif score <= 9:
                return 'mild'
            elif score <= 14:
                return 'moderate'
            else:
                return 'high'
        
        return 'unknown'
    
    def _send_mental_health_alert(self, patient_id: str, assessment: MentalHealthAssessment, 
                                risk_level: str):
        """إرسال تنبيه للحالات عالية الخطورة"""
        try:
            alert_data = {
                'patient_id': patient_id,
                'assessment_type': assessment.assessment_type,
                'score': assessment.score,
                'risk_level': risk_level,
                'interpretation': assessment.interpretation,
                'timestamp': assessment.created_at.isoformat()
            }
            
            # في التطبيق الحقيقي، سيتم إرسال تنبيه للفريق الطبي
            current_app.logger.warning(f"تنبيه صحة نفسية: مريض {patient_id} - مستوى خطر {risk_level}")
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال تنبيه الصحة النفسية: {str(e)}")
    
    def _get_next_steps(self, risk_level: str, assessment_type: str) -> List[str]:
        """الحصول على الخطوات التالية"""
        if risk_level == 'critical':
            return [
                'اتصل بخط المساعدة النفسية فوراً: 16328',
                'توجه لأقرب مستشفى للطوارئ النفسية',
                'لا تبق وحيداً - اطلب مرافقة شخص مقرب'
            ]
        elif risk_level == 'high':
            return [
                'احجز موعد مع أخصائي نفسي خلال 48 ساعة',
                'أخبر شخص مقرب عن حالتك',
                'تجنب اتخاذ قرارات مهمة'
            ]
        elif risk_level == 'moderate':
            return [
                'احجز موعد مع أخصائي نفسي خلال أسبوع',
                'ابدأ في ممارسة تمارين الاسترخاء',
                'حافظ على روتين يومي صحي'
            ]
        else:
            return [
                'استمر في مراقبة حالتك النفسية',
                'مارس الأنشطة التي تحبها',
                'حافظ على التواصل الاجتماعي'
            ]
    
    def track_mood(self, patient_id: str, mood_level: int, notes: str = None, 
                  triggers: List[str] = None) -> Dict:
        """
        تتبع المزاج اليومي
        
        Args:
            patient_id: معرف المريض
            mood_level: مستوى المزاج (1-5)
            notes: ملاحظات
            triggers: المحفزات
            
        Returns:
            Dict: سجل المزاج
        """
        try:
            mood_entry = {
                'entry_id': str(uuid.uuid4()),
                'patient_id': patient_id,
                'date': datetime.now().date().isoformat(),
                'time': datetime.now().time().isoformat(),
                'mood_level': mood_level,
                'mood_description': MoodLevel(mood_level).name,
                'notes': notes,
                'triggers': triggers or [],
                'activities': [],  # يمكن إضافتها لاحقاً
                'sleep_hours': None,  # يمكن ربطها بتتبع النوم
                'created_at': datetime.now().isoformat()
            }
            
            # تحليل الاتجاه
            mood_trend = self._analyze_mood_trend(patient_id)
            
            # توصيات بناءً على المزاج
            recommendations = self._get_mood_recommendations(mood_level, triggers)
            
            return {
                'success': True,
                'mood_entry': mood_entry,
                'mood_trend': mood_trend,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_mood_trend(self, patient_id: str) -> Dict:
        """تحليل اتجاه المزاج"""
        # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
        # هنا محاكاة للتحليل
        
        return {
            'trend': 'improving',  # improving, declining, stable
            'average_mood_week': 3.2,
            'average_mood_month': 3.0,
            'best_day': 'الأحد',
            'worst_day': 'الاثنين',
            'common_triggers': ['ضغط العمل', 'قلة النوم'],
            'mood_pattern': 'أفضل في المساء'
        }
    
    def _get_mood_recommendations(self, mood_level: int, triggers: List[str]) -> List[str]:
        """الحصول على توصيات بناءً على المزاج"""
        recommendations = []
        
        if mood_level <= 2:  # مزاج منخفض
            recommendations = [
                'مارس تمرين التنفس العميق لمدة 5 دقائق',
                'اتصل بصديق أو فرد من العائلة',
                'اخرج للمشي في الهواء الطلق',
                'استمع لموسيقى هادئة',
                'اكتب في مذكرة المشاعر'
            ]
        elif mood_level == 3:  # مزاج محايد
            recommendations = [
                'مارس نشاط تحبه',
                'اقرأ كتاب أو مقال مفيد',
                'تواصل مع الأصدقاء',
                'مارس الرياضة الخفيفة'
            ]
        else:  # مزاج جيد
            recommendations = [
                'استغل هذا المزاج الإيجابي في إنجاز المهام',
                'شارك الإيجابية مع الآخرين',
                'مارس هواية جديدة',
                'خطط لأنشطة ممتعة'
            ]
        
        # توصيات خاصة بالمحفزات
        if triggers:
            if 'ضغط العمل' in triggers:
                recommendations.append('خذ استراحة قصيرة من العمل')
            if 'قلة النوم' in triggers:
                recommendations.append('احرص على النوم مبكراً الليلة')
            if 'مشاكل عائلية' in triggers:
                recommendations.append('تحدث مع شخص تثق به')
        
        return recommendations
    
    def get_relaxation_exercise(self, exercise_type: str = None, duration: int = None) -> Dict:
        """
        الحصول على تمرين استرخاء
        
        Args:
            exercise_type: نوع التمرين
            duration: المدة المطلوبة
            
        Returns:
            Dict: تمرين الاسترخاء
        """
        try:
            available_exercises = self.relaxation_exercises.copy()
            
            # فلترة حسب النوع
            if exercise_type:
                available_exercises = [ex for ex in available_exercises 
                                     if exercise_type.lower() in ex['name'].lower()]
            
            # فلترة حسب المدة
            if duration:
                available_exercises = [ex for ex in available_exercises 
                                     if ex['duration'] <= duration]
            
            if not available_exercises:
                return {
                    'success': False,
                    'error': 'لا توجد تمارين متاحة بالمعايير المحددة'
                }
            
            # اختيار تمرين عشوائي
            import random
            selected_exercise = random.choice(available_exercises)
            
            # إضافة معلومات إضافية
            selected_exercise['session_id'] = str(uuid.uuid4())
            selected_exercise['started_at'] = datetime.now().isoformat()
            
            return {
                'success': True,
                'exercise': selected_exercise,
                'all_exercises': len(self.relaxation_exercises)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def book_therapy_session(self, patient_id: str, therapist_id: int, 
                           preferred_date: str, preferred_time: str,
                           session_type: str = 'individual') -> Dict:
        """
        حجز جلسة علاج نفسي
        
        Args:
            patient_id: معرف المريض
            therapist_id: معرف المعالج
            preferred_date: التاريخ المفضل
            preferred_time: الوقت المفضل
            session_type: نوع الجلسة
            
        Returns:
            Dict: تفاصيل الحجز
        """
        try:
            # البحث عن المعالج
            therapist = next((t for t in self.mental_health_professionals 
                            if t['id'] == therapist_id), None)
            
            if not therapist:
                return {
                    'success': False,
                    'error': 'معالج غير موجود'
                }
            
            # التحقق من التوفر
            availability = self._check_therapist_availability(
                therapist_id, preferred_date, preferred_time
            )
            
            if not availability['available']:
                return {
                    'success': False,
                    'error': 'الموعد غير متاح',
                    'alternative_slots': availability['alternative_slots']
                }
            
            # إنشاء الحجز
            session_id = str(uuid.uuid4())
            session = {
                'session_id': session_id,
                'patient_id': patient_id,
                'therapist_id': therapist_id,
                'therapist_name': therapist['name'],
                'date': preferred_date,
                'time': preferred_time,
                'duration': 50,  # دقيقة
                'session_type': session_type,
                'therapy_type': therapist['therapy_types'][0],  # النوع الأول
                'fee': therapist['consultation_fee'],
                'status': 'confirmed',
                'location': 'online',  # افتراضي
                'created_at': datetime.now().isoformat(),
                'preparation_notes': [
                    'كن في مكان هادئ وخاص',
                    'تأكد من اتصال إنترنت مستقر',
                    'أحضر ورقة وقلم للملاحظات',
                    'فكر في النقاط التي تريد مناقشتها'
                ]
            }
            
            return {
                'success': True,
                'session': session,
                'payment_required': True,
                'cancellation_policy': 'يمكن الإلغاء حتى 24 ساعة قبل الموعد'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_therapist_availability(self, therapist_id: int, date: str, time: str) -> Dict:
        """فحص توفر المعالج"""
        # في التطبيق الحقيقي، سيتم فحص قاعدة البيانات
        # هنا محاكاة للتوفر
        
        alternative_slots = [
            {'date': date, 'time': '10:00'},
            {'date': date, 'time': '14:00'},
            {'date': (datetime.fromisoformat(date) + timedelta(days=1)).date().isoformat(), 'time': time}
        ]
        
        return {
            'available': True,  # افتراض التوفر
            'alternative_slots': alternative_slots
        }
    
    def get_mental_health_resources(self, category: str = None, 
                                  resource_type: str = None) -> Dict:
        """
        الحصول على مصادر التثقيف النفسي
        
        Args:
            category: فئة المصدر
            resource_type: نوع المصدر
            
        Returns:
            Dict: المصادر المتاحة
        """
        try:
            resources = self.educational_resources.copy()
            
            # فلترة حسب النوع
            if resource_type:
                resources = [r for r in resources if r['type'] == resource_type]
            
            # فلترة حسب الفئة (البحث في العلامات)
            if category:
                resources = [r for r in resources 
                           if category.lower() in [tag.lower() for tag in r['tags']]]
            
            # إضافة معلومات إضافية
            for resource in resources:
                resource['views'] = 1250  # محاكاة
                resource['rating'] = 4.5  # محاكاة
                resource['last_updated'] = '2024-01-15'
            
            return {
                'success': True,
                'resources': resources,
                'total_count': len(resources),
                'categories': ['اكتئاب', 'قلق', 'توتر', 'نوم', 'علاقات'],
                'types': ['article', 'video', 'guide', 'podcast']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_mental_health_plan(self, patient_id: str, assessment_results: Dict,
                                goals: List[str]) -> Dict:
        """
        إنشاء خطة الصحة النفسية
        
        Args:
            patient_id: معرف المريض
            assessment_results: نتائج التقييم
            goals: الأهداف العلاجية
            
        Returns:
            Dict: خطة الصحة النفسية
        """
        try:
            plan_id = str(uuid.uuid4())
            
            # تحديد التدخلات المناسبة
            interventions = self._select_interventions(assessment_results)
            
            # إنشاء جدول المتابعة
            follow_up_schedule = self._create_follow_up_schedule(assessment_results)
            
            # خطة الصحة النفسية
            mental_health_plan = {
                'plan_id': plan_id,
                'patient_id': patient_id,
                'assessment_results': assessment_results,
                'goals': goals,
                'interventions': interventions,
                'follow_up_schedule': follow_up_schedule,
                'duration_weeks': 12,  # مدة الخطة
                'created_at': datetime.now().isoformat(),
                'created_by': 'system',
                'status': 'active',
                'progress_tracking': {
                    'mood_tracking': True,
                    'symptom_monitoring': True,
                    'goal_assessment': True,
                    'weekly_check_ins': True
                },
                'emergency_contacts': [
                    {'name': 'خط المساعدة النفسية', 'phone': '16328'},
                    {'name': 'الطوارئ النفسية', 'phone': '123'}
                ]
            }
            
            return {
                'success': True,
                'mental_health_plan': mental_health_plan
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _select_interventions(self, assessment_results: Dict) -> List[Dict]:
        """اختيار التدخلات المناسبة"""
        interventions = []
        
        risk_level = assessment_results.get('risk_level', 'low')
        
        # تدخلات أساسية
        interventions.append({
            'type': 'self_monitoring',
            'name': 'تتبع المزاج اليومي',
            'frequency': 'daily',
            'duration_weeks': 12
        })
        
        interventions.append({
            'type': 'relaxation',
            'name': 'تمارين الاسترخاء',
            'frequency': 'daily',
            'duration_minutes': 10
        })
        
        # تدخلات حسب مستوى الخطر
        if risk_level in ['moderate', 'high', 'critical']:
            interventions.append({
                'type': 'therapy',
                'name': 'جلسات العلاج النفسي',
                'frequency': 'weekly',
                'duration_weeks': 8
            })
        
        if risk_level in ['high', 'critical']:
            interventions.append({
                'type': 'medication_evaluation',
                'name': 'تقييم الحاجة للعلاج الدوائي',
                'frequency': 'as_needed',
                'priority': 'high'
            })
        
        return interventions
    
    def _create_follow_up_schedule(self, assessment_results: Dict) -> List[Dict]:
        """إنشاء جدول المتابعة"""
        schedule = []
        risk_level = assessment_results.get('risk_level', 'low')
        
        # متابعة أسبوعية للحالات عالية الخطورة
        if risk_level in ['high', 'critical']:
            for week in range(1, 5):  # أول 4 أسابيع
                schedule.append({
                    'week': week,
                    'type': 'assessment',
                    'description': 'تقييم أسبوعي للأعراض',
                    'due_date': (datetime.now() + timedelta(weeks=week)).date().isoformat()
                })
        
        # متابعة شهرية للحالات المتوسطة
        elif risk_level == 'moderate':
            for month in range(1, 4):  # 3 أشهر
                schedule.append({
                    'month': month,
                    'type': 'assessment',
                    'description': 'تقييم شهري للتقدم',
                    'due_date': (datetime.now() + timedelta(weeks=month*4)).date().isoformat()
                })
        
        # تقييم نهائي لجميع الحالات
        schedule.append({
            'type': 'final_assessment',
            'description': 'تقييم نهائي لفعالية الخطة',
            'due_date': (datetime.now() + timedelta(weeks=12)).date().isoformat()
        })
        
        return schedule

