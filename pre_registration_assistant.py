"""
المساعد الذكي قبل التسجيل
يساعد المستخدمين الجدد على فهم النظام واستكشاف الميزات قبل إنشاء حساب
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from flask import current_app, session
from dataclasses import dataclass
from enum import Enum
import random

class UserType(Enum):
    PATIENT = "مريض"
    DOCTOR = "طبيب"
    HOSPITAL = "مستشفى"
    PHARMACY = "صيدلية"
    LAB = "مختبر"
    ADMIN = "مدير"

class InteractionType(Enum):
    GREETING = "ترحيب"
    FEATURE_EXPLORATION = "استكشاف الميزات"
    DEMO_REQUEST = "طلب عرض توضيحي"
    QUESTION = "سؤال"
    REGISTRATION_GUIDANCE = "إرشاد التسجيل"
    FEEDBACK = "تقييم"

class AssistantPersonality(Enum):
    PROFESSIONAL = "مهني"
    FRIENDLY = "ودود"
    HELPFUL = "مساعد"
    EXPERT = "خبير"

@dataclass
class PreRegistrationSession:
    session_id: str
    visitor_id: str
    start_time: datetime
    last_interaction: datetime
    user_type_interest: Optional[str]
    features_explored: List[str]
    questions_asked: List[str]
    demo_requests: List[str]
    interaction_count: int
    satisfaction_score: Optional[int]
    conversion_likelihood: float
    preferred_language: str
    device_type: str
    location: Optional[str]
    referral_source: Optional[str]

@dataclass
class AssistantResponse:
    response_id: str
    message: str
    response_type: str
    suggested_actions: List[Dict]
    quick_replies: List[str]
    multimedia_content: Optional[Dict]
    follow_up_questions: List[str]
    confidence_score: float

@dataclass
class FeatureDemo:
    feature_name: str
    demo_type: str
    description: str
    interactive_elements: List[Dict]
    sample_data: Dict
    benefits: List[str]
    user_testimonials: List[str]

class PreRegistrationAssistant:
    def __init__(self):
        """تهيئة المساعد الذكي قبل التسجيل"""
        
        # إعدادات المساعد
        self.assistant_settings = {
            'name': 'سارة',
            'personality': AssistantPersonality.FRIENDLY.value,
            'response_time_ms': 500,
            'max_session_duration_minutes': 30,
            'max_interactions_per_session': 50,
            'languages_supported': ['ar', 'en'],
            'default_language': 'ar'
        }
        
        # قاعدة المعرفة للمساعد
        self.knowledge_base = {
            'platform_overview': {
                'name': 'صحتك في أمان',
                'description': 'منصة طبية شاملة تجمع المرضى والأطباء والمستشفيات في مكان واحد',
                'key_benefits': [
                    'رعاية صحية متكاملة',
                    'تقنيات ذكاء اصطناعي متقدمة',
                    'أمان وخصوصية عالية',
                    'سهولة الاستخدام',
                    'متاح 24/7'
                ],
                'target_users': [
                    'المرضى وعائلاتهم',
                    'الأطباء والممرضين',
                    'المستشفيات والعيادات',
                    'الصيدليات والمختبرات'
                ]
            },
            
            'features_by_user_type': {
                UserType.PATIENT.value: {
                    'core_features': [
                        'حجز المواعيد الطبية',
                        'استشارات طبية فورية',
                        'ملف طبي رقمي شامل',
                        'تذكيرات الأدوية',
                        'تحليل الصور الطبية بالذكاء الاصطناعي',
                        'مراقبة العلامات الحيوية',
                        'خطط التغذية والتمارين',
                        'دعم الصحة النفسية'
                    ],
                    'advanced_features': [
                        'المساعد الصوتي الذكي',
                        'تحليل الأعراض التلقائي',
                        'التنبؤ بالمخاطر الصحية',
                        'ربط العائلة الرقمية',
                        'البطاقة الصحية الرقمية',
                        'دعم الحوامل المتخصص',
                        'إدارة مرض السكري',
                        'نظام الطوارئ الذكي'
                    ],
                    'unique_benefits': [
                        'وصول فوري للرعاية الطبية',
                        'تشخيص أولي بالذكاء الاصطناعي',
                        'متابعة مستمرة للحالة الصحية',
                        'توفير الوقت والجهد',
                        'تكلفة أقل من الطرق التقليدية'
                    ]
                },
                
                UserType.DOCTOR.value: {
                    'core_features': [
                        'إدارة المرضى والمواعيد',
                        'ملفات طبية إلكترونية',
                        'أدوات التشخيص المساعدة',
                        'وصف الأدوية الإلكتروني',
                        'التواصل مع المرضى',
                        'تحليل البيانات الطبية',
                        'التعليم الطبي المستمر',
                        'شبكة الأطباء المهنية'
                    ],
                    'advanced_features': [
                        'الذكاء الاصطناعي للتشخيص',
                        'تحليل الصور الطبية المتقدم',
                        'نظام دعم القرار الطبي',
                        'البحث الطبي والإحصائيات',
                        'التطبيب عن بُعد',
                        'إدارة العيادة الذكية',
                        'نظام الإحالات الإلكتروني',
                        'تتبع نتائج العلاج'
                    ],
                    'unique_benefits': [
                        'تحسين دقة التشخيص',
                        'توفير الوقت في العمل الإداري',
                        'وصول لأحدث المعلومات الطبية',
                        'تحسين التواصل مع المرضى',
                        'زيادة الكفاءة المهنية'
                    ]
                },
                
                UserType.HOSPITAL.value: {
                    'core_features': [
                        'نظام إدارة المستشفى الشامل',
                        'إدارة الأسرة والموارد',
                        'نظام المواعيد المتقدم',
                        'إدارة الموظفين الطبيين',
                        'نظام الفوترة والمحاسبة',
                        'إدارة المخزون الطبي',
                        'تقارير الأداء والإحصائيات',
                        'نظام الجودة والسلامة'
                    ],
                    'advanced_features': [
                        'الذكاء الاصطناعي لإدارة الموارد',
                        'التنبؤ بالطلب على الخدمات',
                        'نظام الطوارئ المتكامل',
                        'إدارة سلسلة التوريد الذكية',
                        'تحليلات البيانات المتقدمة',
                        'نظام الأمان السيبراني',
                        'التكامل مع الأنظمة الحكومية',
                        'إدارة الجائحات والأزمات'
                    ],
                    'unique_benefits': [
                        'تحسين كفاءة العمليات',
                        'تقليل التكاليف التشغيلية',
                        'تحسين جودة الرعاية',
                        'زيادة رضا المرضى',
                        'الامتثال للمعايير الدولية'
                    ]
                }
            },
            
            'common_questions': {
                'هل النظام آمن؟': {
                    'answer': 'نعم، نستخدم أعلى معايير الأمان العالمية مع تشفير متقدم وحماية البيانات الطبية حسب معايير HIPAA.',
                    'details': [
                        'تشفير البيانات من النهاية للنهاية',
                        'مصادقة متعددة العوامل',
                        'نسخ احتياطية آمنة',
                        'مراجعة أمنية دورية',
                        'امتثال للمعايير الدولية'
                    ]
                },
                'كم تكلفة الاستخدام؟': {
                    'answer': 'نقدم خطط متنوعة تناسب جميع الاحتياجات، بدءاً من الخطة المجانية للاستخدام الأساسي.',
                    'details': [
                        'خطة مجانية للميزات الأساسية',
                        'خطط مدفوعة للميزات المتقدمة',
                        'خصومات للمؤسسات الطبية',
                        'فترة تجريبية مجانية',
                        'دعم فني مجاني'
                    ]
                },
                'هل يدعم النظام اللغة العربية؟': {
                    'answer': 'نعم، النظام مصمم خصيصاً للمنطقة العربية ويدعم اللغة العربية بالكامل.',
                    'details': [
                        'واجهة عربية كاملة',
                        'مساعد صوتي باللغة العربية',
                        'محتوى طبي باللغة العربية',
                        'دعم فني باللغة العربية',
                        'تكامل مع الأنظمة المحلية'
                    ]
                },
                'كيف أبدأ الاستخدام؟': {
                    'answer': 'التسجيل سهل وسريع! اختر نوع حسابك واتبع الخطوات البسيطة.',
                    'details': [
                        'تسجيل في دقائق معدودة',
                        'تفعيل فوري للحساب',
                        'جولة تعريفية تفاعلية',
                        'دعم فني للبداية',
                        'تدريب مجاني على النظام'
                    ]
                }
            },
            
            'demo_scenarios': {
                'patient_journey': {
                    'title': 'رحلة المريض',
                    'description': 'تجربة كاملة لمريض من التسجيل حتى العلاج',
                    'steps': [
                        'إنشاء الملف الطبي',
                        'البحث عن طبيب مناسب',
                        'حجز موعد',
                        'الاستشارة الطبية',
                        'الحصول على الوصفة',
                        'متابعة العلاج'
                    ]
                },
                'doctor_workflow': {
                    'title': 'سير عمل الطبيب',
                    'description': 'كيف يدير الطبيب مرضاه بكفاءة',
                    'steps': [
                        'مراجعة جدول المواعيد',
                        'فحص الملفات الطبية',
                        'إجراء الاستشارة',
                        'كتابة التشخيص',
                        'وصف العلاج',
                        'جدولة المتابعة'
                    ]
                },
                'emergency_response': {
                    'title': 'الاستجابة للطوارئ',
                    'description': 'كيف يتعامل النظام مع الحالات الطارئة',
                    'steps': [
                        'اكتشاف الحالة الطارئة',
                        'تحديد أقرب مستشفى',
                        'إرسال البيانات الطبية',
                        'تنسيق الاستقبال',
                        'متابعة الحالة',
                        'التقرير النهائي'
                    ]
                }
            },
            
            'success_stories': [
                {
                    'title': 'إنقاذ حياة مريض سكري',
                    'description': 'اكتشف النظام ارتفاع خطير في السكر وأنقذ حياة المريض',
                    'impact': 'تجنب دخول غيبوبة سكر'
                },
                {
                    'title': 'تشخيص مبكر للسرطان',
                    'description': 'الذكاء الاصطناعي اكتشف علامات مبكرة للسرطان في صورة أشعة',
                    'impact': 'علاج ناجح بنسبة شفاء 95%'
                },
                {
                    'title': 'تحسين إدارة مستشفى',
                    'description': 'مستشفى حسن كفاءته بنسبة 40% باستخدام النظام',
                    'impact': 'تقليل أوقات الانتظار وزيادة رضا المرضى'
                }
            ]
        }
        
        # أنماط المحادثة والردود
        self.conversation_patterns = {
            'greetings': [
                'أهلاً وسهلاً! أنا سارة، مساعدتك الذكية في منصة صحتك في أمان 👋',
                'مرحباً بك! كيف يمكنني مساعدتك اليوم؟ 😊',
                'أهلاً! أنا هنا لأساعدك في اكتشاف كل ما تحتاجه من منصتنا الطبية'
            ],
            
            'feature_introductions': {
                'ai_diagnosis': 'تخيل أن تحصل على تشخيص أولي دقيق في ثوانٍ! نظام الذكاء الاصطناعي لدينا يحلل أعراضك ويقدم توصيات طبية موثوقة.',
                'telemedicine': 'لا حاجة للسفر أو الانتظار! استشر أفضل الأطباء من منزلك عبر الفيديو مع جودة عالية وأمان تام.',
                'health_monitoring': 'راقب صحتك باستمرار! النظام يتتبع علاماتك الحيوية ويحذرك من أي تغيرات مهمة.',
                'medication_management': 'لن تنسى دواءك مرة أخرى! نظام ذكي يذكرك بمواعيد الأدوية ويراقب التفاعلات الدوائية.'
            },
            
            'encouragement_phrases': [
                'ممتاز! هذا اختيار رائع',
                'أحسنت! هذه ميزة مفيدة جداً',
                'رائع! ستحب هذه الخاصية',
                'ممتاز! هذا سيوفر عليك الكثير'
            ],
            
            'transition_phrases': [
                'دعني أوضح لك المزيد...',
                'هل تريد أن نستكشف...',
                'ماذا عن أن نجرب...',
                'يمكنني أيضاً أن أريك...'
            ]
        }
        
        # قاعدة بيانات الجلسات (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.active_sessions = {}
        self.session_analytics = {}
        
        # إعدادات التخصيص
        self.personalization_settings = {
            'learning_enabled': True,
            'context_memory_duration': 30,  # دقيقة
            'max_suggestions': 5,
            'confidence_threshold': 0.7
        }
    
    def start_session(self, visitor_data: Dict) -> Dict:
        """
        بدء جلسة جديدة مع المساعد
        
        Args:
            visitor_data: بيانات الزائر
            
        Returns:
            Dict: معلومات الجلسة والترحيب
        """
        try:
            # إنشاء معرف الجلسة
            session_id = str(uuid.uuid4())
            visitor_id = visitor_data.get('visitor_id', str(uuid.uuid4()))
            
            # إنشاء جلسة جديدة
            session = PreRegistrationSession(
                session_id=session_id,
                visitor_id=visitor_id,
                start_time=datetime.now(),
                last_interaction=datetime.now(),
                user_type_interest=None,
                features_explored=[],
                questions_asked=[],
                demo_requests=[],
                interaction_count=0,
                satisfaction_score=None,
                conversion_likelihood=0.5,
                preferred_language=visitor_data.get('language', 'ar'),
                device_type=visitor_data.get('device_type', 'desktop'),
                location=visitor_data.get('location'),
                referral_source=visitor_data.get('referral_source')
            )
            
            # حفظ الجلسة
            self.active_sessions[session_id] = session
            
            # إنشاء رسالة الترحيب المخصصة
            welcome_message = self._generate_welcome_message(session)
            
            # اقتراحات البداية
            initial_suggestions = self._get_initial_suggestions(session)
            
            return {
                'success': True,
                'session_id': session_id,
                'welcome_message': welcome_message,
                'assistant_name': self.assistant_settings['name'],
                'initial_suggestions': initial_suggestions,
                'quick_actions': self._get_quick_actions(),
                'estimated_session_duration': '5-10 دقائق'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في بدء الجلسة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في بدء المحادثة'
            }
    
    def process_message(self, session_id: str, message: str, message_type: str = 'text') -> Dict:
        """
        معالجة رسالة من المستخدم
        
        Args:
            session_id: معرف الجلسة
            message: الرسالة
            message_type: نوع الرسالة
            
        Returns:
            Dict: رد المساعد
        """
        try:
            if session_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': 'الجلسة غير موجودة'
                }
            
            session = self.active_sessions[session_id]
            
            # تحديث الجلسة
            session.last_interaction = datetime.now()
            session.interaction_count += 1
            
            # تحليل الرسالة
            intent = self._analyze_message_intent(message, session)
            
            # إنتاج الرد
            response = self._generate_response(intent, message, session)
            
            # تحديث سياق الجلسة
            self._update_session_context(session, intent, message)
            
            # تحديث احتمالية التحويل
            session.conversion_likelihood = self._calculate_conversion_likelihood(session)
            
            return {
                'success': True,
                'response': response,
                'session_context': self._get_session_summary(session),
                'conversion_likelihood': session.conversion_likelihood
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في معالجة الرسالة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في معالجة الرسالة'
            }
    
    def request_demo(self, session_id: str, demo_type: str) -> Dict:
        """
        طلب عرض توضيحي
        
        Args:
            session_id: معرف الجلسة
            demo_type: نوع العرض التوضيحي
            
        Returns:
            Dict: العرض التوضيحي
        """
        try:
            if session_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': 'الجلسة غير موجودة'
                }
            
            session = self.active_sessions[session_id]
            session.demo_requests.append(demo_type)
            
            # إنشاء العرض التوضيحي
            demo = self._create_interactive_demo(demo_type, session)
            
            # تحديث احتمالية التحويل
            session.conversion_likelihood += 0.2
            
            return {
                'success': True,
                'demo': demo,
                'follow_up_actions': self._get_demo_follow_up_actions(demo_type)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء العرض التوضيحي: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء العرض التوضيحي'
            }
    
    def get_feature_comparison(self, session_id: str, user_type: str) -> Dict:
        """
        الحصول على مقارنة الميزات
        
        Args:
            session_id: معرف الجلسة
            user_type: نوع المستخدم
            
        Returns:
            Dict: مقارنة الميزات
        """
        try:
            if session_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': 'الجلسة غير موجودة'
                }
            
            session = self.active_sessions[session_id]
            session.user_type_interest = user_type
            
            # إنشاء مقارنة الميزات
            comparison = self._create_feature_comparison(user_type)
            
            # اقتراحات مخصصة
            personalized_suggestions = self._get_personalized_suggestions(user_type, session)
            
            return {
                'success': True,
                'user_type': user_type,
                'feature_comparison': comparison,
                'personalized_suggestions': personalized_suggestions,
                'next_steps': self._get_next_steps(user_type)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في مقارنة الميزات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في مقارنة الميزات'
            }
    
    def provide_registration_guidance(self, session_id: str, user_type: str) -> Dict:
        """
        تقديم إرشادات التسجيل
        
        Args:
            session_id: معرف الجلسة
            user_type: نوع المستخدم
            
        Returns:
            Dict: إرشادات التسجيل
        """
        try:
            if session_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': 'الجلسة غير موجودة'
                }
            
            session = self.active_sessions[session_id]
            
            # إنشاء دليل التسجيل المخصص
            registration_guide = self._create_registration_guide(user_type)
            
            # متطلبات التسجيل
            requirements = self._get_registration_requirements(user_type)
            
            # تحديث احتمالية التحويل
            session.conversion_likelihood += 0.3
            
            return {
                'success': True,
                'user_type': user_type,
                'registration_guide': registration_guide,
                'requirements': requirements,
                'estimated_time': self._get_registration_time_estimate(user_type),
                'support_available': True
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرشادات التسجيل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إرشادات التسجيل'
            }
    
    def end_session(self, session_id: str, feedback: Optional[Dict] = None) -> Dict:
        """
        إنهاء الجلسة
        
        Args:
            session_id: معرف الجلسة
            feedback: تقييم المستخدم
            
        Returns:
            Dict: ملخص الجلسة
        """
        try:
            if session_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': 'الجلسة غير موجودة'
                }
            
            session = self.active_sessions[session_id]
            
            # تحديث التقييم
            if feedback:
                session.satisfaction_score = feedback.get('satisfaction_score')
            
            # إنشاء ملخص الجلسة
            session_summary = self._create_session_summary(session)
            
            # حفظ التحليلات
            self._save_session_analytics(session)
            
            # إزالة الجلسة من الذاكرة
            del self.active_sessions[session_id]
            
            return {
                'success': True,
                'session_summary': session_summary,
                'thank_you_message': 'شكراً لك على وقتك! نتطلع لرؤيتك قريباً في منصة صحتك في أمان 🌟',
                'follow_up_actions': self._get_follow_up_actions(session)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنهاء الجلسة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنهاء الجلسة'
            }
    
    def get_analytics_summary(self) -> Dict:
        """
        الحصول على ملخص التحليلات
        
        Returns:
            Dict: ملخص التحليلات
        """
        try:
            # إحصائيات عامة
            total_sessions = len(self.session_analytics)
            active_sessions = len(self.active_sessions)
            
            # تحليل أنواع المستخدمين
            user_type_interest = {}
            conversion_rates = {}
            satisfaction_scores = []
            
            for session_data in self.session_analytics.values():
                if session_data.get('user_type_interest'):
                    user_type = session_data['user_type_interest']
                    user_type_interest[user_type] = user_type_interest.get(user_type, 0) + 1
                
                if session_data.get('converted'):
                    user_type = session_data.get('user_type_interest', 'unknown')
                    if user_type not in conversion_rates:
                        conversion_rates[user_type] = {'converted': 0, 'total': 0}
                    conversion_rates[user_type]['converted'] += 1
                
                if session_data.get('satisfaction_score'):
                    satisfaction_scores.append(session_data['satisfaction_score'])
            
            # حساب معدلات التحويل
            for user_type in user_type_interest:
                if user_type not in conversion_rates:
                    conversion_rates[user_type] = {'converted': 0, 'total': 0}
                conversion_rates[user_type]['total'] = user_type_interest[user_type]
            
            # حساب متوسط الرضا
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
            
            return {
                'success': True,
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'user_type_interest': user_type_interest,
                'conversion_rates': conversion_rates,
                'average_satisfaction': round(avg_satisfaction, 2),
                'most_requested_features': self._get_most_requested_features(),
                'common_questions': self._get_common_questions_stats()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في التحليلات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في التحليلات'
            }
    
    # الدوال المساعدة
    def _generate_welcome_message(self, session: PreRegistrationSession) -> str:
        """إنتاج رسالة ترحيب مخصصة"""
        greetings = self.conversation_patterns['greetings']
        base_greeting = random.choice(greetings)
        
        # تخصيص حسب الوقت
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            time_greeting = "صباح الخير! "
        elif 12 <= current_hour < 17:
            time_greeting = "مساء الخير! "
        elif 17 <= current_hour < 21:
            time_greeting = "مساء الخير! "
        else:
            time_greeting = "مساء الخير! "
        
        # تخصيص حسب مصدر الإحالة
        referral_message = ""
        if session.referral_source:
            referral_message = f" أرى أنك وصلت إلينا من {session.referral_source}، "
        
        return f"{time_greeting}{base_greeting}{referral_message} كيف يمكنني مساعدتك في اكتشاف منصتنا الطبية المتطورة؟"
    
    def _get_initial_suggestions(self, session: PreRegistrationSession) -> List[str]:
        """الحصول على اقتراحات البداية"""
        suggestions = [
            "أريد معرفة المزيد عن الميزات",
            "كيف يمكنني التسجيل؟",
            "أريد مشاهدة عرض توضيحي",
            "ما هي تكلفة الاستخدام؟",
            "هل النظام آمن؟"
        ]
        
        # تخصيص حسب نوع الجهاز
        if session.device_type == 'mobile':
            suggestions.insert(1, "هل يعمل على الهاتف؟")
        
        return suggestions[:5]
    
    def _get_quick_actions(self) -> List[Dict]:
        """الحصول على الإجراءات السريعة"""
        return [
            {
                'title': 'جولة سريعة',
                'description': 'استكشف الميزات في 3 دقائق',
                'action': 'start_tour',
                'icon': '🚀'
            },
            {
                'title': 'عرض توضيحي',
                'description': 'شاهد النظام في العمل',
                'action': 'request_demo',
                'icon': '🎥'
            },
            {
                'title': 'مقارنة الميزات',
                'description': 'قارن بين الخطط المختلفة',
                'action': 'compare_features',
                'icon': '📊'
            },
            {
                'title': 'تحدث مع خبير',
                'description': 'احصل على استشارة مجانية',
                'action': 'contact_expert',
                'icon': '👨‍⚕️'
            }
        ]
    
    def _analyze_message_intent(self, message: str, session: PreRegistrationSession) -> Dict:
        """تحليل نية الرسالة"""
        message_lower = message.lower()
        
        # تحليل الكلمات المفتاحية
        intents = {
            'greeting': ['مرحبا', 'أهلا', 'السلام', 'صباح', 'مساء'],
            'feature_inquiry': ['ميزات', 'خصائص', 'إمكانيات', 'وظائف', 'خدمات'],
            'demo_request': ['عرض', 'تجربة', 'مشاهدة', 'ديمو', 'تطبيق'],
            'pricing_inquiry': ['سعر', 'تكلفة', 'مجاني', 'اشتراك', 'خطة'],
            'security_inquiry': ['أمان', 'حماية', 'خصوصية', 'تشفير', 'آمن'],
            'registration_inquiry': ['تسجيل', 'حساب', 'اشتراك', 'انضمام'],
            'technical_inquiry': ['تقني', 'نظام', 'متطلبات', 'متوافق', 'يعمل'],
            'comparison_request': ['مقارنة', 'فرق', 'أفضل', 'اختيار']
        }
        
        detected_intent = 'general_inquiry'
        confidence = 0.5
        
        for intent, keywords in intents.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > 0:
                detected_intent = intent
                confidence = min(0.9, 0.6 + (matches * 0.1))
                break
        
        return {
            'intent': detected_intent,
            'confidence': confidence,
            'keywords_found': [kw for kw in sum(intents.values(), []) if kw in message_lower],
            'message_length': len(message),
            'question_type': 'question' if '؟' in message or message.endswith('?') else 'statement'
        }
    
    def _generate_response(self, intent: Dict, message: str, session: PreRegistrationSession) -> AssistantResponse:
        """إنتاج رد المساعد"""
        intent_type = intent['intent']
        
        # اختيار الرد المناسب
        if intent_type == 'greeting':
            response_text = random.choice([
                "أهلاً وسهلاً! سعيدة بلقائك 😊",
                "مرحباً بك! كيف يمكنني مساعدتك؟",
                "أهلاً! أنا هنا لأساعدك في كل ما تحتاجه"
            ])
            
        elif intent_type == 'feature_inquiry':
            response_text = "رائع! لدينا ميزات مذهلة ستغير طريقة تعاملك مع الرعاية الصحية. أي نوع من الميزات يهمك أكثر؟"
            
        elif intent_type == 'demo_request':
            response_text = "ممتاز! العروض التوضيحية هي أفضل طريقة لفهم قوة منصتنا. أي نوع من العروض تفضل؟"
            
        elif intent_type == 'pricing_inquiry':
            response_text = self.knowledge_base['common_questions']['كم تكلفة الاستخدام؟']['answer']
            
        elif intent_type == 'security_inquiry':
            response_text = self.knowledge_base['common_questions']['هل النظام آمن؟']['answer']
            
        elif intent_type == 'registration_inquiry':
            response_text = self.knowledge_base['common_questions']['كيف أبدأ الاستخدام؟']['answer']
            
        else:
            response_text = "شكراً لسؤالك! دعني أساعدك في العثور على المعلومات التي تحتاجها."
        
        # إنشاء اقتراحات المتابعة
        suggested_actions = self._get_suggested_actions(intent_type, session)
        quick_replies = self._get_quick_replies(intent_type)
        follow_up_questions = self._get_follow_up_questions(intent_type)
        
        return AssistantResponse(
            response_id=str(uuid.uuid4()),
            message=response_text,
            response_type=intent_type,
            suggested_actions=suggested_actions,
            quick_replies=quick_replies,
            multimedia_content=None,
            follow_up_questions=follow_up_questions,
            confidence_score=intent['confidence']
        )
    
    def _get_suggested_actions(self, intent_type: str, session: PreRegistrationSession) -> List[Dict]:
        """الحصول على الإجراءات المقترحة"""
        actions = []
        
        if intent_type == 'feature_inquiry':
            actions = [
                {'title': 'استكشف ميزات المرضى', 'action': 'explore_patient_features'},
                {'title': 'استكشف ميزات الأطباء', 'action': 'explore_doctor_features'},
                {'title': 'شاهد عرض توضيحي', 'action': 'request_demo'}
            ]
        
        elif intent_type == 'demo_request':
            actions = [
                {'title': 'رحلة المريض', 'action': 'demo_patient_journey'},
                {'title': 'سير عمل الطبيب', 'action': 'demo_doctor_workflow'},
                {'title': 'الاستجابة للطوارئ', 'action': 'demo_emergency_response'}
            ]
        
        elif intent_type == 'registration_inquiry':
            actions = [
                {'title': 'دليل التسجيل للمرضى', 'action': 'registration_guide_patient'},
                {'title': 'دليل التسجيل للأطباء', 'action': 'registration_guide_doctor'},
                {'title': 'دليل التسجيل للمستشفيات', 'action': 'registration_guide_hospital'}
            ]
        
        return actions
    
    def _get_quick_replies(self, intent_type: str) -> List[str]:
        """الحصول على الردود السريعة"""
        quick_replies = {
            'feature_inquiry': ['أريد معرفة المزيد', 'شاهد عرض توضيحي', 'كيف أبدأ؟'],
            'demo_request': ['رحلة المريض', 'سير عمل الطبيب', 'الطوارئ'],
            'pricing_inquiry': ['الخطة المجانية', 'الخطط المدفوعة', 'خصومات المؤسسات'],
            'registration_inquiry': ['مريض', 'طبيب', 'مستشفى']
        }
        
        return quick_replies.get(intent_type, ['نعم', 'لا', 'أريد معرفة المزيد'])
    
    def _get_follow_up_questions(self, intent_type: str) -> List[str]:
        """الحصول على أسئلة المتابعة"""
        follow_ups = {
            'feature_inquiry': [
                'أي نوع من المستخدمين أنت؟',
                'ما هي أهم احتياجاتك الطبية؟',
                'هل تفضل الاستشارات الحضورية أم عن بُعد؟'
            ],
            'demo_request': [
                'أي سيناريو يهمك أكثر؟',
                'هل تريد تجربة تفاعلية؟',
                'كم من الوقت لديك للعرض؟'
            ],
            'registration_inquiry': [
                'ما نوع الحساب الذي تريد إنشاؤه؟',
                'هل لديك أي أسئلة عن عملية التسجيل؟',
                'هل تحتاج مساعدة في التحضير للتسجيل؟'
            ]
        }
        
        return follow_ups.get(intent_type, [])
    
    def _update_session_context(self, session: PreRegistrationSession, intent: Dict, message: str):
        """تحديث سياق الجلسة"""
        intent_type = intent['intent']
        
        # تحديث الميزات المستكشفة
        if intent_type == 'feature_inquiry':
            if 'feature_exploration' not in session.features_explored:
                session.features_explored.append('feature_exploration')
        
        # تحديث الأسئلة المطروحة
        if intent['question_type'] == 'question':
            session.questions_asked.append(intent_type)
        
        # تحديث نوع المستخدم المهتم
        message_lower = message.lower()
        if any(word in message_lower for word in ['مريض', 'علاج', 'دواء']):
            session.user_type_interest = UserType.PATIENT.value
        elif any(word in message_lower for word in ['طبيب', 'تشخيص', 'عيادة']):
            session.user_type_interest = UserType.DOCTOR.value
        elif any(word in message_lower for word in ['مستشفى', 'إدارة', 'نظام']):
            session.user_type_interest = UserType.HOSPITAL.value
    
    def _calculate_conversion_likelihood(self, session: PreRegistrationSession) -> float:
        """حساب احتمالية التحويل"""
        score = 0.5  # نقطة البداية
        
        # عوامل إيجابية
        if session.user_type_interest:
            score += 0.2
        
        if session.demo_requests:
            score += 0.3
        
        if len(session.features_explored) > 2:
            score += 0.2
        
        if session.interaction_count > 5:
            score += 0.1
        
        # عوامل سلبية
        if session.interaction_count > 20:
            score -= 0.1  # قد يكون مترددًا
        
        return min(1.0, max(0.0, score))
    
    def _get_session_summary(self, session: PreRegistrationSession) -> Dict:
        """الحصول على ملخص الجلسة"""
        duration = (datetime.now() - session.start_time).total_seconds() / 60
        
        return {
            'session_duration_minutes': round(duration, 1),
            'interaction_count': session.interaction_count,
            'user_type_interest': session.user_type_interest,
            'features_explored': len(session.features_explored),
            'demo_requests': len(session.demo_requests),
            'conversion_likelihood': session.conversion_likelihood
        }
    
    def _create_interactive_demo(self, demo_type: str, session: PreRegistrationSession) -> FeatureDemo:
        """إنشاء عرض توضيحي تفاعلي"""
        demo_data = self.knowledge_base['demo_scenarios'].get(demo_type, {})
        
        return FeatureDemo(
            feature_name=demo_data.get('title', demo_type),
            demo_type='interactive',
            description=demo_data.get('description', ''),
            interactive_elements=self._create_demo_elements(demo_type),
            sample_data=self._get_demo_sample_data(demo_type),
            benefits=self._get_demo_benefits(demo_type),
            user_testimonials=self._get_demo_testimonials(demo_type)
        )
    
    def _create_demo_elements(self, demo_type: str) -> List[Dict]:
        """إنشاء عناصر العرض التوضيحي التفاعلية"""
        elements = []
        
        if demo_type == 'patient_journey':
            elements = [
                {'type': 'form', 'title': 'إنشاء الملف الطبي', 'interactive': True},
                {'type': 'search', 'title': 'البحث عن طبيب', 'interactive': True},
                {'type': 'calendar', 'title': 'حجز موعد', 'interactive': True},
                {'type': 'video_call', 'title': 'الاستشارة الطبية', 'interactive': False},
                {'type': 'prescription', 'title': 'الحصول على الوصفة', 'interactive': True}
            ]
        
        elif demo_type == 'doctor_workflow':
            elements = [
                {'type': 'dashboard', 'title': 'لوحة التحكم', 'interactive': True},
                {'type': 'patient_list', 'title': 'قائمة المرضى', 'interactive': True},
                {'type': 'medical_record', 'title': 'الملف الطبي', 'interactive': True},
                {'type': 'diagnosis_tool', 'title': 'أداة التشخيص', 'interactive': True},
                {'type': 'prescription_writer', 'title': 'كتابة الوصفة', 'interactive': True}
            ]
        
        return elements
    
    def _get_demo_sample_data(self, demo_type: str) -> Dict:
        """الحصول على بيانات العينة للعرض التوضيحي"""
        sample_data = {
            'patient_journey': {
                'patient_name': 'أحمد محمد',
                'age': 35,
                'condition': 'ارتفاع ضغط الدم',
                'doctor_name': 'د. سارة أحمد',
                'appointment_time': '2024-02-15 10:00'
            },
            'doctor_workflow': {
                'doctor_name': 'د. محمد علي',
                'specialty': 'طب الباطنة',
                'patients_today': 12,
                'next_appointment': '09:30'
            }
        }
        
        return sample_data.get(demo_type, {})
    
    def _get_demo_benefits(self, demo_type: str) -> List[str]:
        """الحصول على فوائد العرض التوضيحي"""
        benefits = {
            'patient_journey': [
                'توفير الوقت والجهد',
                'رعاية طبية أفضل',
                'سهولة الوصول للأطباء',
                'متابعة مستمرة للحالة'
            ],
            'doctor_workflow': [
                'تحسين كفاءة العمل',
                'تقليل الأخطاء الطبية',
                'وصول سريع للمعلومات',
                'تحسين التواصل مع المرضى'
            ]
        }
        
        return benefits.get(demo_type, [])
    
    def _get_demo_testimonials(self, demo_type: str) -> List[str]:
        """الحصول على شهادات المستخدمين"""
        testimonials = [
            '"النظام غير حياتي! أصبح بإمكاني الحصول على الرعاية الطبية بسهولة" - مريم أحمد',
            '"كطبيب، هذا النظام وفر علي ساعات من العمل الإداري" - د. خالد محمد',
            '"مستشفانا أصبح أكثر كفاءة بنسبة 40% بعد استخدام النظام" - إدارة مستشفى النور'
        ]
        
        return testimonials
    
    def _get_demo_follow_up_actions(self, demo_type: str) -> List[Dict]:
        """الحصول على إجراءات المتابعة بعد العرض التوضيحي"""
        return [
            {'title': 'جرب بنفسك', 'action': 'start_trial'},
            {'title': 'تحدث مع خبير', 'action': 'contact_expert'},
            {'title': 'احصل على عرض سعر', 'action': 'get_quote'},
            {'title': 'ابدأ التسجيل', 'action': 'start_registration'}
        ]
    
    def _create_feature_comparison(self, user_type: str) -> Dict:
        """إنشاء مقارنة الميزات"""
        features = self.knowledge_base['features_by_user_type'].get(user_type, {})
        
        return {
            'user_type': user_type,
            'core_features': features.get('core_features', []),
            'advanced_features': features.get('advanced_features', []),
            'unique_benefits': features.get('unique_benefits', []),
            'comparison_matrix': self._create_comparison_matrix(user_type)
        }
    
    def _create_comparison_matrix(self, user_type: str) -> List[Dict]:
        """إنشاء مصفوفة المقارنة"""
        # مقارنة بين الخطط المختلفة
        return [
            {
                'feature': 'الميزات الأساسية',
                'free': True,
                'premium': True,
                'enterprise': True
            },
            {
                'feature': 'الذكاء الاصطناعي',
                'free': False,
                'premium': True,
                'enterprise': True
            },
            {
                'feature': 'التحليلات المتقدمة',
                'free': False,
                'premium': False,
                'enterprise': True
            }
        ]
    
    def _get_personalized_suggestions(self, user_type: str, session: PreRegistrationSession) -> List[str]:
        """الحصول على اقتراحات مخصصة"""
        suggestions = []
        
        if user_type == UserType.PATIENT.value:
            suggestions = [
                'ابدأ بإنشاء ملفك الطبي الرقمي',
                'جرب المساعد الصوتي الذكي',
                'استكشف ميزة تحليل الأعراض',
                'تعرف على نظام تذكيرات الأدوية'
            ]
        
        elif user_type == UserType.DOCTOR.value:
            suggestions = [
                'استكشف أدوات التشخيص المساعدة',
                'جرب نظام إدارة المرضى',
                'تعرف على ميزات التطبيب عن بُعد',
                'استكشف تحليلات الأداء'
            ]
        
        # تخصيص حسب الجهاز
        if session.device_type == 'mobile':
            suggestions.append('جرب التطبيق على هاتفك')
        
        return suggestions
    
    def _get_next_steps(self, user_type: str) -> List[Dict]:
        """الحصول على الخطوات التالية"""
        return [
            {'step': 1, 'title': 'إنشاء حساب مجاني', 'estimated_time': '2 دقيقة'},
            {'step': 2, 'title': 'إكمال الملف الشخصي', 'estimated_time': '5 دقائق'},
            {'step': 3, 'title': 'استكشاف الميزات', 'estimated_time': '10 دقائق'},
            {'step': 4, 'title': 'بدء الاستخدام الفعلي', 'estimated_time': 'فوري'}
        ]
    
    def _create_registration_guide(self, user_type: str) -> Dict:
        """إنشاء دليل التسجيل"""
        guides = {
            UserType.PATIENT.value: {
                'title': 'دليل التسجيل للمرضى',
                'steps': [
                    'اختر "تسجيل مريض جديد"',
                    'أدخل المعلومات الشخصية',
                    'أضف المعلومات الطبية الأساسية',
                    'فعل الحساب عبر البريد الإلكتروني',
                    'ابدأ استخدام النظام'
                ],
                'tips': [
                    'تأكد من صحة البريد الإلكتروني',
                    'استخدم كلمة مرور قوية',
                    'أضف رقم هاتف للطوارئ'
                ]
            },
            UserType.DOCTOR.value: {
                'title': 'دليل التسجيل للأطباء',
                'steps': [
                    'اختر "تسجيل طبيب جديد"',
                    'أدخل المعلومات الشخصية والمهنية',
                    'ارفع المستندات المطلوبة',
                    'انتظر التحقق من البيانات',
                    'فعل الحساب وابدأ الاستخدام'
                ],
                'tips': [
                    'تأكد من صحة رقم الترخيص',
                    'ارفع صور واضحة للمستندات',
                    'التحقق يستغرق 24-48 ساعة'
                ]
            }
        }
        
        return guides.get(user_type, {})
    
    def _get_registration_requirements(self, user_type: str) -> List[str]:
        """الحصول على متطلبات التسجيل"""
        requirements = {
            UserType.PATIENT.value: [
                'بطاقة هوية سارية',
                'بريد إلكتروني صحيح',
                'رقم هاتف للتواصل'
            ],
            UserType.DOCTOR.value: [
                'بطاقة هوية سارية',
                'ترخيص مزاولة المهنة',
                'شهادة التخرج',
                'بريد إلكتروني مهني',
                'رقم هاتف للتواصل'
            ],
            UserType.HOSPITAL.value: [
                'ترخيص المنشأة الطبية',
                'السجل التجاري',
                'بيانات المسؤول المفوض',
                'بريد إلكتروني رسمي'
            ]
        }
        
        return requirements.get(user_type, [])
    
    def _get_registration_time_estimate(self, user_type: str) -> str:
        """تقدير وقت التسجيل"""
        estimates = {
            UserType.PATIENT.value: '2-3 دقائق',
            UserType.DOCTOR.value: '5-10 دقائق + 24-48 ساعة للتحقق',
            UserType.HOSPITAL.value: '10-15 دقيقة + 2-3 أيام للتحقق'
        }
        
        return estimates.get(user_type, '5 دقائق')
    
    def _create_session_summary(self, session: PreRegistrationSession) -> Dict:
        """إنشاء ملخص الجلسة"""
        duration = (datetime.now() - session.start_time).total_seconds() / 60
        
        return {
            'session_id': session.session_id,
            'duration_minutes': round(duration, 1),
            'interactions': session.interaction_count,
            'user_type_interest': session.user_type_interest,
            'features_explored': session.features_explored,
            'demo_requests': session.demo_requests,
            'questions_asked': len(session.questions_asked),
            'conversion_likelihood': session.conversion_likelihood,
            'satisfaction_score': session.satisfaction_score
        }
    
    def _save_session_analytics(self, session: PreRegistrationSession):
        """حفظ تحليلات الجلسة"""
        session_data = {
            'session_id': session.session_id,
            'visitor_id': session.visitor_id,
            'start_time': session.start_time.isoformat(),
            'duration_minutes': (datetime.now() - session.start_time).total_seconds() / 60,
            'interaction_count': session.interaction_count,
            'user_type_interest': session.user_type_interest,
            'features_explored': session.features_explored,
            'demo_requests': session.demo_requests,
            'questions_asked': session.questions_asked,
            'conversion_likelihood': session.conversion_likelihood,
            'satisfaction_score': session.satisfaction_score,
            'device_type': session.device_type,
            'location': session.location,
            'referral_source': session.referral_source,
            'converted': session.conversion_likelihood > 0.7  # تحديد التحويل
        }
        
        self.session_analytics[session.session_id] = session_data
    
    def _get_follow_up_actions(self, session: PreRegistrationSession) -> List[Dict]:
        """الحصول على إجراءات المتابعة"""
        actions = []
        
        if session.conversion_likelihood > 0.7:
            actions.append({
                'title': 'ابدأ التسجيل الآن',
                'action': 'start_registration',
                'priority': 'high'
            })
        
        if session.user_type_interest:
            actions.append({
                'title': f'دليل التسجيل لـ{session.user_type_interest}',
                'action': 'get_registration_guide',
                'priority': 'medium'
            })
        
        actions.extend([
            {
                'title': 'احصل على استشارة مجانية',
                'action': 'book_consultation',
                'priority': 'medium'
            },
            {
                'title': 'اشترك في النشرة الإخبارية',
                'action': 'subscribe_newsletter',
                'priority': 'low'
            }
        ])
        
        return actions
    
    def _get_most_requested_features(self) -> List[Dict]:
        """الحصول على الميزات الأكثر طلباً"""
        # في التطبيق الحقيقي، سيتم حساب هذا من البيانات الفعلية
        return [
            {'feature': 'الذكاء الاصطناعي للتشخيص', 'requests': 85},
            {'feature': 'التطبيب عن بُعد', 'requests': 72},
            {'feature': 'إدارة الأدوية', 'requests': 68},
            {'feature': 'الملف الطبي الرقمي', 'requests': 65}
        ]
    
    def _get_common_questions_stats(self) -> List[Dict]:
        """الحصول على إحصائيات الأسئلة الشائعة"""
        return [
            {'question': 'هل النظام آمن؟', 'frequency': 45},
            {'question': 'كم تكلفة الاستخدام؟', 'frequency': 38},
            {'question': 'كيف أبدأ الاستخدام؟', 'frequency': 32},
            {'question': 'هل يدعم اللغة العربية؟', 'frequency': 28}
        ]

