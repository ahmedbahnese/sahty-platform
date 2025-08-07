"""
خدمة دعم مرضى السكري المتقدمة
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class DiabetesType(Enum):
    TYPE_1 = "النوع الأول"
    TYPE_2 = "النوع الثاني"
    GESTATIONAL = "سكري الحمل"
    PREDIABETES = "ما قبل السكري"

class GlucoseLevel(Enum):
    VERY_LOW = "منخفض جداً"
    LOW = "منخفض"
    NORMAL = "طبيعي"
    HIGH = "مرتفع"
    VERY_HIGH = "مرتفع جداً"

class MedicationType(Enum):
    INSULIN = "إنسولين"
    METFORMIN = "ميتفورمين"
    SULFONYLUREA = "سلفونيل يوريا"
    DPP4_INHIBITOR = "مثبط DPP-4"
    GLP1_AGONIST = "ناهض GLP-1"

@dataclass
class GlucoseReading:
    reading_id: str
    patient_id: str
    glucose_value: float
    reading_time: datetime
    meal_relation: str  # قبل الأكل، بعد الأكل، صائم
    notes: str
    symptoms: List[str]
    medication_taken: bool

class DiabetesService:
    def __init__(self):
        """تهيئة خدمة دعم مرضى السكري"""
        
        # المعايير الطبية لمستويات السكر
        self.glucose_ranges = {
            'fasting': {  # صائم
                'normal': (70, 100),
                'prediabetes': (100, 125),
                'diabetes': (126, float('inf'))
            },
            'postprandial': {  # بعد الأكل بساعتين
                'normal': (70, 140),
                'prediabetes': (140, 199),
                'diabetes': (200, float('inf'))
            },
            'random': {  # عشوائي
                'normal': (70, 140),
                'elevated': (140, 199),
                'diabetes': (200, float('inf'))
            },
            'hba1c': {  # الهيموجلوبين السكري
                'normal': (0, 5.7),
                'prediabetes': (5.7, 6.4),
                'diabetes': (6.5, float('inf'))
            }
        }
        
        # أعراض ارتفاع وانخفاض السكر
        self.symptoms_database = {
            'hyperglycemia': {  # ارتفاع السكر
                'mild': ['عطش شديد', 'كثرة التبول', 'تعب', 'رؤية ضبابية'],
                'moderate': ['غثيان', 'قيء', 'ألم في البطن', 'رائحة الأسيتون في النفس'],
                'severe': ['صعوبة في التنفس', 'فقدان الوعي', 'جفاف شديد']
            },
            'hypoglycemia': {  # انخفاض السكر
                'mild': ['جوع شديد', 'رعشة', 'تعرق', 'دوخة'],
                'moderate': ['تشويش', 'صداع', 'تغيرات مزاجية', 'ضعف'],
                'severe': ['تشنجات', 'فقدان الوعي', 'غيبوبة']
            }
        }
        
        # قاعدة بيانات أدوية السكري
        self.diabetes_medications = {
            'insulin_rapid': {
                'name': 'إنسولين سريع المفعول',
                'type': MedicationType.INSULIN.value,
                'onset': '15-30 دقيقة',
                'peak': '1-3 ساعات',
                'duration': '3-5 ساعات',
                'administration': 'حقن تحت الجلد',
                'timing': 'قبل الوجبات بـ 15 دقيقة',
                'side_effects': ['انخفاض السكر', 'تورم مكان الحقن'],
                'storage': 'في الثلاجة (2-8°C)',
                'brands': ['نوفورابيد', 'هيومالوج', 'أبيدرا']
            },
            'insulin_long': {
                'name': 'إنسولين طويل المفعول',
                'type': MedicationType.INSULIN.value,
                'onset': '1-2 ساعة',
                'peak': 'بدون ذروة واضحة',
                'duration': '20-24 ساعة',
                'administration': 'حقن تحت الجلد',
                'timing': 'مرة واحدة يومياً في نفس الوقت',
                'side_effects': ['انخفاض السكر', 'زيادة الوزن'],
                'storage': 'في الثلاجة (2-8°C)',
                'brands': ['لانتوس', 'ليفيمير', 'تريسيبا']
            },
            'metformin': {
                'name': 'ميتفورمين',
                'type': MedicationType.METFORMIN.value,
                'mechanism': 'تقليل إنتاج الجلوكوز من الكبد',
                'administration': 'أقراص فموية',
                'timing': 'مع الوجبات',
                'side_effects': ['اضطراب معدي', 'إسهال', 'طعم معدني'],
                'contraindications': ['أمراض الكلى الشديدة', 'أمراض الكبد'],
                'brands': ['جلوكوفاج', 'سيدوفاج', 'ديافورمين']
            },
            'glibenclamide': {
                'name': 'جليبنكلاميد',
                'type': MedicationType.SULFONYLUREA.value,
                'mechanism': 'تحفيز إفراز الإنسولين',
                'administration': 'أقراص فموية',
                'timing': 'قبل الوجبات بـ 30 دقيقة',
                'side_effects': ['انخفاض السكر', 'زيادة الوزن'],
                'contraindications': ['الحمل', 'الرضاعة', 'أمراض الكبد الشديدة'],
                'brands': ['داونيل', 'يوجليكون', 'جليبيزيد']
            }
        }
        
        # خطط العلاج المعيارية
        self.treatment_plans = {
            DiabetesType.TYPE_1.value: {
                'primary_treatment': 'إنسولين',
                'monitoring_frequency': 'يومي متعدد',
                'target_hba1c': 7.0,
                'lifestyle_modifications': [
                    'حساب الكربوهيدرات',
                    'ممارسة الرياضة المنتظمة',
                    'مراقبة السكر المستمرة'
                ]
            },
            DiabetesType.TYPE_2.value: {
                'primary_treatment': 'تعديل نمط الحياة + أدوية',
                'monitoring_frequency': 'يومي أو حسب الحاجة',
                'target_hba1c': 7.0,
                'lifestyle_modifications': [
                    'إنقاص الوزن',
                    'نظام غذائي صحي',
                    'ممارسة الرياضة',
                    'الإقلاع عن التدخين'
                ]
            },
            DiabetesType.GESTATIONAL.value: {
                'primary_treatment': 'نظام غذائي + مراقبة',
                'monitoring_frequency': 'يومي',
                'target_glucose': {
                    'fasting': 95,
                    'postprandial_1h': 140,
                    'postprandial_2h': 120
                },
                'lifestyle_modifications': [
                    'نظام غذائي للحوامل',
                    'ممارسة رياضة خفيفة',
                    'مراقبة وزن الحمل'
                ]
            }
        }
        
        # نصائح غذائية لمرضى السكري
        self.dietary_guidelines = {
            'carbohydrate_counting': {
                'title': 'حساب الكربوهيدرات',
                'description': 'تعلم كيفية حساب الكربوهيدرات في الطعام',
                'guidelines': [
                    '15 جرام كربوهيدرات = حصة واحدة',
                    'اقرأ ملصقات الطعام بعناية',
                    'استخدم كوب القياس والميزان',
                    'تعلم أحجام الحصص المعيارية'
                ],
                'examples': {
                    'خبز': '1 شريحة = 15 جرام',
                    'أرز مطبوخ': '1/3 كوب = 15 جرام',
                    'فاكهة متوسطة': '1 حبة = 15 جرام',
                    'لبن': '1 كوب = 12 جرام'
                }
            },
            'glycemic_index': {
                'title': 'مؤشر نسبة السكر في الدم',
                'description': 'اختيار الأطعمة ذات المؤشر المنخفض',
                'low_gi_foods': [
                    'الشوفان', 'البقوليات', 'الخضروات الورقية',
                    'التفاح', 'الكمثرى', 'الأرز البني'
                ],
                'high_gi_foods': [
                    'الخبز الأبيض', 'الأرز الأبيض', 'البطاطس المقلية',
                    'المشروبات السكرية', 'الحلويات'
                ]
            },
            'meal_planning': {
                'title': 'تخطيط الوجبات',
                'principles': [
                    'تناول وجبات منتظمة',
                    'لا تتخطى الوجبات',
                    'وزع الكربوهيدرات على اليوم',
                    'أكثر من الخضروات غير النشوية'
                ],
                'plate_method': {
                    'vegetables': '1/2 الطبق',
                    'protein': '1/4 الطبق',
                    'carbohydrates': '1/4 الطبق'
                }
            }
        }
        
        # تمارين مناسبة لمرضى السكري
        self.exercise_recommendations = {
            'aerobic': {
                'type': 'تمارين هوائية',
                'frequency': '150 دقيقة أسبوعياً',
                'examples': ['المشي السريع', 'السباحة', 'ركوب الدراجة'],
                'benefits': ['تحسين حساسية الإنسولين', 'خفض السكر', 'تقوية القلب']
            },
            'resistance': {
                'type': 'تمارين المقاومة',
                'frequency': 'مرتين أسبوعياً',
                'examples': ['رفع الأثقال', 'تمارين المقاومة', 'اليوجا'],
                'benefits': ['بناء العضلات', 'تحسين الأيض', 'تقوية العظام']
            },
            'flexibility': {
                'type': 'تمارين المرونة',
                'frequency': 'يومياً',
                'examples': ['التمدد', 'اليوجا', 'التاي تشي'],
                'benefits': ['تحسين المرونة', 'تقليل التوتر', 'تحسين التوازن']
            }
        }
    
    def create_diabetes_profile(self, patient_id: str, diabetes_data: Dict) -> Dict:
        """
        إنشاء ملف مريض السكري
        
        Args:
            patient_id: معرف المريض
            diabetes_data: بيانات السكري
            
        Returns:
            Dict: ملف مريض السكري
        """
        try:
            profile_id = str(uuid.uuid4())
            
            # تحديد نوع السكري
            diabetes_type = diabetes_data.get('type', DiabetesType.TYPE_2.value)
            
            # تحديد خطة العلاج
            treatment_plan = self.treatment_plans.get(diabetes_type, 
                                                    self.treatment_plans[DiabetesType.TYPE_2.value])
            
            # إنشاء الملف الشخصي
            diabetes_profile = {
                'profile_id': profile_id,
                'patient_id': patient_id,
                'diabetes_type': diabetes_type,
                'diagnosis_date': diabetes_data.get('diagnosis_date'),
                'current_medications': diabetes_data.get('medications', []),
                'allergies': diabetes_data.get('allergies', []),
                'complications': diabetes_data.get('complications', []),
                'family_history': diabetes_data.get('family_history', False),
                'treatment_plan': treatment_plan,
                'monitoring_schedule': self._create_monitoring_schedule(diabetes_type),
                'target_values': self._set_target_values(diabetes_type, diabetes_data),
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            # إنشاء خطة المتابعة الأولية
            follow_up_plan = self._create_follow_up_plan(diabetes_profile)
            
            # إنشاء خطة التثقيف
            education_plan = self._create_education_plan(diabetes_type)
            
            return {
                'success': True,
                'diabetes_profile': diabetes_profile,
                'follow_up_plan': follow_up_plan,
                'education_plan': education_plan,
                'initial_recommendations': self._get_initial_recommendations(diabetes_profile)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء ملف مريض السكري: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_monitoring_schedule(self, diabetes_type: str) -> Dict:
        """إنشاء جدول المراقبة"""
        if diabetes_type == DiabetesType.TYPE_1.value:
            return {
                'glucose_monitoring': {
                    'frequency': '4-6 مرات يومياً',
                    'times': ['قبل الإفطار', 'قبل الغداء', 'قبل العشاء', 'قبل النوم'],
                    'additional': ['عند الشعور بأعراض', 'قبل وبعد الرياضة']
                },
                'hba1c_testing': 'كل 3 أشهر',
                'ketone_testing': 'عند ارتفاع السكر فوق 250',
                'blood_pressure': 'شهرياً',
                'weight': 'أسبوعياً'
            }
        elif diabetes_type == DiabetesType.TYPE_2.value:
            return {
                'glucose_monitoring': {
                    'frequency': '1-2 مرة يومياً',
                    'times': ['قبل الإفطار', 'بعد الوجبات أحياناً'],
                    'additional': ['عند تغيير الدواء', 'عند المرض']
                },
                'hba1c_testing': 'كل 3-6 أشهر',
                'blood_pressure': 'شهرياً',
                'weight': 'أسبوعياً',
                'cholesterol': 'سنوياً'
            }
        else:  # سكري الحمل
            return {
                'glucose_monitoring': {
                    'frequency': '4 مرات يومياً',
                    'times': ['صائم', 'بعد الإفطار بساعة', 'بعد الغداء بساعة', 'بعد العشاء بساعة']
                },
                'weight_monitoring': 'أسبوعياً',
                'blood_pressure': 'أسبوعياً',
                'urine_ketones': 'عند الحاجة'
            }
    
    def _set_target_values(self, diabetes_type: str, patient_data: Dict) -> Dict:
        """تحديد القيم المستهدفة"""
        age = patient_data.get('age', 50)
        complications = patient_data.get('complications', [])
        
        # تعديل الأهداف حسب العمر والمضاعفات
        if age > 65 or complications:
            hba1c_target = 7.5
        else:
            hba1c_target = 7.0
        
        targets = {
            'hba1c': hba1c_target,
            'fasting_glucose': (80, 130),
            'postprandial_glucose': (80, 180),
            'blood_pressure': (130, 80),
            'ldl_cholesterol': 100,
            'hdl_cholesterol': {
                'male': 40,
                'female': 50
            },
            'triglycerides': 150
        }
        
        # تعديل خاص لسكري الحمل
        if diabetes_type == DiabetesType.GESTATIONAL.value:
            targets.update({
                'fasting_glucose': (60, 95),
                'postprandial_1h': (60, 140),
                'postprandial_2h': (60, 120)
            })
        
        return targets
    
    def _create_follow_up_plan(self, profile: Dict) -> Dict:
        """إنشاء خطة المتابعة"""
        diabetes_type = profile['diabetes_type']
        
        if diabetes_type == DiabetesType.TYPE_1.value:
            return {
                'endocrinologist': 'كل 3 أشهر',
                'ophthalmologist': 'سنوياً',
                'podiatrist': 'سنوياً',
                'dentist': 'كل 6 أشهر',
                'dietitian': 'حسب الحاجة',
                'diabetes_educator': 'عند التشخيص ثم حسب الحاجة'
            }
        else:
            return {
                'primary_care': 'كل 3-6 أشهر',
                'endocrinologist': 'حسب الحاجة',
                'ophthalmologist': 'سنوياً',
                'podiatrist': 'سنوياً',
                'dentist': 'كل 6 أشهر',
                'dietitian': 'عند التشخيص ثم حسب الحاجة'
            }
    
    def _create_education_plan(self, diabetes_type: str) -> Dict:
        """إنشاء خطة التثقيف"""
        basic_topics = [
            'ما هو مرض السكري؟',
            'أعراض ارتفاع وانخفاض السكر',
            'كيفية قياس السكر',
            'النظام الغذائي الصحي',
            'أهمية ممارسة الرياضة',
            'العناية بالقدمين',
            'إدارة المرض أثناء المرض'
        ]
        
        if diabetes_type == DiabetesType.TYPE_1.value:
            basic_topics.extend([
                'أنواع الإنسولين وطرق الحقن',
                'حساب الكربوهيدرات',
                'تعديل جرعة الإنسولين',
                'التعامل مع الحماض الكيتوني'
            ])
        
        return {
            'topics': basic_topics,
            'delivery_methods': [
                'جلسات فردية',
                'مجموعات دعم',
                'مواد تعليمية مكتوبة',
                'فيديوهات تعليمية',
                'تطبيقات الهاتف'
            ],
            'assessment_schedule': 'كل 6 أشهر'
        }
    
    def _get_initial_recommendations(self, profile: Dict) -> List[str]:
        """الحصول على التوصيات الأولية"""
        recommendations = [
            'ابدأ بمراقبة السكر حسب الجدول المحدد',
            'اتبع النظام الغذائي الموصى به',
            'مارس الرياضة بانتظام',
            'تناول الأدوية في مواعيدها',
            'احتفظ بسجل يومي للسكر'
        ]
        
        if profile['diabetes_type'] == DiabetesType.TYPE_1.value:
            recommendations.extend([
                'تعلم كيفية حقن الإنسولين بشكل صحيح',
                'احمل معك دائماً مصدر سكر سريع',
                'تعلم حساب الكربوهيدرات'
            ])
        
        return recommendations
    
    def record_glucose_reading(self, patient_id: str, reading_data: Dict) -> Dict:
        """
        تسجيل قراءة السكر
        
        Args:
            patient_id: معرف المريض
            reading_data: بيانات القراءة
            
        Returns:
            Dict: تحليل القراءة
        """
        try:
            reading_id = str(uuid.uuid4())
            
            # إنشاء سجل القراءة
            glucose_reading = GlucoseReading(
                reading_id=reading_id,
                patient_id=patient_id,
                glucose_value=reading_data['glucose_value'],
                reading_time=datetime.now(),
                meal_relation=reading_data.get('meal_relation', 'random'),
                notes=reading_data.get('notes', ''),
                symptoms=reading_data.get('symptoms', []),
                medication_taken=reading_data.get('medication_taken', False)
            )
            
            # تحليل القراءة
            analysis = self._analyze_glucose_reading(glucose_reading)
            
            # تحديد الإجراءات المطلوبة
            actions = self._determine_required_actions(glucose_reading, analysis)
            
            # تحديث الإحصائيات
            statistics = self._update_glucose_statistics(patient_id, glucose_reading)
            
            return {
                'success': True,
                'reading': glucose_reading.__dict__,
                'analysis': analysis,
                'required_actions': actions,
                'statistics': statistics
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_glucose_reading(self, reading: GlucoseReading) -> Dict:
        """تحليل قراءة السكر"""
        glucose_value = reading.glucose_value
        meal_relation = reading.meal_relation
        
        # تحديد النطاق المناسب للمقارنة
        if meal_relation == 'fasting':
            ranges = self.glucose_ranges['fasting']
        elif meal_relation in ['postprandial', 'after_meal']:
            ranges = self.glucose_ranges['postprandial']
        else:
            ranges = self.glucose_ranges['random']
        
        # تحديد مستوى السكر
        if glucose_value < 70:
            level = GlucoseLevel.LOW.value
            severity = 'mild' if glucose_value >= 54 else 'severe'
        elif glucose_value <= ranges['normal'][1]:
            level = GlucoseLevel.NORMAL.value
            severity = 'normal'
        elif glucose_value <= ranges.get('prediabetes', ranges.get('elevated', (0, 199)))[1]:
            level = GlucoseLevel.HIGH.value
            severity = 'mild'
        else:
            level = GlucoseLevel.VERY_HIGH.value
            severity = 'severe' if glucose_value > 300 else 'moderate'
        
        # تحليل الأعراض
        symptom_analysis = self._analyze_symptoms(reading.symptoms, level)
        
        return {
            'glucose_level': level,
            'severity': severity,
            'target_range': ranges['normal'],
            'deviation': glucose_value - ranges['normal'][1] if glucose_value > ranges['normal'][1] else 
                        ranges['normal'][0] - glucose_value if glucose_value < ranges['normal'][0] else 0,
            'symptom_analysis': symptom_analysis,
            'risk_assessment': self._assess_risk(glucose_value, severity, reading.symptoms)
        }
    
    def _analyze_symptoms(self, symptoms: List[str], glucose_level: str) -> Dict:
        """تحليل الأعراض"""
        if not symptoms:
            return {'match': 'no_symptoms', 'consistency': 'unknown'}
        
        # تحديد نوع الأعراض المتوقعة
        if glucose_level in [GlucoseLevel.LOW.value, GlucoseLevel.VERY_LOW.value]:
            expected_symptoms = (self.symptoms_database['hypoglycemia']['mild'] + 
                               self.symptoms_database['hypoglycemia']['moderate'])
        elif glucose_level in [GlucoseLevel.HIGH.value, GlucoseLevel.VERY_HIGH.value]:
            expected_symptoms = (self.symptoms_database['hyperglycemia']['mild'] + 
                               self.symptoms_database['hyperglycemia']['moderate'])
        else:
            return {'match': 'normal_range', 'consistency': 'good'}
        
        # فحص التطابق
        matching_symptoms = [s for s in symptoms if s in expected_symptoms]
        consistency = 'good' if len(matching_symptoms) > 0 else 'poor'
        
        return {
            'match': 'consistent' if matching_symptoms else 'inconsistent',
            'consistency': consistency,
            'matching_symptoms': matching_symptoms,
            'unexpected_symptoms': [s for s in symptoms if s not in expected_symptoms]
        }
    
    def _assess_risk(self, glucose_value: float, severity: str, symptoms: List[str]) -> str:
        """تقييم المخاطر"""
        if glucose_value < 54 or glucose_value > 400:
            return 'critical'
        elif glucose_value < 70 and 'فقدان الوعي' in symptoms:
            return 'high'
        elif glucose_value > 300 and severity == 'severe':
            return 'high'
        elif severity in ['moderate', 'severe']:
            return 'medium'
        else:
            return 'low'
    
    def _determine_required_actions(self, reading: GlucoseReading, analysis: Dict) -> List[Dict]:
        """تحديد الإجراءات المطلوبة"""
        actions = []
        glucose_value = reading.glucose_value
        risk_level = analysis['risk_assessment']
        
        if risk_level == 'critical':
            actions.append({
                'type': 'emergency',
                'priority': 'urgent',
                'action': 'اطلب المساعدة الطبية الفورية',
                'details': 'اتصل بالطوارئ أو اذهب لأقرب مستشفى'
            })
        
        if glucose_value < 70:
            actions.append({
                'type': 'treatment',
                'priority': 'immediate',
                'action': 'تناول 15 جرام كربوهيدرات سريعة',
                'details': 'عصير فواكه، أقراص جلوكوز، أو ملعقة عسل'
            })
            actions.append({
                'type': 'monitoring',
                'priority': 'immediate',
                'action': 'أعد قياس السكر بعد 15 دقيقة',
                'details': 'إذا لم يتحسن، كرر العلاج'
            })
        
        if glucose_value > 250:
            actions.append({
                'type': 'monitoring',
                'priority': 'high',
                'action': 'فحص الكيتونات في البول',
                'details': 'خاصة لمرضى النوع الأول'
            })
            actions.append({
                'type': 'hydration',
                'priority': 'high',
                'action': 'اشرب الماء بكثرة',
                'details': 'تجنب المشروبات السكرية'
            })
        
        if analysis['glucose_level'] != GlucoseLevel.NORMAL.value:
            actions.append({
                'type': 'consultation',
                'priority': 'medium',
                'action': 'استشر طبيبك',
                'details': 'لمراجعة خطة العلاج إذا تكررت القراءات غير الطبيعية'
            })
        
        return actions
    
    def _update_glucose_statistics(self, patient_id: str, reading: GlucoseReading) -> Dict:
        """تحديث إحصائيات السكر"""
        # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
        # هنا محاكاة للإحصائيات
        
        return {
            'average_glucose_7days': 145,
            'average_glucose_30days': 152,
            'time_in_range_percentage': 65,
            'readings_count_7days': 28,
            'readings_count_30days': 120,
            'last_hba1c_estimate': 7.2,
            'trend': 'improving'
        }
    
    def generate_diabetes_report(self, patient_id: str, period_days: int = 30) -> Dict:
        """
        إنتاج تقرير السكري
        
        Args:
            patient_id: معرف المريض
            period_days: فترة التقرير بالأيام
            
        Returns:
            Dict: تقرير السكري
        """
        try:
            report_id = str(uuid.uuid4())
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            # هنا محاكاة للتقرير
            
            report = {
                'report_id': report_id,
                'patient_id': patient_id,
                'period': {
                    'start_date': start_date.date().isoformat(),
                    'end_date': end_date.date().isoformat(),
                    'days': period_days
                },
                'glucose_summary': {
                    'total_readings': 85,
                    'average_glucose': 148,
                    'glucose_range': {
                        'minimum': 65,
                        'maximum': 285
                    },
                    'time_in_range': {
                        'target_range': '70-180 mg/dL',
                        'percentage': 68,
                        'time_below': 8,
                        'time_above': 24
                    },
                    'estimated_hba1c': 7.1
                },
                'patterns_analysis': {
                    'dawn_phenomenon': 'detected',
                    'postprandial_spikes': 'frequent',
                    'nocturnal_hypoglycemia': 'rare',
                    'exercise_response': 'good'
                },
                'medication_adherence': {
                    'overall_score': 85,
                    'missed_doses': 4,
                    'timing_consistency': 'good'
                },
                'lifestyle_factors': {
                    'diet_compliance': 75,
                    'exercise_frequency': 4,  # أيام في الأسبوع
                    'sleep_quality': 'fair',
                    'stress_level': 'moderate'
                },
                'complications_screening': {
                    'last_eye_exam': '2023-08-15',
                    'last_foot_exam': '2023-09-20',
                    'blood_pressure_control': 'good',
                    'cholesterol_levels': 'target'
                },
                'recommendations': [
                    'تحسين التحكم في السكر بعد الوجبات',
                    'زيادة تكرار ممارسة الرياضة',
                    'مراجعة جرعات الإنسولين مع الطبيب',
                    'تحسين جودة النوم'
                ],
                'next_appointments': [
                    {
                        'type': 'endocrinologist',
                        'recommended_date': (end_date + timedelta(days=90)).date().isoformat(),
                        'reason': 'مراجعة دورية'
                    },
                    {
                        'type': 'ophthalmologist',
                        'recommended_date': (end_date + timedelta(days=180)).date().isoformat(),
                        'reason': 'فحص العين السنوي'
                    }
                ]
            }
            
            return {
                'success': True,
                'report': report,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_diabetes_education_content(self, topic: str, diabetes_type: str = None) -> Dict:
        """
        الحصول على محتوى تعليمي عن السكري
        
        Args:
            topic: الموضوع المطلوب
            diabetes_type: نوع السكري
            
        Returns:
            Dict: المحتوى التعليمي
        """
        try:
            education_content = {
                'carb_counting': {
                    'title': 'حساب الكربوهيدرات',
                    'content': self.dietary_guidelines['carbohydrate_counting'],
                    'interactive_tools': [
                        'حاسبة الكربوهيدرات',
                        'دليل أحجام الحصص',
                        'تطبيق تتبع الطعام'
                    ]
                },
                'insulin_injection': {
                    'title': 'تقنيات حقن الإنسولين',
                    'content': {
                        'preparation': [
                            'اغسل يديك جيداً',
                            'تحقق من نوع وتاريخ انتهاء الإنسولين',
                            'دع الإنسولين يصل لدرجة حرارة الغرفة'
                        ],
                        'injection_sites': [
                            'البطن (الأسرع امتصاصاً)',
                            'الفخذ (امتصاص متوسط)',
                            'الذراع (امتصاص بطيء)'
                        ],
                        'technique': [
                            'نظف مكان الحقن بالكحول',
                            'اقرص الجلد برفق',
                            'أدخل الإبرة بزاوية 90 درجة',
                            'احقن الإنسولين ببطء',
                            'انتظر 10 ثوان قبل سحب الإبرة'
                        ]
                    },
                    'video_tutorials': [
                        'تقنية الحقن الصحيحة',
                        'تدوير مواقع الحقن',
                        'التعامل مع مشاكل الحقن'
                    ]
                },
                'hypoglycemia_management': {
                    'title': 'التعامل مع انخفاض السكر',
                    'content': {
                        'recognition': self.symptoms_database['hypoglycemia']['mild'],
                        'treatment': [
                            'قاعدة 15-15: 15 جرام كربوهيدرات سريعة',
                            'انتظر 15 دقيقة',
                            'أعد قياس السكر',
                            'كرر العلاج إذا لزم الأمر'
                        ],
                        'prevention': [
                            'تناول وجبات منتظمة',
                            'احمل معك مصدر سكر سريع',
                            'راقب السكر قبل الرياضة',
                            'اضبط جرعة الإنسولين حسب النشاط'
                        ]
                    }
                },
                'foot_care': {
                    'title': 'العناية بالقدمين',
                    'content': {
                        'daily_care': [
                            'افحص قدميك يومياً',
                            'اغسل قدميك بماء دافئ',
                            'جفف بين أصابع القدم',
                            'استخدم مرطب للجلد الجاف'
                        ],
                        'warning_signs': [
                            'جروح لا تشفى',
                            'تغير في لون الجلد',
                            'تورم أو احمرار',
                            'فقدان الإحساس'
                        ],
                        'prevention': [
                            'ارتد أحذية مريحة',
                            'تجنب المشي حافي القدمين',
                            'قص الأظافر بحذر',
                            'فحص دوري عند الطبيب'
                        ]
                    }
                }
            }
            
            if topic not in education_content:
                return {
                    'success': False,
                    'error': 'موضوع غير متوفر'
                }
            
            content = education_content[topic]
            
            # إضافة محتوى خاص بنوع السكري
            if diabetes_type:
                content['specific_notes'] = self._get_type_specific_notes(topic, diabetes_type)
            
            return {
                'success': True,
                'topic': topic,
                'content': content,
                'related_topics': self._get_related_topics(topic),
                'assessment_quiz': self._generate_assessment_quiz(topic)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_type_specific_notes(self, topic: str, diabetes_type: str) -> List[str]:
        """ملاحظات خاصة بنوع السكري"""
        notes = []
        
        if diabetes_type == DiabetesType.TYPE_1.value:
            if topic == 'carb_counting':
                notes.append('حساب الكربوهيدرات ضروري لتحديد جرعة الإنسولين')
            elif topic == 'hypoglycemia_management':
                notes.append('مرضى النوع الأول أكثر عرضة لانخفاض السكر الشديد')
        
        elif diabetes_type == DiabetesType.TYPE_2.value:
            if topic == 'carb_counting':
                notes.append('التركيز على تقليل الكربوهيدرات قد يساعد في التحكم')
            elif topic == 'foot_care':
                notes.append('مرضى النوع الثاني أكثر عرضة لمشاكل الدورة الدموية')
        
        return notes
    
    def _get_related_topics(self, topic: str) -> List[str]:
        """الموضوعات ذات الصلة"""
        related = {
            'carb_counting': ['insulin_injection', 'meal_planning'],
            'insulin_injection': ['carb_counting', 'hypoglycemia_management'],
            'hypoglycemia_management': ['insulin_injection', 'exercise_guidelines'],
            'foot_care': ['circulation_health', 'wound_care']
        }
        
        return related.get(topic, [])
    
    def _generate_assessment_quiz(self, topic: str) -> List[Dict]:
        """إنتاج اختبار تقييمي"""
        quizzes = {
            'carb_counting': [
                {
                    'question': 'كم جرام كربوهيدرات في شريحة خبز واحدة؟',
                    'options': ['10 جرام', '15 جرام', '20 جرام', '25 جرام'],
                    'correct_answer': 1,
                    'explanation': 'شريحة الخبز الواحدة تحتوي على حوالي 15 جرام كربوهيدرات'
                }
            ],
            'hypoglycemia_management': [
                {
                    'question': 'ما هو العلاج الأول لانخفاض السكر؟',
                    'options': ['شرب الماء', '15 جرام كربوهيدرات سريعة', 'تناول البروتين', 'الراحة'],
                    'correct_answer': 1,
                    'explanation': 'العلاج الأول هو تناول 15 جرام من الكربوهيدرات سريعة الامتصاص'
                }
            ]
        }
        
        return quizzes.get(topic, [])
    
    def create_medication_reminder(self, patient_id: str, medication_schedule: Dict) -> Dict:
        """
        إنشاء تذكيرات الأدوية
        
        Args:
            patient_id: معرف المريض
            medication_schedule: جدول الأدوية
            
        Returns:
            Dict: تذكيرات الأدوية
        """
        try:
            reminders = []
            
            for medication in medication_schedule['medications']:
                for time_slot in medication['schedule']:
                    reminder_id = str(uuid.uuid4())
                    
                    reminder = {
                        'reminder_id': reminder_id,
                        'patient_id': patient_id,
                        'medication_name': medication['name'],
                        'dosage': medication['dosage'],
                        'time': time_slot['time'],
                        'meal_relation': time_slot.get('meal_relation', 'independent'),
                        'special_instructions': medication.get('instructions', []),
                        'reminder_methods': ['app_notification', 'sms', 'email'],
                        'snooze_options': [5, 15, 30],  # دقائق
                        'created_at': datetime.now().isoformat()
                    }
                    
                    reminders.append(reminder)
            
            return {
                'success': True,
                'reminders': reminders,
                'total_reminders': len(reminders),
                'next_reminder': self._get_next_reminder(reminders)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_next_reminder(self, reminders: List[Dict]) -> Optional[Dict]:
        """الحصول على التذكير التالي"""
        if not reminders:
            return None
        
        now = datetime.now()
        upcoming_reminders = []
        
        for reminder in reminders:
            reminder_time = datetime.strptime(reminder['time'], '%H:%M').time()
            today_reminder = datetime.combine(now.date(), reminder_time)
            
            if today_reminder > now:
                upcoming_reminders.append({
                    'reminder': reminder,
                    'datetime': today_reminder
                })
            else:
                # التذكير التالي غداً
                tomorrow_reminder = today_reminder + timedelta(days=1)
                upcoming_reminders.append({
                    'reminder': reminder,
                    'datetime': tomorrow_reminder
                })
        
        if upcoming_reminders:
            next_reminder = min(upcoming_reminders, key=lambda x: x['datetime'])
            return next_reminder['reminder']
        
        return None

