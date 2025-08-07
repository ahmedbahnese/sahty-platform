"""
خدمة تحليل الفحوصات الطبية والتحاليل المخبرية
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class TestCategory(Enum):
    BLOOD_CHEMISTRY = "كيمياء الدم"
    HEMATOLOGY = "أمراض الدم"
    IMMUNOLOGY = "المناعة"
    MICROBIOLOGY = "الميكروبيولوجيا"
    HORMONES = "الهرمونات"
    CARDIAC_MARKERS = "علامات القلب"
    LIVER_FUNCTION = "وظائف الكبد"
    KIDNEY_FUNCTION = "وظائف الكلى"
    LIPID_PROFILE = "دهون الدم"
    DIABETES_MARKERS = "علامات السكري"

class TestStatus(Enum):
    NORMAL = "طبيعي"
    ABNORMAL_LOW = "منخفض"
    ABNORMAL_HIGH = "مرتفع"
    CRITICAL_LOW = "منخفض خطير"
    CRITICAL_HIGH = "مرتفع خطير"

class UrgencyLevel(Enum):
    ROUTINE = "روتيني"
    URGENT = "عاجل"
    STAT = "طارئ"

@dataclass
class LabTest:
    test_id: str
    test_name: str
    category: str
    value: float
    unit: str
    reference_range: tuple
    status: str
    urgency: str

class LabAnalysisService:
    def __init__(self):
        """تهيئة خدمة تحليل الفحوصات"""
        
        # قاعدة بيانات التحاليل المرجعية
        self.reference_ranges = {
            # كيمياء الدم
            'glucose_fasting': {
                'name': 'الجلوكوز (صائم)',
                'category': TestCategory.BLOOD_CHEMISTRY.value,
                'unit': 'mg/dL',
                'reference_range': {
                    'adult': (70, 100),
                    'elderly': (70, 110),
                    'child': (60, 100)
                },
                'critical_values': {'low': 50, 'high': 400},
                'interpretation': {
                    'low': 'انخفاض السكر - قد يشير لفرط جرعة الإنسولين',
                    'high': 'ارتفاع السكر - قد يشير لمرض السكري',
                    'normal': 'مستوى طبيعي للسكر'
                }
            },
            'hba1c': {
                'name': 'الهيموجلوبين السكري',
                'category': TestCategory.DIABETES_MARKERS.value,
                'unit': '%',
                'reference_range': {
                    'adult': (4.0, 5.6),
                    'diabetic_target': (0, 7.0)
                },
                'critical_values': {'high': 10.0},
                'interpretation': {
                    'normal': 'تحكم جيد في السكر',
                    'prediabetes': '5.7-6.4% - ما قبل السكري',
                    'diabetes': 'أكثر من 6.5% - مرض السكري'
                }
            },
            'creatinine': {
                'name': 'الكرياتينين',
                'category': TestCategory.KIDNEY_FUNCTION.value,
                'unit': 'mg/dL',
                'reference_range': {
                    'male': (0.7, 1.3),
                    'female': (0.6, 1.1),
                    'elderly_male': (0.7, 1.5),
                    'elderly_female': (0.6, 1.3)
                },
                'critical_values': {'high': 4.0},
                'interpretation': {
                    'high': 'قد يشير لضعف وظائف الكلى',
                    'normal': 'وظائف الكلى طبيعية'
                }
            },
            'urea': {
                'name': 'اليوريا',
                'category': TestCategory.KIDNEY_FUNCTION.value,
                'unit': 'mg/dL',
                'reference_range': {
                    'adult': (15, 45),
                    'elderly': (15, 50)
                },
                'critical_values': {'high': 100},
                'interpretation': {
                    'high': 'قد يشير لضعف وظائف الكلى أو الجفاف',
                    'normal': 'مستوى طبيعي'
                }
            },
            'alt': {
                'name': 'إنزيم ALT',
                'category': TestCategory.LIVER_FUNCTION.value,
                'unit': 'U/L',
                'reference_range': {
                    'male': (10, 40),
                    'female': (7, 35)
                },
                'critical_values': {'high': 200},
                'interpretation': {
                    'high': 'قد يشير لالتهاب أو تلف في الكبد',
                    'normal': 'وظائف الكبد طبيعية'
                }
            },
            'ast': {
                'name': 'إنزيم AST',
                'category': TestCategory.LIVER_FUNCTION.value,
                'unit': 'U/L',
                'reference_range': {
                    'male': (10, 40),
                    'female': (9, 32)
                },
                'critical_values': {'high': 200},
                'interpretation': {
                    'high': 'قد يشير لتلف في الكبد أو القلب أو العضلات',
                    'normal': 'مستوى طبيعي'
                }
            },
            'total_cholesterol': {
                'name': 'الكولسترول الكلي',
                'category': TestCategory.LIPID_PROFILE.value,
                'unit': 'mg/dL',
                'reference_range': {
                    'adult': (0, 200),
                    'borderline': (200, 239),
                    'high': (240, float('inf'))
                },
                'interpretation': {
                    'normal': 'مستوى مرغوب فيه',
                    'borderline': 'مستوى حدي - يحتاج متابعة',
                    'high': 'مستوى مرتفع - يزيد خطر أمراض القلب'
                }
            },
            'ldl_cholesterol': {
                'name': 'الكولسترول الضار LDL',
                'category': TestCategory.LIPID_PROFILE.value,
                'unit': 'mg/dL',
                'reference_range': {
                    'optimal': (0, 100),
                    'near_optimal': (100, 129),
                    'borderline': (130, 159),
                    'high': (160, 189),
                    'very_high': (190, float('inf'))
                },
                'interpretation': {
                    'optimal': 'مستوى مثالي',
                    'high': 'مستوى مرتفع - يزيد خطر أمراض القلب'
                }
            },
            'hdl_cholesterol': {
                'name': 'الكولسترول المفيد HDL',
                'category': TestCategory.LIPID_PROFILE.value,
                'unit': 'mg/dL',
                'reference_range': {
                    'male': (40, float('inf')),
                    'female': (50, float('inf'))
                },
                'interpretation': {
                    'low': 'مستوى منخفض - يزيد خطر أمراض القلب',
                    'normal': 'مستوى جيد - يحمي من أمراض القلب'
                }
            },
            'triglycerides': {
                'name': 'الدهون الثلاثية',
                'category': TestCategory.LIPID_PROFILE.value,
                'unit': 'mg/dL',
                'reference_range': {
                    'normal': (0, 150),
                    'borderline': (150, 199),
                    'high': (200, 499),
                    'very_high': (500, float('inf'))
                },
                'interpretation': {
                    'normal': 'مستوى طبيعي',
                    'high': 'مستوى مرتفع - يزيد خطر أمراض القلب'
                }
            },
            'hemoglobin': {
                'name': 'الهيموجلوبين',
                'category': TestCategory.HEMATOLOGY.value,
                'unit': 'g/dL',
                'reference_range': {
                    'male': (13.8, 17.2),
                    'female': (12.1, 15.1),
                    'child': (11.0, 16.0)
                },
                'critical_values': {'low': 7.0, 'high': 20.0},
                'interpretation': {
                    'low': 'فقر دم - قد يحتاج علاج',
                    'high': 'زيادة في كريات الدم الحمراء',
                    'normal': 'مستوى طبيعي'
                }
            },
            'wbc_count': {
                'name': 'عدد كريات الدم البيضاء',
                'category': TestCategory.HEMATOLOGY.value,
                'unit': '×10³/μL',
                'reference_range': {
                    'adult': (4.5, 11.0),
                    'child': (5.0, 14.5)
                },
                'critical_values': {'low': 2.0, 'high': 30.0},
                'interpretation': {
                    'low': 'نقص في المناعة - قد يشير لعدوى أو مرض',
                    'high': 'زيادة قد تشير لعدوى أو التهاب',
                    'normal': 'مستوى طبيعي'
                }
            },
            'platelet_count': {
                'name': 'عدد الصفائح الدموية',
                'category': TestCategory.HEMATOLOGY.value,
                'unit': '×10³/μL',
                'reference_range': {
                    'adult': (150, 450)
                },
                'critical_values': {'low': 50, 'high': 1000},
                'interpretation': {
                    'low': 'نقص الصفائح - خطر النزيف',
                    'high': 'زيادة الصفائح - خطر التجلط',
                    'normal': 'مستوى طبيعي'
                }
            },
            'tsh': {
                'name': 'الهرمون المحفز للغدة الدرقية',
                'category': TestCategory.HORMONES.value,
                'unit': 'mIU/L',
                'reference_range': {
                    'adult': (0.4, 4.0),
                    'elderly': (0.5, 5.0)
                },
                'interpretation': {
                    'low': 'قد يشير لفرط نشاط الغدة الدرقية',
                    'high': 'قد يشير لقصور الغدة الدرقية',
                    'normal': 'وظائف الغدة الدرقية طبيعية'
                }
            },
            'vitamin_d': {
                'name': 'فيتامين د',
                'category': TestCategory.HORMONES.value,
                'unit': 'ng/mL',
                'reference_range': {
                    'deficient': (0, 20),
                    'insufficient': (20, 30),
                    'sufficient': (30, 100),
                    'toxic': (100, float('inf'))
                },
                'interpretation': {
                    'deficient': 'نقص شديد - يحتاج علاج فوري',
                    'insufficient': 'نقص - يحتاج مكملات',
                    'sufficient': 'مستوى كافي',
                    'toxic': 'مستوى سام - توقف عن المكملات'
                }
            },
            'vitamin_b12': {
                'name': 'فيتامين ب12',
                'category': TestCategory.HORMONES.value,
                'unit': 'pg/mL',
                'reference_range': {
                    'adult': (200, 900)
                },
                'interpretation': {
                    'low': 'نقص فيتامين ب12 - قد يسبب فقر دم',
                    'normal': 'مستوى كافي'
                }
            },
            'ferritin': {
                'name': 'الفيريتين',
                'category': TestCategory.HEMATOLOGY.value,
                'unit': 'ng/mL',
                'reference_range': {
                    'male': (12, 300),
                    'female': (12, 150),
                    'postmenopausal': (12, 200)
                },
                'interpretation': {
                    'low': 'نقص مخزون الحديد',
                    'high': 'زيادة مخزون الحديد - قد يشير لالتهاب',
                    'normal': 'مخزون حديد طبيعي'
                }
            }
        }
        
        # أنماط التحاليل الشائعة
        self.test_panels = {
            'complete_metabolic_panel': {
                'name': 'الفحص الشامل الأساسي',
                'tests': ['glucose_fasting', 'creatinine', 'urea', 'alt', 'ast'],
                'purpose': 'تقييم عام لوظائف الجسم الأساسية'
            },
            'lipid_panel': {
                'name': 'فحص دهون الدم',
                'tests': ['total_cholesterol', 'ldl_cholesterol', 'hdl_cholesterol', 'triglycerides'],
                'purpose': 'تقييم خطر أمراض القلب والشرايين'
            },
            'diabetes_panel': {
                'name': 'فحص السكري',
                'tests': ['glucose_fasting', 'hba1c'],
                'purpose': 'تشخيص ومتابعة مرض السكري'
            },
            'thyroid_panel': {
                'name': 'فحص الغدة الدرقية',
                'tests': ['tsh'],
                'purpose': 'تقييم وظائف الغدة الدرقية'
            },
            'anemia_panel': {
                'name': 'فحص فقر الدم',
                'tests': ['hemoglobin', 'ferritin', 'vitamin_b12'],
                'purpose': 'تشخيص أسباب فقر الدم'
            },
            'complete_blood_count': {
                'name': 'صورة الدم الكاملة',
                'tests': ['hemoglobin', 'wbc_count', 'platelet_count'],
                'purpose': 'تقييم عام لخلايا الدم'
            }
        }
        
        # التفاعلات والعلاقات بين التحاليل
        self.test_correlations = {
            'diabetes_risk': {
                'primary_tests': ['glucose_fasting', 'hba1c'],
                'supporting_tests': ['triglycerides', 'hdl_cholesterol'],
                'risk_factors': {
                    'glucose_fasting': '>100',
                    'hba1c': '>5.7',
                    'triglycerides': '>150',
                    'hdl_cholesterol': '<40 (male), <50 (female)'
                }
            },
            'cardiovascular_risk': {
                'primary_tests': ['total_cholesterol', 'ldl_cholesterol', 'hdl_cholesterol'],
                'supporting_tests': ['triglycerides', 'glucose_fasting'],
                'risk_factors': {
                    'total_cholesterol': '>200',
                    'ldl_cholesterol': '>130',
                    'hdl_cholesterol': '<40 (male), <50 (female)',
                    'triglycerides': '>150'
                }
            },
            'kidney_function': {
                'primary_tests': ['creatinine', 'urea'],
                'supporting_tests': ['glucose_fasting'],
                'risk_factors': {
                    'creatinine': '>1.3 (male), >1.1 (female)',
                    'urea': '>45'
                }
            }
        }
        
        # توصيات المتابعة
        self.follow_up_recommendations = {
            'abnormal_glucose': {
                'immediate': ['إعادة الفحص خلال أسبوع', 'استشارة طبيب باطنة'],
                'lifestyle': ['تقليل السكريات', 'ممارسة الرياضة', 'إنقاص الوزن'],
                'monitoring': ['فحص HbA1c كل 3 أشهر', 'مراقبة السكر يومياً']
            },
            'abnormal_lipids': {
                'immediate': ['استشارة طبيب قلب', 'تقييم خطر أمراض القلب'],
                'lifestyle': ['نظام غذائي قليل الدهون', 'ممارسة الرياضة', 'الإقلاع عن التدخين'],
                'monitoring': ['إعادة الفحص كل 6 أشهر']
            },
            'abnormal_kidney': {
                'immediate': ['استشارة طبيب كلى', 'فحص البول'],
                'lifestyle': ['تقليل الملح', 'شرب الماء بكثرة', 'تجنب المسكنات'],
                'monitoring': ['فحص دوري كل 3 أشهر']
            },
            'abnormal_liver': {
                'immediate': ['استشارة طبيب كبد', 'فحص فيروسات الكبد'],
                'lifestyle': ['تجنب الكحول', 'تقليل الأدوية غير الضرورية'],
                'monitoring': ['إعادة الفحص كل شهر']
            }
        }
    
    def analyze_lab_results(self, patient_id: str, lab_data: Dict) -> Dict:
        """
        تحليل نتائج الفحوصات المخبرية
        
        Args:
            patient_id: معرف المريض
            lab_data: بيانات التحاليل
            
        Returns:
            Dict: تحليل شامل للنتائج
        """
        try:
            analysis_id = str(uuid.uuid4())
            patient_info = lab_data.get('patient_info', {})
            test_results = lab_data.get('test_results', [])
            
            # تحليل كل فحص على حدة
            individual_analyses = []
            abnormal_results = []
            critical_results = []
            
            for test_result in test_results:
                test_analysis = self._analyze_individual_test(test_result, patient_info)
                individual_analyses.append(test_analysis)
                
                if test_analysis['status'] != TestStatus.NORMAL.value:
                    abnormal_results.append(test_analysis)
                
                if test_analysis['urgency'] == UrgencyLevel.STAT.value:
                    critical_results.append(test_analysis)
            
            # تحليل الأنماط والعلاقات
            pattern_analysis = self._analyze_test_patterns(individual_analyses, patient_info)
            
            # تقييم المخاطر الصحية
            risk_assessment = self._assess_health_risks(individual_analyses, patient_info)
            
            # توصيات المتابعة
            recommendations = self._generate_recommendations(
                abnormal_results, critical_results, pattern_analysis, risk_assessment
            )
            
            # إنشاء التقرير الشامل
            comprehensive_analysis = {
                'analysis_id': analysis_id,
                'patient_id': patient_id,
                'analysis_date': datetime.now().isoformat(),
                'test_date': lab_data.get('test_date', datetime.now().date().isoformat()),
                'laboratory': lab_data.get('laboratory', 'غير محدد'),
                'summary': {
                    'total_tests': len(test_results),
                    'normal_tests': len([t for t in individual_analyses if t['status'] == TestStatus.NORMAL.value]),
                    'abnormal_tests': len(abnormal_results),
                    'critical_tests': len(critical_results),
                    'overall_status': self._determine_overall_status(individual_analyses)
                },
                'individual_results': individual_analyses,
                'abnormal_results': abnormal_results,
                'critical_results': critical_results,
                'pattern_analysis': pattern_analysis,
                'risk_assessment': risk_assessment,
                'recommendations': recommendations,
                'follow_up_schedule': self._create_follow_up_schedule(abnormal_results, risk_assessment),
                'lifestyle_modifications': self._suggest_lifestyle_modifications(pattern_analysis, risk_assessment)
            }
            
            return {
                'success': True,
                'analysis': comprehensive_analysis
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحليل الفحوصات: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_individual_test(self, test_result: Dict, patient_info: Dict) -> Dict:
        """تحليل فحص مفرد"""
        test_code = test_result['test_code']
        test_value = test_result['value']
        
        if test_code not in self.reference_ranges:
            return {
                'test_code': test_code,
                'test_name': test_result.get('name', test_code),
                'value': test_value,
                'unit': test_result.get('unit', ''),
                'status': 'unknown',
                'interpretation': 'فحص غير معروف في قاعدة البيانات',
                'urgency': UrgencyLevel.ROUTINE.value
            }
        
        test_info = self.reference_ranges[test_code]
        
        # تحديد النطاق المرجعي المناسب
        reference_range = self._get_appropriate_reference_range(test_info, patient_info)
        
        # تحديد حالة النتيجة
        status = self._determine_test_status(test_value, reference_range, test_info)
        
        # تحديد مستوى الإلحاح
        urgency = self._determine_urgency(test_value, test_info)
        
        # الحصول على التفسير
        interpretation = self._get_test_interpretation(test_code, test_value, status, test_info)
        
        return {
            'test_code': test_code,
            'test_name': test_info['name'],
            'category': test_info['category'],
            'value': test_value,
            'unit': test_info['unit'],
            'reference_range': reference_range,
            'status': status,
            'urgency': urgency,
            'interpretation': interpretation,
            'clinical_significance': self._get_clinical_significance(test_code, status)
        }
    
    def _get_appropriate_reference_range(self, test_info: Dict, patient_info: Dict) -> tuple:
        """تحديد النطاق المرجعي المناسب"""
        age = patient_info.get('age', 30)
        gender = patient_info.get('gender', 'adult')
        
        reference_ranges = test_info['reference_range']
        
        # اختيار النطاق الأنسب
        if age >= 65 and 'elderly' in reference_ranges:
            return reference_ranges['elderly']
        elif age < 18 and 'child' in reference_ranges:
            return reference_ranges['child']
        elif gender == 'male' and 'male' in reference_ranges:
            return reference_ranges['male']
        elif gender == 'female' and 'female' in reference_ranges:
            return reference_ranges['female']
        else:
            return reference_ranges.get('adult', list(reference_ranges.values())[0])
    
    def _determine_test_status(self, value: float, reference_range: tuple, test_info: Dict) -> str:
        """تحديد حالة الفحص"""
        min_normal, max_normal = reference_range
        critical_values = test_info.get('critical_values', {})
        
        # فحص القيم الحرجة أولاً
        if 'low' in critical_values and value <= critical_values['low']:
            return TestStatus.CRITICAL_LOW.value
        elif 'high' in critical_values and value >= critical_values['high']:
            return TestStatus.CRITICAL_HIGH.value
        
        # فحص النطاق الطبيعي
        if value < min_normal:
            return TestStatus.ABNORMAL_LOW.value
        elif value > max_normal:
            return TestStatus.ABNORMAL_HIGH.value
        else:
            return TestStatus.NORMAL.value
    
    def _determine_urgency(self, value: float, test_info: Dict) -> str:
        """تحديد مستوى الإلحاح"""
        critical_values = test_info.get('critical_values', {})
        
        if (('low' in critical_values and value <= critical_values['low']) or
            ('high' in critical_values and value >= critical_values['high'])):
            return UrgencyLevel.STAT.value
        
        # منطق إضافي لتحديد الإلحاح
        reference_range = list(test_info['reference_range'].values())[0]
        min_normal, max_normal = reference_range
        
        if value < min_normal * 0.5 or value > max_normal * 2:
            return UrgencyLevel.URGENT.value
        
        return UrgencyLevel.ROUTINE.value
    
    def _get_test_interpretation(self, test_code: str, value: float, status: str, test_info: Dict) -> str:
        """الحصول على تفسير الفحص"""
        interpretations = test_info.get('interpretation', {})
        
        if status == TestStatus.NORMAL.value:
            return interpretations.get('normal', 'النتيجة ضمن النطاق الطبيعي')
        elif status in [TestStatus.ABNORMAL_LOW.value, TestStatus.CRITICAL_LOW.value]:
            return interpretations.get('low', 'النتيجة أقل من الطبيعي')
        elif status in [TestStatus.ABNORMAL_HIGH.value, TestStatus.CRITICAL_HIGH.value]:
            return interpretations.get('high', 'النتيجة أعلى من الطبيعي')
        
        return 'تحتاج لتفسير طبي متخصص'
    
    def _get_clinical_significance(self, test_code: str, status: str) -> str:
        """الحصول على الأهمية السريرية"""
        if status == TestStatus.NORMAL.value:
            return 'لا توجد مخاوف سريرية'
        
        clinical_significance = {
            'glucose_fasting': 'مهم لتشخيص ومتابعة مرض السكري',
            'hba1c': 'مؤشر التحكم في السكر خلال 2-3 أشهر الماضية',
            'creatinine': 'مؤشر رئيسي لوظائف الكلى',
            'alt': 'مؤشر لصحة الكبد',
            'total_cholesterol': 'عامل خطر لأمراض القلب والشرايين',
            'hemoglobin': 'مؤشر لفقر الدم أو زيادة كريات الدم الحمراء',
            'tsh': 'مؤشر لوظائف الغدة الدرقية'
        }
        
        return clinical_significance.get(test_code, 'يحتاج تقييم طبي')
    
    def _analyze_test_patterns(self, individual_analyses: List[Dict], patient_info: Dict) -> Dict:
        """تحليل الأنماط والعلاقات بين التحاليل"""
        patterns = {
            'metabolic_syndrome_indicators': [],
            'diabetes_risk_factors': [],
            'cardiovascular_risk_factors': [],
            'kidney_dysfunction_signs': [],
            'liver_dysfunction_signs': [],
            'anemia_indicators': [],
            'thyroid_dysfunction_signs': []
        }
        
        # تحليل متلازمة الأيض
        glucose = self._find_test_result(individual_analyses, 'glucose_fasting')
        triglycerides = self._find_test_result(individual_analyses, 'triglycerides')
        hdl = self._find_test_result(individual_analyses, 'hdl_cholesterol')
        
        if glucose and glucose['status'] != TestStatus.NORMAL.value:
            patterns['metabolic_syndrome_indicators'].append('ارتفاع السكر')
            patterns['diabetes_risk_factors'].append('سكر الدم غير طبيعي')
        
        if triglycerides and triglycerides['status'] == TestStatus.ABNORMAL_HIGH.value:
            patterns['metabolic_syndrome_indicators'].append('ارتفاع الدهون الثلاثية')
            patterns['cardiovascular_risk_factors'].append('دهون ثلاثية مرتفعة')
        
        if hdl and hdl['status'] == TestStatus.ABNORMAL_LOW.value:
            patterns['metabolic_syndrome_indicators'].append('انخفاض الكولسترول المفيد')
            patterns['cardiovascular_risk_factors'].append('كولسترول مفيد منخفض')
        
        # تحليل وظائف الكلى
        creatinine = self._find_test_result(individual_analyses, 'creatinine')
        urea = self._find_test_result(individual_analyses, 'urea')
        
        if creatinine and creatinine['status'] == TestStatus.ABNORMAL_HIGH.value:
            patterns['kidney_dysfunction_signs'].append('ارتفاع الكرياتينين')
        
        if urea and urea['status'] == TestStatus.ABNORMAL_HIGH.value:
            patterns['kidney_dysfunction_signs'].append('ارتفاع اليوريا')
        
        # تحليل وظائف الكبد
        alt = self._find_test_result(individual_analyses, 'alt')
        ast = self._find_test_result(individual_analyses, 'ast')
        
        if alt and alt['status'] == TestStatus.ABNORMAL_HIGH.value:
            patterns['liver_dysfunction_signs'].append('ارتفاع إنزيم ALT')
        
        if ast and ast['status'] == TestStatus.ABNORMAL_HIGH.value:
            patterns['liver_dysfunction_signs'].append('ارتفاع إنزيم AST')
        
        # تحليل فقر الدم
        hemoglobin = self._find_test_result(individual_analyses, 'hemoglobin')
        ferritin = self._find_test_result(individual_analyses, 'ferritin')
        
        if hemoglobin and hemoglobin['status'] == TestStatus.ABNORMAL_LOW.value:
            patterns['anemia_indicators'].append('انخفاض الهيموجلوبين')
        
        if ferritin and ferritin['status'] == TestStatus.ABNORMAL_LOW.value:
            patterns['anemia_indicators'].append('نقص مخزون الحديد')
        
        return {
            'patterns_detected': patterns,
            'pattern_summary': self._summarize_patterns(patterns),
            'clinical_correlations': self._identify_clinical_correlations(individual_analyses)
        }
    
    def _find_test_result(self, analyses: List[Dict], test_code: str) -> Optional[Dict]:
        """البحث عن نتيجة فحص معين"""
        for analysis in analyses:
            if analysis['test_code'] == test_code:
                return analysis
        return None
    
    def _summarize_patterns(self, patterns: Dict) -> List[str]:
        """تلخيص الأنماط المكتشفة"""
        summary = []
        
        if len(patterns['metabolic_syndrome_indicators']) >= 2:
            summary.append('مؤشرات لمتلازمة الأيض')
        
        if patterns['diabetes_risk_factors']:
            summary.append('عوامل خطر للإصابة بالسكري')
        
        if patterns['cardiovascular_risk_factors']:
            summary.append('عوامل خطر لأمراض القلب والشرايين')
        
        if patterns['kidney_dysfunction_signs']:
            summary.append('علامات ضعف وظائف الكلى')
        
        if patterns['liver_dysfunction_signs']:
            summary.append('علامات ضعف وظائف الكبد')
        
        if patterns['anemia_indicators']:
            summary.append('مؤشرات فقر الدم')
        
        return summary if summary else ['لا توجد أنماط مرضية واضحة']
    
    def _identify_clinical_correlations(self, analyses: List[Dict]) -> List[Dict]:
        """تحديد الارتباطات السريرية"""
        correlations = []
        
        # ارتباط السكري بدهون الدم
        glucose = self._find_test_result(analyses, 'glucose_fasting')
        triglycerides = self._find_test_result(analyses, 'triglycerides')
        
        if (glucose and glucose['status'] != TestStatus.NORMAL.value and
            triglycerides and triglycerides['status'] == TestStatus.ABNORMAL_HIGH.value):
            correlations.append({
                'type': 'diabetes_lipid_correlation',
                'description': 'ارتباط بين ارتفاع السكر والدهون الثلاثية',
                'clinical_significance': 'يزيد خطر أمراض القلب والشرايين'
            })
        
        # ارتباط وظائف الكلى بالسكري
        creatinine = self._find_test_result(analyses, 'creatinine')
        
        if (glucose and glucose['status'] != TestStatus.NORMAL.value and
            creatinine and creatinine['status'] == TestStatus.ABNORMAL_HIGH.value):
            correlations.append({
                'type': 'diabetic_nephropathy',
                'description': 'احتمالية اعتلال الكلى السكري',
                'clinical_significance': 'يحتاج متابعة دقيقة لوظائف الكلى'
            })
        
        return correlations
    
    def _assess_health_risks(self, analyses: List[Dict], patient_info: Dict) -> Dict:
        """تقييم المخاطر الصحية"""
        risks = {
            'cardiovascular_risk': 'low',
            'diabetes_risk': 'low',
            'kidney_disease_risk': 'low',
            'liver_disease_risk': 'low',
            'overall_risk': 'low'
        }
        
        risk_factors = []
        
        # تقييم خطر أمراض القلب
        cv_risk_factors = 0
        cholesterol = self._find_test_result(analyses, 'total_cholesterol')
        ldl = self._find_test_result(analyses, 'ldl_cholesterol')
        hdl = self._find_test_result(analyses, 'hdl_cholesterol')
        triglycerides = self._find_test_result(analyses, 'triglycerides')
        
        if cholesterol and cholesterol['status'] == TestStatus.ABNORMAL_HIGH.value:
            cv_risk_factors += 1
            risk_factors.append('ارتفاع الكولسترول الكلي')
        
        if ldl and ldl['status'] == TestStatus.ABNORMAL_HIGH.value:
            cv_risk_factors += 1
            risk_factors.append('ارتفاع الكولسترول الضار')
        
        if hdl and hdl['status'] == TestStatus.ABNORMAL_LOW.value:
            cv_risk_factors += 1
            risk_factors.append('انخفاض الكولسترول المفيد')
        
        if triglycerides and triglycerides['status'] == TestStatus.ABNORMAL_HIGH.value:
            cv_risk_factors += 1
            risk_factors.append('ارتفاع الدهون الثلاثية')
        
        if cv_risk_factors >= 3:
            risks['cardiovascular_risk'] = 'high'
        elif cv_risk_factors >= 2:
            risks['cardiovascular_risk'] = 'moderate'
        
        # تقييم خطر السكري
        glucose = self._find_test_result(analyses, 'glucose_fasting')
        hba1c = self._find_test_result(analyses, 'hba1c')
        
        if glucose and glucose['status'] == TestStatus.ABNORMAL_HIGH.value:
            risks['diabetes_risk'] = 'high' if glucose['value'] >= 126 else 'moderate'
            risk_factors.append('ارتفاع سكر الدم')
        
        if hba1c and hba1c['status'] == TestStatus.ABNORMAL_HIGH.value:
            if hba1c['value'] >= 6.5:
                risks['diabetes_risk'] = 'high'
            elif hba1c['value'] >= 5.7:
                risks['diabetes_risk'] = 'moderate'
            risk_factors.append('ارتفاع الهيموجلوبين السكري')
        
        # تقييم خطر أمراض الكلى
        creatinine = self._find_test_result(analyses, 'creatinine')
        urea = self._find_test_result(analyses, 'urea')
        
        if creatinine and creatinine['status'] == TestStatus.ABNORMAL_HIGH.value:
            risks['kidney_disease_risk'] = 'high' if creatinine['value'] >= 2.0 else 'moderate'
            risk_factors.append('ارتفاع الكرياتينين')
        
        if urea and urea['status'] == TestStatus.ABNORMAL_HIGH.value:
            risks['kidney_disease_risk'] = 'moderate'
            risk_factors.append('ارتفاع اليوريا')
        
        # تحديد المخاطر الإجمالية
        high_risks = [r for r in risks.values() if r == 'high']
        moderate_risks = [r for r in risks.values() if r == 'moderate']
        
        if high_risks:
            risks['overall_risk'] = 'high'
        elif moderate_risks:
            risks['overall_risk'] = 'moderate'
        
        return {
            'risk_levels': risks,
            'risk_factors': risk_factors,
            'risk_score': self._calculate_risk_score(risks),
            'risk_explanation': self._explain_risk_assessment(risks, risk_factors)
        }
    
    def _calculate_risk_score(self, risks: Dict) -> int:
        """حساب نقاط المخاطر"""
        score = 0
        for risk_level in risks.values():
            if risk_level == 'high':
                score += 3
            elif risk_level == 'moderate':
                score += 2
            elif risk_level == 'low':
                score += 1
        
        return score
    
    def _explain_risk_assessment(self, risks: Dict, risk_factors: List[str]) -> str:
        """شرح تقييم المخاطر"""
        if risks['overall_risk'] == 'high':
            return f"مستوى خطر مرتفع بناءً على: {', '.join(risk_factors)}. يحتاج متابعة طبية عاجلة."
        elif risks['overall_risk'] == 'moderate':
            return f"مستوى خطر متوسط بناءً على: {', '.join(risk_factors)}. يحتاج متابعة طبية منتظمة."
        else:
            return "مستوى خطر منخفض. استمر في المتابعة الدورية."
    
    def _determine_overall_status(self, analyses: List[Dict]) -> str:
        """تحديد الحالة الإجمالية"""
        critical_count = len([a for a in analyses if a['urgency'] == UrgencyLevel.STAT.value])
        abnormal_count = len([a for a in analyses if a['status'] != TestStatus.NORMAL.value])
        total_count = len(analyses)
        
        if critical_count > 0:
            return 'critical'
        elif abnormal_count > total_count * 0.5:
            return 'concerning'
        elif abnormal_count > 0:
            return 'needs_attention'
        else:
            return 'normal'
    
    def _generate_recommendations(self, abnormal_results: List[Dict], 
                                critical_results: List[Dict],
                                pattern_analysis: Dict, 
                                risk_assessment: Dict) -> Dict:
        """إنتاج التوصيات"""
        recommendations = {
            'immediate_actions': [],
            'medical_consultations': [],
            'follow_up_tests': [],
            'lifestyle_changes': [],
            'monitoring_schedule': []
        }
        
        # إجراءات فورية للنتائج الحرجة
        if critical_results:
            recommendations['immediate_actions'].append('اطلب المساعدة الطبية الفورية')
            recommendations['immediate_actions'].append('لا تؤجل زيارة الطبيب')
        
        # استشارات طبية
        specialties_needed = set()
        for result in abnormal_results:
            if result['category'] == TestCategory.DIABETES_MARKERS.value:
                specialties_needed.add('طبيب باطنة أو غدد صماء')
            elif result['category'] == TestCategory.KIDNEY_FUNCTION.value:
                specialties_needed.add('طبيب كلى')
            elif result['category'] == TestCategory.LIVER_FUNCTION.value:
                specialties_needed.add('طبيب كبد')
            elif result['category'] == TestCategory.LIPID_PROFILE.value:
                specialties_needed.add('طبيب قلب')
            elif result['category'] == TestCategory.HEMATOLOGY.value:
                specialties_needed.add('طبيب أمراض دم')
        
        recommendations['medical_consultations'] = list(specialties_needed)
        
        # فحوصات المتابعة
        if risk_assessment['risk_levels']['diabetes_risk'] in ['moderate', 'high']:
            recommendations['follow_up_tests'].append('إعادة فحص السكر والهيموجلوبين السكري')
        
        if risk_assessment['risk_levels']['cardiovascular_risk'] in ['moderate', 'high']:
            recommendations['follow_up_tests'].append('تخطيط القلب وفحص الشرايين')
        
        # تغييرات نمط الحياة
        if 'عوامل خطر للإصابة بالسكري' in pattern_analysis['pattern_summary']:
            recommendations['lifestyle_changes'].extend([
                'اتباع نظام غذائي صحي قليل السكريات',
                'ممارسة الرياضة بانتظام',
                'إنقاص الوزن إذا لزم الأمر'
            ])
        
        if 'عوامل خطر لأمراض القلب والشرايين' in pattern_analysis['pattern_summary']:
            recommendations['lifestyle_changes'].extend([
                'تقليل الدهون المشبعة في الطعام',
                'الإقلاع عن التدخين',
                'تقليل الملح في الطعام'
            ])
        
        return recommendations
    
    def _create_follow_up_schedule(self, abnormal_results: List[Dict], 
                                 risk_assessment: Dict) -> List[Dict]:
        """إنشاء جدول المتابعة"""
        follow_up_schedule = []
        
        # متابعة حسب مستوى المخاطر
        if risk_assessment['risk_levels']['overall_risk'] == 'high':
            follow_up_schedule.append({
                'timeframe': 'خلال أسبوع',
                'tests': 'إعادة الفحوصات غير الطبيعية',
                'consultation': 'استشارة طبية عاجلة'
            })
        elif risk_assessment['risk_levels']['overall_risk'] == 'moderate':
            follow_up_schedule.append({
                'timeframe': 'خلال شهر',
                'tests': 'إعادة الفحوصات المهمة',
                'consultation': 'استشارة طبية'
            })
        
        # متابعة دورية
        follow_up_schedule.append({
            'timeframe': 'كل 3-6 أشهر',
            'tests': 'فحوصات دورية شاملة',
            'consultation': 'متابعة دورية'
        })
        
        return follow_up_schedule
    
    def _suggest_lifestyle_modifications(self, pattern_analysis: Dict, 
                                       risk_assessment: Dict) -> List[Dict]:
        """اقتراح تعديلات نمط الحياة"""
        modifications = []
        
        # تعديلات غذائية
        if 'عوامل خطر للإصابة بالسكري' in pattern_analysis['pattern_summary']:
            modifications.append({
                'category': 'التغذية',
                'recommendations': [
                    'تقليل السكريات البسيطة',
                    'زيادة الألياف والخضروات',
                    'تناول وجبات صغيرة متكررة',
                    'شرب الماء بكثرة'
                ]
            })
        
        # النشاط البدني
        if risk_assessment['risk_levels']['cardiovascular_risk'] in ['moderate', 'high']:
            modifications.append({
                'category': 'النشاط البدني',
                'recommendations': [
                    'المشي 30 دقيقة يومياً',
                    'تمارين القلب 3 مرات أسبوعياً',
                    'تجنب الجلوس لفترات طويلة',
                    'صعود الدرج بدلاً من المصعد'
                ]
            })
        
        # إدارة التوتر
        modifications.append({
            'category': 'إدارة التوتر',
            'recommendations': [
                'ممارسة تقنيات الاسترخاء',
                'النوم 7-8 ساعات يومياً',
                'تجنب الضغوط النفسية',
                'ممارسة الهوايات'
            ]
        })
        
        return modifications
    
    def generate_patient_report(self, analysis: Dict, patient_info: Dict) -> Dict:
        """
        إنتاج تقرير للمريض
        
        Args:
            analysis: تحليل الفحوصات
            patient_info: معلومات المريض
            
        Returns:
            Dict: تقرير المريض
        """
        try:
            report = {
                'report_id': str(uuid.uuid4()),
                'patient_name': patient_info.get('name', 'غير محدد'),
                'patient_id': patient_info.get('patient_id'),
                'report_date': datetime.now().isoformat(),
                'test_date': analysis.get('test_date'),
                'laboratory': analysis.get('laboratory'),
                
                # ملخص مبسط
                'summary': {
                    'overall_status': self._translate_status(analysis['summary']['overall_status']),
                    'total_tests': analysis['summary']['total_tests'],
                    'normal_tests': analysis['summary']['normal_tests'],
                    'abnormal_tests': analysis['summary']['abnormal_tests'],
                    'key_findings': self._extract_key_findings(analysis)
                },
                
                # النتائج بلغة مبسطة
                'results_explanation': self._create_patient_friendly_explanation(analysis),
                
                # التوصيات المبسطة
                'what_to_do': {
                    'immediate_steps': analysis['recommendations']['immediate_actions'],
                    'doctor_visits': analysis['recommendations']['medical_consultations'],
                    'lifestyle_tips': analysis['lifestyle_modifications'],
                    'next_tests': analysis['follow_up_schedule']
                },
                
                # معلومات تثقيفية
                'educational_content': self._get_educational_content(analysis),
                
                # أسئلة شائعة
                'faq': self._generate_faq(analysis)
            }
            
            return {
                'success': True,
                'patient_report': report
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _translate_status(self, status: str) -> str:
        """ترجمة الحالة للمريض"""
        translations = {
            'normal': 'جميع النتائج طبيعية',
            'needs_attention': 'بعض النتائج تحتاج متابعة',
            'concerning': 'نتائج تحتاج اهتمام طبي',
            'critical': 'نتائج تحتاج تدخل طبي فوري'
        }
        return translations.get(status, status)
    
    def _extract_key_findings(self, analysis: Dict) -> List[str]:
        """استخراج النتائج الرئيسية"""
        key_findings = []
        
        for result in analysis['abnormal_results']:
            if result['urgency'] == UrgencyLevel.STAT.value:
                key_findings.append(f"{result['test_name']}: {result['interpretation']}")
        
        # إضافة أهم النتائج غير الطبيعية
        important_tests = ['glucose_fasting', 'hba1c', 'total_cholesterol', 'creatinine']
        for result in analysis['individual_results']:
            if (result['test_code'] in important_tests and 
                result['status'] != TestStatus.NORMAL.value):
                key_findings.append(f"{result['test_name']}: {result['interpretation']}")
        
        return key_findings[:5]  # أهم 5 نتائج
    
    def _create_patient_friendly_explanation(self, analysis: Dict) -> List[Dict]:
        """شرح النتائج بلغة مبسطة"""
        explanations = []
        
        for result in analysis['individual_results']:
            if result['status'] != TestStatus.NORMAL.value:
                explanation = {
                    'test_name': result['test_name'],
                    'your_result': f"{result['value']} {result['unit']}",
                    'normal_range': f"{result['reference_range'][0]}-{result['reference_range'][1]} {result['unit']}",
                    'what_it_means': result['interpretation'],
                    'importance': result['clinical_significance']
                }
                explanations.append(explanation)
        
        return explanations
    
    def _get_educational_content(self, analysis: Dict) -> List[Dict]:
        """الحصول على محتوى تثقيفي"""
        content = []
        
        # محتوى حسب الأنماط المكتشفة
        patterns = analysis['pattern_analysis']['pattern_summary']
        
        if 'عوامل خطر للإصابة بالسكري' in patterns:
            content.append({
                'topic': 'الوقاية من مرض السكري',
                'content': [
                    'مرض السكري يمكن الوقاية منه في كثير من الحالات',
                    'النظام الغذائي الصحي والرياضة هما أهم وسائل الوقاية',
                    'المتابعة الدورية مهمة للكشف المبكر'
                ]
            })
        
        if 'عوامل خطر لأمراض القلب والشرايين' in patterns:
            content.append({
                'topic': 'صحة القلب والشرايين',
                'content': [
                    'أمراض القلب هي السبب الأول للوفاة عالمياً',
                    'التحكم في الكولسترول وضغط الدم مهم جداً',
                    'الإقلاع عن التدخين يقلل المخاطر بشكل كبير'
                ]
            })
        
        return content
    
    def _generate_faq(self, analysis: Dict) -> List[Dict]:
        """إنتاج أسئلة شائعة"""
        faq = [
            {
                'question': 'هل نتائجي خطيرة؟',
                'answer': self._assess_severity_for_patient(analysis)
            },
            {
                'question': 'متى يجب أن أراجع الطبيب؟',
                'answer': self._when_to_see_doctor(analysis)
            },
            {
                'question': 'هل يمكنني تحسين نتائجي بنفسي؟',
                'answer': 'نعم، كثير من النتائج يمكن تحسينها بتغيير نمط الحياة مثل التغذية الصحية والرياضة'
            },
            {
                'question': 'كم مرة يجب أن أعيد الفحوصات؟',
                'answer': self._follow_up_frequency(analysis)
            }
        ]
        
        return faq
    
    def _assess_severity_for_patient(self, analysis: Dict) -> str:
        """تقييم الخطورة للمريض"""
        if analysis['summary']['overall_status'] == 'critical':
            return 'بعض النتائج تحتاج اهتمام طبي فوري. من المهم مراجعة الطبيب في أقرب وقت.'
        elif analysis['summary']['overall_status'] == 'concerning':
            return 'النتائج تحتاج متابعة طبية ولكن ليست خطيرة. راجع طبيبك خلال الأسبوع القادم.'
        elif analysis['summary']['overall_status'] == 'needs_attention':
            return 'معظم النتائج طبيعية مع بعض النقاط التي تحتاج متابعة بسيطة.'
        else:
            return 'جميع النتائج طبيعية. استمر في المتابعة الدورية.'
    
    def _when_to_see_doctor(self, analysis: Dict) -> str:
        """متى يراجع الطبيب"""
        if analysis['critical_results']:
            return 'فوراً - لديك نتائج تحتاج تدخل طبي عاجل'
        elif analysis['abnormal_results']:
            return 'خلال أسبوع - لمناقشة النتائج غير الطبيعية'
        else:
            return 'حسب الجدول المعتاد للفحوصات الدورية'
    
    def _follow_up_frequency(self, analysis: Dict) -> str:
        """تكرار المتابعة"""
        if analysis['risk_assessment']['risk_levels']['overall_risk'] == 'high':
            return 'كل 1-3 أشهر حسب توصية الطبيب'
        elif analysis['risk_assessment']['risk_levels']['overall_risk'] == 'moderate':
            return 'كل 3-6 أشهر'
        else:
            return 'كل 6-12 شهر للفحوصات الدورية'

