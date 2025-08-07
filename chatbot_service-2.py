"""
خدمة روبوت المحادثة الذكي للدعم الطبي
"""

import os
import json
import uuid
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum
import openai
import threading
import time

class ConversationState(Enum):
    GREETING = "ترحيب"
    SYMPTOM_ASSESSMENT = "تقييم الأعراض"
    APPOINTMENT_BOOKING = "حجز موعد"
    MEDICATION_INQUIRY = "استفسار دوائي"
    EMERGENCY_ASSESSMENT = "تقييم طوارئ"
    GENERAL_INQUIRY = "استفسار عام"
    HEALTH_EDUCATION = "تثقيف صحي"
    FEEDBACK_COLLECTION = "جمع التقييمات"

class MessageType(Enum):
    TEXT = "نص"
    VOICE = "صوت"
    IMAGE = "صورة"
    QUICK_REPLY = "رد سريع"
    CARD = "بطاقة"
    CAROUSEL = "عرض متعدد"

class UrgencyLevel(Enum):
    LOW = "منخفض"
    MEDIUM = "متوسط"
    HIGH = "عالي"
    CRITICAL = "حرج"

@dataclass
class ChatMessage:
    message_id: str
    conversation_id: str
    user_id: str
    message_type: str
    content: str
    intent: Optional[str]
    entities: Dict
    confidence: float
    urgency_level: str
    response_generated: bool
    timestamp: datetime

@dataclass
class ConversationContext:
    conversation_id: str
    user_id: str
    current_state: str
    collected_data: Dict
    last_activity: datetime
    session_duration: int
    message_count: int
    user_satisfaction: Optional[float]

@dataclass
class HealthIntent:
    intent_name: str
    patterns: List[str]
    responses: List[str]
    required_entities: List[str]
    follow_up_questions: List[str]
    urgency_indicators: List[str]

class ChatbotService:
    def __init__(self):
        """تهيئة خدمة روبوت المحادثة"""
        
        # إعدادات الروبوت
        self.chatbot_settings = {
            'max_conversation_duration_hours': 24,
            'max_messages_per_session': 100,
            'response_timeout_seconds': 30,
            'confidence_threshold': 0.7,
            'emergency_keywords_threshold': 0.9,
            'supported_languages': ['ar', 'en'],
            'max_message_length': 1000,
            'session_timeout_minutes': 30
        }
        
        # قاعدة المعرفة الطبية
        self.medical_knowledge_base = {
            'symptoms': {
                'حمى': {
                    'description': 'ارتفاع في درجة حرارة الجسم',
                    'common_causes': ['عدوى فيروسية', 'عدوى بكتيرية', 'التهاب'],
                    'urgency_indicators': ['درجة حرارة أعلى من 39', 'صعوبة في التنفس', 'فقدان الوعي'],
                    'first_aid': ['شرب السوائل', 'الراحة', 'خافض حرارة'],
                    'when_to_seek_help': 'إذا استمرت أكثر من 3 أيام أو تجاوزت 39 درجة'
                },
                'صداع': {
                    'description': 'ألم في الرأس أو الرقبة',
                    'common_causes': ['التوتر', 'الجفاف', 'قلة النوم', 'الصداع النصفي'],
                    'urgency_indicators': ['صداع مفاجئ شديد', 'مع حمى وتصلب الرقبة', 'مع تغيرات في الرؤية'],
                    'first_aid': ['الراحة في مكان هادئ', 'شرب الماء', 'مسكن ألم خفيف'],
                    'when_to_seek_help': 'إذا كان مفاجئاً وشديداً أو مصحوباً بأعراض أخرى'
                },
                'ألم في الصدر': {
                    'description': 'ألم أو ضغط في منطقة الصدر',
                    'common_causes': ['مشاكل القلب', 'مشاكل الرئة', 'مشاكل العضلات', 'القلق'],
                    'urgency_indicators': ['ألم شديد مع ضيق تنفس', 'ألم ينتشر للذراع', 'تعرق شديد'],
                    'first_aid': ['الجلوس والراحة', 'تجنب المجهود', 'طلب المساعدة فوراً'],
                    'when_to_seek_help': 'فوراً - اتصل بالطوارئ'
                }
            },
            'medications': {
                'باراسيتامول': {
                    'uses': ['خافض حرارة', 'مسكن ألم'],
                    'dosage': '500-1000 مجم كل 6-8 ساعات',
                    'max_daily': '4000 مجم',
                    'warnings': ['لا تتجاوز الجرعة المحددة', 'احذر مع أمراض الكبد'],
                    'side_effects': ['نادرة عند الاستخدام الصحيح']
                },
                'إيبوبروفين': {
                    'uses': ['مسكن ألم', 'مضاد التهاب', 'خافض حرارة'],
                    'dosage': '200-400 مجم كل 6-8 ساعات',
                    'max_daily': '1200 مجم',
                    'warnings': ['تناول مع الطعام', 'احذر مع أمراض الكلى والقلب'],
                    'side_effects': ['اضطراب المعدة', 'دوخة']
                }
            },
            'emergency_conditions': {
                'نوبة قلبية': {
                    'symptoms': ['ألم شديد في الصدر', 'ضيق تنفس', 'تعرق', 'غثيان'],
                    'immediate_action': 'اتصل بالطوارئ فوراً - 123',
                    'first_aid': ['أجلس المريض', 'فك الملابس الضيقة', 'أعط أسبرين إذا متوفر']
                },
                'سكتة دماغية': {
                    'symptoms': ['ضعف مفاجئ في الوجه أو الذراع', 'صعوبة في الكلام', 'دوخة شديدة'],
                    'immediate_action': 'اتصل بالطوارئ فوراً - 123',
                    'first_aid': ['لا تعط أي دواء', 'ضع المريض في وضع آمن', 'راقب التنفس']
                }
            }
        }
        
        # أنماط التعرف على النوايا
        self.intent_patterns = {
            'symptom_inquiry': [
                r'أشعر بـ?(.+)',
                r'عندي (.+)',
                r'أعاني من (.+)',
                r'لدي ألم في (.+)',
                r'أحس بـ?(.+)'
            ],
            'medication_inquiry': [
                r'ما هو دواء (.+)',
                r'معلومات عن (.+)',
                r'جرعة (.+)',
                r'أعراض جانبية (.+)',
                r'هل يمكنني تناول (.+)'
            ],
            'appointment_booking': [
                r'أريد حجز موعد',
                r'موعد مع (.+)',
                r'متى يمكنني زيارة',
                r'حجز مع طبيب',
                r'أحتاج موعد'
            ],
            'emergency': [
                r'طوارئ',
                r'مساعدة عاجلة',
                r'ألم شديد',
                r'لا أستطيع التنفس',
                r'فقدت الوعي',
                r'نزيف شديد'
            ],
            'general_health': [
                r'نصائح صحية',
                r'كيف أحافظ على صحتي',
                r'تمارين رياضية',
                r'نظام غذائي',
                r'الوقاية من (.+)'
            ]
        }
        
        # ردود سريعة مقترحة
        self.quick_replies = {
            'greeting': [
                'أعراض مرضية',
                'حجز موعد',
                'استفسار دوائي',
                'نصائح صحية',
                'طوارئ'
            ],
            'symptom_assessment': [
                'نعم',
                'لا',
                'أحياناً',
                'لست متأكد',
                'أريد التحدث مع طبيب'
            ],
            'appointment_booking': [
                'طبيب عام',
                'طبيب أسنان',
                'طبيب عيون',
                'طبيب نساء',
                'طبيب أطفال'
            ]
        }
        
        # قوالب الردود
        self.response_templates = {
            'greeting': [
                'مرحباً! أنا مساعدك الصحي الذكي. كيف يمكنني مساعدتك اليوم؟',
                'أهلاً وسهلاً! أنا هنا لمساعدتك في أي استفسار صحي. ما الذي تحتاج إليه؟',
                'مرحباً بك في صحتك في أمان! كيف يمكنني خدمتك؟'
            ],
            'symptom_acknowledgment': [
                'أفهم أنك تشعر بـ {symptom}. دعني أساعدك في تقييم الحالة.',
                'شكراً لإخباري عن {symptom}. سأطرح عليك بعض الأسئلة لفهم الحالة بشكل أفضل.',
                'أقدر ثقتك في إخباري عن {symptom}. دعنا نتحدث عن التفاصيل.'
            ],
            'emergency_response': [
                '🚨 هذا يبدو كحالة طوارئ! يرجى الاتصال بالطوارئ فوراً على 123',
                '⚠️ أنصحك بشدة بطلب المساعدة الطبية العاجلة. اتصل بـ 123',
                '🆘 هذه أعراض تتطلب تدخلاً طبياً فورياً. لا تتأخر في طلب المساعدة!'
            ],
            'medication_info': [
                'إليك معلومات عن {medication}:',
                'بخصوص {medication}، إليك ما تحتاج معرفته:',
                'معلومات مهمة عن {medication}:'
            ],
            'appointment_confirmation': [
                'تم حجز موعدك بنجاح! ستصلك رسالة تأكيد قريباً.',
                'ممتاز! تم تسجيل طلب الموعد. سنتواصل معك لتأكيد التفاصيل.',
                'شكراً! تم إرسال طلب الموعد للطبيب المختص.'
            ]
        }
        
        # قاعدة بيانات المحادثات (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.conversations = {}
        self.user_contexts = {}
        self.chat_analytics = {}
        
        # تهيئة OpenAI للذكاء الاصطناعي
        self.openai_client = openai.OpenAI()
        
        # خيوط معالجة الرسائل
        self.message_queue = []
        self.processing_thread = None
        self._start_message_processor()
    
    def start_conversation(self, user_id: str, initial_message: str = None) -> Dict:
        """
        بدء محادثة جديدة
        
        Args:
            user_id: معرف المستخدم
            initial_message: الرسالة الأولى (اختيارية)
            
        Returns:
            Dict: معلومات المحادثة الجديدة
        """
        try:
            conversation_id = str(uuid.uuid4())
            
            # إنشاء سياق المحادثة
            context = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id,
                current_state=ConversationState.GREETING.value,
                collected_data={},
                last_activity=datetime.now(),
                session_duration=0,
                message_count=0,
                user_satisfaction=None
            )
            
            self.user_contexts[user_id] = context
            self.conversations[conversation_id] = []
            
            # رسالة ترحيب
            greeting_response = self._generate_greeting_response(user_id)
            
            # إضافة رسالة الروبوت
            bot_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                user_id='chatbot',
                message_type=MessageType.TEXT.value,
                content=greeting_response['message'],
                intent='greeting',
                entities={},
                confidence=1.0,
                urgency_level=UrgencyLevel.LOW.value,
                response_generated=True,
                timestamp=datetime.now()
            )
            
            self.conversations[conversation_id].append(bot_message)
            
            # معالجة الرسالة الأولى إذا كانت موجودة
            if initial_message:
                user_response = self.process_message(user_id, initial_message)
                return {
                    'success': True,
                    'conversation_id': conversation_id,
                    'greeting': greeting_response,
                    'initial_response': user_response
                }
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'greeting': greeting_response,
                'quick_replies': self.quick_replies['greeting']
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في بدء المحادثة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في بدء المحادثة'
            }
    
    def process_message(self, user_id: str, message: str, message_type: str = 'text') -> Dict:
        """
        معالجة رسالة من المستخدم
        
        Args:
            user_id: معرف المستخدم
            message: نص الرسالة
            message_type: نوع الرسالة
            
        Returns:
            Dict: رد الروبوت
        """
        try:
            # التحقق من وجود سياق المحادثة
            if user_id not in self.user_contexts:
                return self.start_conversation(user_id, message)
            
            context = self.user_contexts[user_id]
            conversation_id = context.conversation_id
            
            # التحقق من انتهاء صلاحية الجلسة
            if self._is_session_expired(context):
                return self.start_conversation(user_id, message)
            
            # تحليل الرسالة
            analysis_result = self._analyze_message(message, context)
            
            # إنشاء رسالة المستخدم
            user_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                user_id=user_id,
                message_type=message_type,
                content=message,
                intent=analysis_result['intent'],
                entities=analysis_result['entities'],
                confidence=analysis_result['confidence'],
                urgency_level=analysis_result['urgency_level'],
                response_generated=False,
                timestamp=datetime.now()
            )
            
            # حفظ رسالة المستخدم
            self.conversations[conversation_id].append(user_message)
            
            # فحص حالات الطوارئ
            if analysis_result['urgency_level'] == UrgencyLevel.CRITICAL.value:
                return self._handle_emergency(user_id, analysis_result)
            
            # إنتاج الرد
            response = self._generate_response(user_id, analysis_result, context)
            
            # إنشاء رسالة الروبوت
            bot_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                user_id='chatbot',
                message_type=response['message_type'],
                content=response['message'],
                intent=analysis_result['intent'],
                entities=analysis_result['entities'],
                confidence=response['confidence'],
                urgency_level=analysis_result['urgency_level'],
                response_generated=True,
                timestamp=datetime.now()
            )
            
            # حفظ رسالة الروبوت
            self.conversations[conversation_id].append(bot_message)
            
            # تحديث السياق
            self._update_context(context, analysis_result, response)
            
            return {
                'success': True,
                'message': response['message'],
                'message_type': response['message_type'],
                'quick_replies': response.get('quick_replies', []),
                'cards': response.get('cards', []),
                'follow_up_questions': response.get('follow_up_questions', []),
                'urgency_level': analysis_result['urgency_level'],
                'confidence': response['confidence'],
                'conversation_state': context.current_state
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في معالجة الرسالة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في معالجة رسالتك. يرجى المحاولة مرة أخرى.'
            }
    
    def get_conversation_history(self, user_id: str, limit: int = 50) -> Dict:
        """
        الحصول على تاريخ المحادثة
        
        Args:
            user_id: معرف المستخدم
            limit: عدد الرسائل المطلوبة
            
        Returns:
            Dict: تاريخ المحادثة
        """
        try:
            if user_id not in self.user_contexts:
                return {
                    'success': False,
                    'error': 'لا توجد محادثة نشطة'
                }
            
            context = self.user_contexts[user_id]
            conversation_id = context.conversation_id
            
            if conversation_id not in self.conversations:
                return {
                    'success': False,
                    'error': 'تاريخ المحادثة غير موجود'
                }
            
            messages = self.conversations[conversation_id]
            
            # ترتيب الرسائل حسب الوقت وأخذ العدد المطلوب
            sorted_messages = sorted(messages, key=lambda x: x.timestamp, reverse=True)[:limit]
            sorted_messages.reverse()  # إعادة الترتيب الزمني الطبيعي
            
            # تحويل الرسائل إلى تنسيق JSON
            formatted_messages = []
            for msg in sorted_messages:
                formatted_messages.append({
                    'message_id': msg.message_id,
                    'sender': 'user' if msg.user_id != 'chatbot' else 'bot',
                    'message_type': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'urgency_level': msg.urgency_level
                })
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'messages': formatted_messages,
                'total_messages': len(messages),
                'conversation_state': context.current_state,
                'session_duration': context.session_duration
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على تاريخ المحادثة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على تاريخ المحادثة'
            }
    
    def end_conversation(self, user_id: str, feedback: Dict = None) -> Dict:
        """
        إنهاء المحادثة
        
        Args:
            user_id: معرف المستخدم
            feedback: تقييم المستخدم (اختياري)
            
        Returns:
            Dict: نتيجة الإنهاء
        """
        try:
            if user_id not in self.user_contexts:
                return {
                    'success': False,
                    'error': 'لا توجد محادثة نشطة'
                }
            
            context = self.user_contexts[user_id]
            
            # حفظ التقييم إذا كان موجوداً
            if feedback:
                context.user_satisfaction = feedback.get('rating', None)
                self._save_feedback(user_id, feedback)
            
            # حفظ إحصائيات المحادثة
            self._save_conversation_analytics(context)
            
            # رسالة وداع
            farewell_message = self._generate_farewell_message(context)
            
            # تنظيف السياق
            del self.user_contexts[user_id]
            
            return {
                'success': True,
                'message': farewell_message,
                'session_summary': {
                    'duration_minutes': context.session_duration,
                    'message_count': context.message_count,
                    'satisfaction_rating': context.user_satisfaction
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنهاء المحادثة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنهاء المحادثة'
            }
    
    def get_health_information(self, topic: str, user_id: str = None) -> Dict:
        """
        الحصول على معلومات صحية حول موضوع معين
        
        Args:
            topic: الموضوع المطلوب
            user_id: معرف المستخدم (اختياري)
            
        Returns:
            Dict: المعلومات الصحية
        """
        try:
            # البحث في قاعدة المعرفة
            topic_lower = topic.lower()
            
            # البحث في الأعراض
            for symptom, info in self.medical_knowledge_base['symptoms'].items():
                if symptom in topic_lower or topic_lower in symptom:
                    return {
                        'success': True,
                        'topic': symptom,
                        'type': 'symptom',
                        'information': info,
                        'disclaimer': 'هذه المعلومات للتثقيف فقط ولا تغني عن استشارة الطبيب'
                    }
            
            # البحث في الأدوية
            for medication, info in self.medical_knowledge_base['medications'].items():
                if medication in topic_lower or topic_lower in medication:
                    return {
                        'success': True,
                        'topic': medication,
                        'type': 'medication',
                        'information': info,
                        'disclaimer': 'استشر الطبيب أو الصيدلي قبل تناول أي دواء'
                    }
            
            # البحث في حالات الطوارئ
            for condition, info in self.medical_knowledge_base['emergency_conditions'].items():
                if condition in topic_lower or topic_lower in condition:
                    return {
                        'success': True,
                        'topic': condition,
                        'type': 'emergency',
                        'information': info,
                        'disclaimer': 'في حالات الطوارئ، اتصل بالطوارئ فوراً'
                    }
            
            # إذا لم يتم العثور على معلومات، استخدم الذكاء الاصطناعي
            ai_response = self._get_ai_health_information(topic)
            
            return {
                'success': True,
                'topic': topic,
                'type': 'general',
                'information': ai_response,
                'disclaimer': 'هذه المعلومات للتثقيف فقط ولا تغني عن استشارة الطبيب المختص'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على المعلومات الصحية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على المعلومات'
            }
    
    def assess_symptoms(self, symptoms: List[str], user_id: str) -> Dict:
        """
        تقييم الأعراض وتحديد مستوى الخطورة
        
        Args:
            symptoms: قائمة الأعراض
            user_id: معرف المستخدم
            
        Returns:
            Dict: تقييم الأعراض
        """
        try:
            assessment_result = {
                'urgency_level': UrgencyLevel.LOW.value,
                'recommendations': [],
                'warning_signs': [],
                'next_steps': [],
                'estimated_conditions': []
            }
            
            emergency_indicators = []
            high_urgency_indicators = []
            
            # تحليل كل عرض
            for symptom in symptoms:
                symptom_lower = symptom.lower()
                
                # البحث في قاعدة المعرفة
                for known_symptom, info in self.medical_knowledge_base['symptoms'].items():
                    if known_symptom in symptom_lower or symptom_lower in known_symptom:
                        # فحص مؤشرات الطوارئ
                        for indicator in info['urgency_indicators']:
                            if any(word in symptom_lower for word in indicator.split()):
                                emergency_indicators.append(indicator)
                        
                        # إضافة الحالات المحتملة
                        assessment_result['estimated_conditions'].extend(info['common_causes'])
                        
                        # إضافة الإسعافات الأولية
                        assessment_result['recommendations'].extend(info['first_aid'])
                        
                        # إضافة متى يجب طلب المساعدة
                        assessment_result['next_steps'].append(info['when_to_seek_help'])
            
            # تحديد مستوى الخطورة
            if emergency_indicators:
                assessment_result['urgency_level'] = UrgencyLevel.CRITICAL.value
                assessment_result['warning_signs'] = emergency_indicators
                assessment_result['immediate_action'] = 'اتصل بالطوارئ فوراً - 123'
            
            elif len(symptoms) > 3 or any('شديد' in s for s in symptoms):
                assessment_result['urgency_level'] = UrgencyLevel.HIGH.value
                assessment_result['immediate_action'] = 'راجع الطبيب في أقرب وقت'
            
            elif len(symptoms) > 1:
                assessment_result['urgency_level'] = UrgencyLevel.MEDIUM.value
                assessment_result['immediate_action'] = 'راقب الأعراض وراجع الطبيب إذا ساءت'
            
            # إزالة التكرارات
            assessment_result['estimated_conditions'] = list(set(assessment_result['estimated_conditions']))
            assessment_result['recommendations'] = list(set(assessment_result['recommendations']))
            assessment_result['next_steps'] = list(set(assessment_result['next_steps']))
            
            # حفظ التقييم في سياق المستخدم
            if user_id in self.user_contexts:
                self.user_contexts[user_id].collected_data['symptom_assessment'] = assessment_result
            
            return {
                'success': True,
                'assessment': assessment_result,
                'symptoms_analyzed': symptoms,
                'confidence': 0.8,
                'disclaimer': 'هذا التقييم أولي ولا يغني عن الفحص الطبي المتخصص'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تقييم الأعراض: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تقييم الأعراض'
            }
    
    def get_chatbot_analytics(self, date_range: Dict = None) -> Dict:
        """
        الحصول على إحصائيات الروبوت
        
        Args:
            date_range: نطاق التاريخ (اختياري)
            
        Returns:
            Dict: الإحصائيات
        """
        try:
            # في التطبيق الحقيقي، ستكون هذه البيانات من قاعدة البيانات
            analytics = {
                'total_conversations': len(self.conversations),
                'active_conversations': len(self.user_contexts),
                'total_messages': sum(len(conv) for conv in self.conversations.values()),
                'average_session_duration': 15.5,  # بالدقائق
                'user_satisfaction_average': 4.2,  # من 5
                'most_common_intents': {
                    'symptom_inquiry': 35,
                    'appointment_booking': 25,
                    'medication_inquiry': 20,
                    'general_health': 15,
                    'emergency': 5
                },
                'response_accuracy': 0.87,
                'emergency_cases_handled': 12,
                'successful_appointments_booked': 45
            }
            
            return {
                'success': True,
                'analytics': analytics,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على الإحصائيات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الإحصائيات'
            }
    
    # الدوال المساعدة
    def _analyze_message(self, message: str, context: ConversationContext) -> Dict:
        """تحليل رسالة المستخدم"""
        message_lower = message.lower()
        
        # تحديد النية
        intent = self._detect_intent(message_lower)
        
        # استخراج الكيانات
        entities = self._extract_entities(message, intent)
        
        # تحديد مستوى الخطورة
        urgency_level = self._assess_urgency(message_lower, entities)
        
        # حساب الثقة
        confidence = self._calculate_confidence(intent, entities, message)
        
        return {
            'intent': intent,
            'entities': entities,
            'urgency_level': urgency_level,
            'confidence': confidence,
            'original_message': message
        }
    
    def _detect_intent(self, message: str) -> str:
        """كشف نية المستخدم"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent
        
        # إذا لم يتم العثور على نية محددة، استخدم الذكاء الاصطناعي
        return self._ai_intent_detection(message)
    
    def _extract_entities(self, message: str, intent: str) -> Dict:
        """استخراج الكيانات من الرسالة"""
        entities = {}
        
        if intent == 'symptom_inquiry':
            # استخراج الأعراض
            symptoms = self._extract_symptoms(message)
            if symptoms:
                entities['symptoms'] = symptoms
        
        elif intent == 'medication_inquiry':
            # استخراج أسماء الأدوية
            medications = self._extract_medications(message)
            if medications:
                entities['medications'] = medications
        
        elif intent == 'appointment_booking':
            # استخراج نوع الطبيب والوقت المفضل
            doctor_type = self._extract_doctor_type(message)
            if doctor_type:
                entities['doctor_type'] = doctor_type
            
            time_preference = self._extract_time_preference(message)
            if time_preference:
                entities['time_preference'] = time_preference
        
        return entities
    
    def _assess_urgency(self, message: str, entities: Dict) -> str:
        """تقييم مستوى الخطورة"""
        # كلمات مفتاحية للطوارئ
        emergency_keywords = [
            'طوارئ', 'مساعدة عاجلة', 'ألم شديد', 'لا أستطيع التنفس',
            'فقدت الوعي', 'نزيف شديد', 'نوبة قلبية', 'سكتة دماغية'
        ]
        
        high_urgency_keywords = [
            'ألم شديد', 'حمى عالية', 'صعوبة تنفس', 'دوخة شديدة',
            'قيء مستمر', 'ألم في الصدر'
        ]
        
        # فحص الطوارئ
        for keyword in emergency_keywords:
            if keyword in message:
                return UrgencyLevel.CRITICAL.value
        
        # فحص الخطورة العالية
        for keyword in high_urgency_keywords:
            if keyword in message:
                return UrgencyLevel.HIGH.value
        
        # فحص الأعراض في الكيانات
        if 'symptoms' in entities:
            symptoms = entities['symptoms']
            if len(symptoms) > 2:
                return UrgencyLevel.MEDIUM.value
        
        return UrgencyLevel.LOW.value
    
    def _calculate_confidence(self, intent: str, entities: Dict, message: str) -> float:
        """حساب مستوى الثقة في التحليل"""
        confidence = 0.5  # قيمة أساسية
        
        # زيادة الثقة بناءً على وضوح النية
        if intent in self.intent_patterns:
            confidence += 0.3
        
        # زيادة الثقة بناءً على وجود كيانات
        if entities:
            confidence += 0.2 * len(entities)
        
        # تقليل الثقة للرسائل القصيرة جداً أو الطويلة جداً
        message_length = len(message.split())
        if message_length < 3 or message_length > 50:
            confidence -= 0.1
        
        return min(confidence, 1.0)
    
    def _generate_response(self, user_id: str, analysis: Dict, context: ConversationContext) -> Dict:
        """إنتاج رد الروبوت"""
        intent = analysis['intent']
        entities = analysis['entities']
        urgency_level = analysis['urgency_level']
        
        if intent == 'symptom_inquiry':
            return self._generate_symptom_response(entities, context)
        
        elif intent == 'medication_inquiry':
            return self._generate_medication_response(entities, context)
        
        elif intent == 'appointment_booking':
            return self._generate_appointment_response(entities, context)
        
        elif intent == 'emergency':
            return self._generate_emergency_response(analysis, context)
        
        elif intent == 'general_health':
            return self._generate_health_education_response(entities, context)
        
        else:
            return self._generate_general_response(analysis, context)
    
    def _generate_greeting_response(self, user_id: str) -> Dict:
        """إنتاج رسالة ترحيب"""
        import random
        
        greeting = random.choice(self.response_templates['greeting'])
        
        return {
            'message': greeting,
            'message_type': MessageType.TEXT.value,
            'confidence': 1.0
        }
    
    def _generate_symptom_response(self, entities: Dict, context: ConversationContext) -> Dict:
        """إنتاج رد للاستفسار عن الأعراض"""
        symptoms = entities.get('symptoms', [])
        
        if not symptoms:
            return {
                'message': 'يمكنك إخباري بالأعراض التي تشعر بها وسأساعدك في تقييمها.',
                'message_type': MessageType.TEXT.value,
                'confidence': 0.8,
                'quick_replies': ['حمى', 'صداع', 'ألم في الصدر', 'ألم في البطن']
            }
        
        # تقييم الأعراض
        assessment = self.assess_symptoms(symptoms, context.user_id)
        
        if assessment['success']:
            assessment_data = assessment['assessment']
            
            response_message = f"بناءً على الأعراض التي ذكرتها ({', '.join(symptoms)}):\n\n"
            
            if assessment_data['urgency_level'] == UrgencyLevel.CRITICAL.value:
                response_message += "🚨 هذه أعراض تتطلب عناية طبية فورية!\n"
                response_message += assessment_data.get('immediate_action', '')
            
            else:
                response_message += f"مستوى الخطورة: {assessment_data['urgency_level']}\n\n"
                
                if assessment_data['estimated_conditions']:
                    response_message += "الحالات المحتملة:\n"
                    for condition in assessment_data['estimated_conditions'][:3]:
                        response_message += f"• {condition}\n"
                    response_message += "\n"
                
                if assessment_data['recommendations']:
                    response_message += "نصائح أولية:\n"
                    for rec in assessment_data['recommendations'][:3]:
                        response_message += f"• {rec}\n"
                    response_message += "\n"
                
                response_message += assessment_data.get('immediate_action', '')
            
            response_message += "\n\n⚠️ هذا التقييم أولي ولا يغني عن استشارة الطبيب."
            
            return {
                'message': response_message,
                'message_type': MessageType.TEXT.value,
                'confidence': assessment['confidence'],
                'quick_replies': ['حجز موعد مع طبيب', 'أعراض أخرى', 'نصائح إضافية']
            }
        
        else:
            return {
                'message': 'عذراً، لم أتمكن من تقييم الأعراض. هل يمكنك وصفها بشكل أكثر تفصيلاً؟',
                'message_type': MessageType.TEXT.value,
                'confidence': 0.5
            }
    
    def _generate_medication_response(self, entities: Dict, context: ConversationContext) -> Dict:
        """إنتاج رد للاستفسار عن الأدوية"""
        medications = entities.get('medications', [])
        
        if not medications:
            return {
                'message': 'ما هو الدواء الذي تريد معرفة معلومات عنه؟',
                'message_type': MessageType.TEXT.value,
                'confidence': 0.8
            }
        
        medication = medications[0]  # أخذ أول دواء
        
        # البحث في قاعدة المعرفة
        for known_med, info in self.medical_knowledge_base['medications'].items():
            if known_med.lower() in medication.lower() or medication.lower() in known_med.lower():
                response_message = f"معلومات عن {known_med}:\n\n"
                response_message += f"الاستخدامات: {', '.join(info['uses'])}\n"
                response_message += f"الجرعة: {info['dosage']}\n"
                response_message += f"الحد الأقصى يومياً: {info['max_daily']}\n\n"
                response_message += "تحذيرات:\n"
                for warning in info['warnings']:
                    response_message += f"• {warning}\n"
                response_message += "\n⚠️ استشر الطبيب أو الصيدلي قبل الاستخدام."
                
                return {
                    'message': response_message,
                    'message_type': MessageType.TEXT.value,
                    'confidence': 0.9,
                    'quick_replies': ['أعراض جانبية', 'تفاعلات دوائية', 'بدائل أخرى']
                }
        
        # إذا لم يتم العثور على الدواء، استخدم الذكاء الاصطناعي
        ai_response = self._get_ai_medication_info(medication)
        
        return {
            'message': ai_response,
            'message_type': MessageType.TEXT.value,
            'confidence': 0.7
        }
    
    def _generate_appointment_response(self, entities: Dict, context: ConversationContext) -> Dict:
        """إنتاج رد لحجز الموعد"""
        doctor_type = entities.get('doctor_type', 'طبيب عام')
        
        response_message = f"سأساعدك في حجز موعد مع {doctor_type}.\n\n"
        response_message += "يرجى اختيار الوقت المفضل:"
        
        # إنشاء بطاقات للأوقات المتاحة
        time_cards = [
            {
                'title': 'صباحاً',
                'subtitle': '9:00 ص - 12:00 م',
                'action': 'book_morning'
            },
            {
                'title': 'بعد الظهر',
                'subtitle': '2:00 م - 5:00 م',
                'action': 'book_afternoon'
            },
            {
                'title': 'مساءً',
                'subtitle': '6:00 م - 9:00 م',
                'action': 'book_evening'
            }
        ]
        
        return {
            'message': response_message,
            'message_type': MessageType.CARD.value,
            'cards': time_cards,
            'confidence': 0.9,
            'quick_replies': ['صباحاً', 'بعد الظهر', 'مساءً', 'أي وقت متاح']
        }
    
    def _generate_emergency_response(self, analysis: Dict, context: ConversationContext) -> Dict:
        """إنتاج رد لحالات الطوارئ"""
        import random
        
        emergency_message = random.choice(self.response_templates['emergency_response'])
        emergency_message += "\n\nفي هذه الأثناء:\n"
        emergency_message += "• ابق هادئاً\n"
        emergency_message += "• لا تتحرك إذا كان لديك إصابة\n"
        emergency_message += "• اطلب من شخص البقاء معك\n"
        emergency_message += "• اتبع تعليمات المسعف عبر الهاتف"
        
        return {
            'message': emergency_message,
            'message_type': MessageType.TEXT.value,
            'confidence': 1.0,
            'urgency_level': UrgencyLevel.CRITICAL.value
        }
    
    def _generate_health_education_response(self, entities: Dict, context: ConversationContext) -> Dict:
        """إنتاج رد للتثقيف الصحي"""
        health_tips = [
            "💧 اشرب 8 أكواب من الماء يومياً",
            "🏃‍♂️ مارس الرياضة 30 دقيقة يومياً",
            "🥗 تناول 5 حصص من الفواكه والخضروات يومياً",
            "😴 احصل على 7-8 ساعات نوم يومياً",
            "🧘‍♀️ مارس تمارين الاسترخاء لتقليل التوتر",
            "🚭 تجنب التدخين والكحول",
            "🧼 اغسل يديك بانتظام",
            "☀️ تعرض لأشعة الشمس 15 دقيقة يومياً"
        ]
        
        import random
        selected_tips = random.sample(health_tips, 3)
        
        response_message = "إليك بعض النصائح الصحية المهمة:\n\n"
        for tip in selected_tips:
            response_message += f"{tip}\n"
        
        response_message += "\nهل تريد نصائح حول موضوع صحي محدد؟"
        
        return {
            'message': response_message,
            'message_type': MessageType.TEXT.value,
            'confidence': 0.9,
            'quick_replies': ['التغذية', 'الرياضة', 'النوم', 'الصحة النفسية']
        }
    
    def _generate_general_response(self, analysis: Dict, context: ConversationContext) -> Dict:
        """إنتاج رد عام"""
        general_responses = [
            "أفهم استفسارك. هل يمكنك توضيح أكثر كيف يمكنني مساعدتك؟",
            "أنا هنا لمساعدتك في أي استفسار صحي. ما الذي تحتاج إليه تحديداً؟",
            "يمكنني مساعدتك في الأعراض، الأدوية، حجز المواعيد، أو النصائح الصحية. ماذا تختار؟"
        ]
        
        import random
        response = random.choice(general_responses)
        
        return {
            'message': response,
            'message_type': MessageType.TEXT.value,
            'confidence': 0.6,
            'quick_replies': self.quick_replies['greeting']
        }
    
    def _handle_emergency(self, user_id: str, analysis: Dict) -> Dict:
        """معالجة حالات الطوارئ"""
        # إرسال تنبيه فوري
        emergency_response = self._generate_emergency_response(analysis, self.user_contexts[user_id])
        
        # تسجيل الحالة الطارئة
        self._log_emergency_case(user_id, analysis)
        
        # إشعار الفريق الطبي (في التطبيق الحقيقي)
        # self._notify_medical_team(user_id, analysis)
        
        return {
            'success': True,
            'message': emergency_response['message'],
            'message_type': emergency_response['message_type'],
            'urgency_level': UrgencyLevel.CRITICAL.value,
            'emergency_protocols_activated': True
        }
    
    def _update_context(self, context: ConversationContext, analysis: Dict, response: Dict):
        """تحديث سياق المحادثة"""
        context.last_activity = datetime.now()
        context.message_count += 1
        
        # تحديث البيانات المجمعة
        intent = analysis['intent']
        if intent not in context.collected_data:
            context.collected_data[intent] = []
        
        context.collected_data[intent].append({
            'entities': analysis['entities'],
            'timestamp': datetime.now().isoformat(),
            'confidence': analysis['confidence']
        })
        
        # تحديث حالة المحادثة
        if intent == 'symptom_inquiry':
            context.current_state = ConversationState.SYMPTOM_ASSESSMENT.value
        elif intent == 'appointment_booking':
            context.current_state = ConversationState.APPOINTMENT_BOOKING.value
        elif intent == 'medication_inquiry':
            context.current_state = ConversationState.MEDICATION_INQUIRY.value
        elif intent == 'emergency':
            context.current_state = ConversationState.EMERGENCY_ASSESSMENT.value
    
    def _is_session_expired(self, context: ConversationContext) -> bool:
        """فحص انتهاء صلاحية الجلسة"""
        timeout_minutes = self.chatbot_settings['session_timeout_minutes']
        time_diff = datetime.now() - context.last_activity
        return time_diff.total_seconds() > (timeout_minutes * 60)
    
    def _extract_symptoms(self, message: str) -> List[str]:
        """استخراج الأعراض من الرسالة"""
        symptoms = []
        message_lower = message.lower()
        
        # قائمة الأعراض الشائعة
        common_symptoms = [
            'حمى', 'صداع', 'ألم', 'دوخة', 'غثيان', 'قيء', 'إسهال',
            'إمساك', 'سعال', 'زكام', 'التهاب الحلق', 'ضيق تنفس',
            'خفقان', 'تعب', 'إرهاق', 'أرق', 'طفح جلدي'
        ]
        
        for symptom in common_symptoms:
            if symptom in message_lower:
                symptoms.append(symptom)
        
        return symptoms
    
    def _extract_medications(self, message: str) -> List[str]:
        """استخراج أسماء الأدوية من الرسالة"""
        medications = []
        message_lower = message.lower()
        
        # قائمة الأدوية الشائعة
        common_medications = [
            'باراسيتامول', 'إيبوبروفين', 'أسبرين', 'أموكسيسيلين',
            'أوجمنتين', 'فولتارين', 'بروفين', 'أدول', 'بانادول'
        ]
        
        for medication in common_medications:
            if medication.lower() in message_lower:
                medications.append(medication)
        
        return medications
    
    def _extract_doctor_type(self, message: str) -> Optional[str]:
        """استخراج نوع الطبيب من الرسالة"""
        message_lower = message.lower()
        
        doctor_types = {
            'عام': 'طبيب عام',
            'أسنان': 'طبيب أسنان',
            'عيون': 'طبيب عيون',
            'نساء': 'طبيب نساء وتوليد',
            'أطفال': 'طبيب أطفال',
            'قلب': 'طبيب قلب',
            'جلدية': 'طبيب جلدية',
            'عظام': 'طبيب عظام'
        }
        
        for keyword, doctor_type in doctor_types.items():
            if keyword in message_lower:
                return doctor_type
        
        return None
    
    def _extract_time_preference(self, message: str) -> Optional[str]:
        """استخراج الوقت المفضل من الرسالة"""
        message_lower = message.lower()
        
        time_keywords = {
            'صباح': 'صباحاً',
            'ظهر': 'بعد الظهر',
            'مساء': 'مساءً',
            'ليل': 'ليلاً'
        }
        
        for keyword, time_period in time_keywords.items():
            if keyword in message_lower:
                return time_period
        
        return None
    
    def _ai_intent_detection(self, message: str) -> str:
        """كشف النية باستخدام الذكاء الاصطناعي"""
        try:
            prompt = f"""
            حدد نية المستخدم من الرسالة التالية:
            "{message}"
            
            النوايا المحتملة:
            - symptom_inquiry: استفسار عن أعراض
            - medication_inquiry: استفسار عن دواء
            - appointment_booking: حجز موعد
            - emergency: حالة طوارئ
            - general_health: استفسار صحي عام
            - greeting: تحية
            
            أجب بكلمة واحدة فقط من القائمة أعلاه.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            intent = response.choices[0].message.content.strip()
            return intent if intent in ['symptom_inquiry', 'medication_inquiry', 'appointment_booking', 'emergency', 'general_health', 'greeting'] else 'general_health'
            
        except Exception as e:
            current_app.logger.error(f"خطأ في كشف النية بالذكاء الاصطناعي: {str(e)}")
            return 'general_health'
    
    def _get_ai_health_information(self, topic: str) -> str:
        """الحصول على معلومات صحية باستخدام الذكاء الاصطناعي"""
        try:
            prompt = f"""
            أعط معلومات صحية موجزة ودقيقة عن: {topic}
            
            يجب أن تتضمن الإجابة:
            - تعريف مبسط
            - الأسباب الشائعة
            - الأعراض
            - نصائح الوقاية
            - متى يجب استشارة الطبيب
            
            اكتب بالعربية وبأسلوب مفهوم للعامة.
            أضف تنبيه أن هذه المعلومات للتثقيف فقط.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على المعلومات الصحية: {str(e)}")
            return "عذراً، لم أتمكن من الحصول على معلومات حول هذا الموضوع. يرجى استشارة طبيب مختص."
    
    def _get_ai_medication_info(self, medication: str) -> str:
        """الحصول على معلومات الدواء باستخدام الذكاء الاصطناعي"""
        try:
            prompt = f"""
            أعط معلومات أساسية عن الدواء: {medication}
            
            يجب أن تتضمن:
            - الاستخدامات الرئيسية
            - الجرعة العامة (بدون تحديد دقيق)
            - التحذيرات المهمة
            - نصيحة بضرورة استشارة الطبيب أو الصيدلي
            
            اكتب بالعربية وأضف تنبيه واضح أن هذه معلومات عامة فقط.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على معلومات الدواء: {str(e)}")
            return "عذراً، لم أتمكن من الحصول على معلومات حول هذا الدواء. يرجى استشارة الصيدلي."
    
    def _generate_farewell_message(self, context: ConversationContext) -> str:
        """إنتاج رسالة وداع"""
        farewell_messages = [
            "شكراً لاستخدام خدمة المساعد الصحي. أتمنى لك دوام الصحة والعافية! 🌟",
            "كان من دواعي سروري مساعدتك. اعتن بصحتك ولا تتردد في العودة إلينا! 💚",
            "أتمنى أن أكون قد ساعدتك. صحتك تهمنا، فلا تتردد في التواصل معنا مرة أخرى! 🏥"
        ]
        
        import random
        return random.choice(farewell_messages)
    
    def _save_feedback(self, user_id: str, feedback: Dict):
        """حفظ تقييم المستخدم"""
        # في التطبيق الحقيقي، سيتم حفظ التقييم في قاعدة البيانات
        pass
    
    def _save_conversation_analytics(self, context: ConversationContext):
        """حفظ إحصائيات المحادثة"""
        # في التطبيق الحقيقي، سيتم حفظ الإحصائيات في قاعدة البيانات
        pass
    
    def _log_emergency_case(self, user_id: str, analysis: Dict):
        """تسجيل حالة الطوارئ"""
        # في التطبيق الحقيقي، سيتم تسجيل الحالة وإشعار الفريق الطبي
        current_app.logger.warning(f"حالة طوارئ للمستخدم {user_id}: {analysis}")
    
    def _start_message_processor(self):
        """بدء معالج الرسائل في خيط منفصل"""
        def process_messages():
            while True:
                try:
                    if self.message_queue:
                        message_data = self.message_queue.pop(0)
                        # معالجة الرسالة
                        self.process_message(
                            message_data['user_id'],
                            message_data['message'],
                            message_data.get('message_type', 'text')
                        )
                    time.sleep(0.1)  # تجنب استهلاك المعالج
                except Exception as e:
                    current_app.logger.error(f"خطأ في معالج الرسائل: {str(e)}")
                    time.sleep(1)
        
        self.processing_thread = threading.Thread(target=process_messages, daemon=True)
        self.processing_thread.start()

