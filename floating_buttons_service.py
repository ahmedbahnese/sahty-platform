"""
خدمة الأزرار العائمة الذكية والإجراءات السريعة
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class ButtonType(Enum):
    EMERGENCY = "طوارئ"
    QUICK_APPOINTMENT = "موعد سريع"
    MEDICATION_REMINDER = "تذكير دواء"
    HEALTH_CHECK = "فحص صحي"
    CALL_DOCTOR = "اتصال بطبيب"
    PHARMACY_FINDER = "البحث عن صيدلية"
    HOSPITAL_FINDER = "البحث عن مستشفى"
    SYMPTOM_CHECKER = "فحص الأعراض"
    AI_ASSISTANT = "المساعد الذكي"
    BLOOD_PRESSURE = "قياس ضغط الدم"
    BLOOD_SUGAR = "قياس السكر"
    WEIGHT_TRACKER = "متابعة الوزن"
    WATER_REMINDER = "تذكير شرب الماء"
    EXERCISE_REMINDER = "تذكير التمارين"
    MOOD_TRACKER = "متابعة المزاج"
    SLEEP_TRACKER = "متابعة النوم"
    NUTRITION_LOG = "تسجيل الطعام"
    INSURANCE_CHECK = "فحص التأمين"
    MEDICAL_RECORDS = "السجلات الطبية"
    FAMILY_HEALTH = "صحة العائلة"

class ButtonContext(Enum):
    HOME = "الرئيسية"
    PROFILE = "الملف الشخصي"
    APPOINTMENTS = "المواعيد"
    MEDICATIONS = "الأدوية"
    HEALTH_RECORDS = "السجلات الصحية"
    EMERGENCY = "الطوارئ"
    FAMILY = "العائلة"
    SETTINGS = "الإعدادات"

class ButtonPriority(Enum):
    CRITICAL = "حرج"
    HIGH = "عالي"
    MEDIUM = "متوسط"
    LOW = "منخفض"

class ButtonVisibility(Enum):
    ALWAYS = "دائماً"
    CONTEXT_BASED = "حسب السياق"
    TIME_BASED = "حسب الوقت"
    CONDITION_BASED = "حسب الحالة"
    USER_PREFERENCE = "حسب تفضيل المستخدم"

@dataclass
class FloatingButton:
    button_id: str
    button_type: str
    title: str
    description: str
    icon: str
    color: str
    action: str
    context: List[str]
    priority: str
    visibility: str
    conditions: Dict
    position: Dict
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]

@dataclass
class ButtonAction:
    action_id: str
    button_id: str
    user_id: str
    action_type: str
    parameters: Dict
    executed_at: datetime
    result: Dict
    success: bool

class FloatingButtonsService:
    def __init__(self):
        """تهيئة خدمة الأزرار العائمة الذكية"""
        
        # إعدادات الأزرار
        self.button_settings = {
            'max_buttons_per_screen': 5,
            'auto_hide_duration_seconds': 30,
            'animation_duration_ms': 300,
            'button_size_px': 56,
            'margin_px': 16,
            'enable_haptic_feedback': True,
            'enable_sound_feedback': False,
            'smart_positioning': True,
            'context_awareness': True
        }
        
        # قوالب الأزرار المحددة مسبقاً
        self.button_templates = {
            ButtonType.EMERGENCY.value: {
                'title': 'طوارئ',
                'description': 'اتصال سريع بخدمات الطوارئ',
                'icon': 'emergency',
                'color': '#FF0000',
                'action': 'emergency_call',
                'priority': ButtonPriority.CRITICAL.value,
                'visibility': ButtonVisibility.ALWAYS.value,
                'contexts': [ButtonContext.HOME.value, ButtonContext.EMERGENCY.value],
                'conditions': {},
                'position': {'bottom': 20, 'right': 20}
            },
            ButtonType.QUICK_APPOINTMENT.value: {
                'title': 'موعد سريع',
                'description': 'حجز موعد طبي سريع',
                'icon': 'calendar_plus',
                'color': '#2196F3',
                'action': 'quick_appointment',
                'priority': ButtonPriority.HIGH.value,
                'visibility': ButtonVisibility.CONTEXT_BASED.value,
                'contexts': [ButtonContext.HOME.value, ButtonContext.APPOINTMENTS.value],
                'conditions': {'has_preferred_doctor': True},
                'position': {'bottom': 90, 'right': 20}
            },
            ButtonType.MEDICATION_REMINDER.value: {
                'title': 'تذكير دواء',
                'description': 'تسجيل تناول الدواء',
                'icon': 'pill',
                'color': '#4CAF50',
                'action': 'medication_reminder',
                'priority': ButtonPriority.HIGH.value,
                'visibility': ButtonVisibility.TIME_BASED.value,
                'contexts': [ButtonContext.HOME.value, ButtonContext.MEDICATIONS.value],
                'conditions': {'has_pending_medications': True},
                'position': {'bottom': 160, 'right': 20}
            },
            ButtonType.AI_ASSISTANT.value: {
                'title': 'المساعد الذكي',
                'description': 'استشارة المساعد الطبي الذكي',
                'icon': 'robot',
                'color': '#9C27B0',
                'action': 'ai_assistant',
                'priority': ButtonPriority.MEDIUM.value,
                'visibility': ButtonVisibility.ALWAYS.value,
                'contexts': [ButtonContext.HOME.value],
                'conditions': {},
                'position': {'bottom': 230, 'right': 20}
            },
            ButtonType.SYMPTOM_CHECKER.value: {
                'title': 'فحص الأعراض',
                'description': 'تحليل الأعراض والحصول على نصائح',
                'icon': 'stethoscope',
                'color': '#FF9800',
                'action': 'symptom_checker',
                'priority': ButtonPriority.MEDIUM.value,
                'visibility': ButtonVisibility.CONTEXT_BASED.value,
                'contexts': [ButtonContext.HOME.value, ButtonContext.HEALTH_RECORDS.value],
                'conditions': {},
                'position': {'bottom': 300, 'right': 20}
            },
            ButtonType.BLOOD_PRESSURE.value: {
                'title': 'قياس الضغط',
                'description': 'تسجيل قراءة ضغط الدم',
                'icon': 'heart_pulse',
                'color': '#E91E63',
                'action': 'blood_pressure_log',
                'priority': ButtonPriority.MEDIUM.value,
                'visibility': ButtonVisibility.CONDITION_BASED.value,
                'contexts': [ButtonContext.HOME.value, ButtonContext.HEALTH_RECORDS.value],
                'conditions': {'has_hypertension': True},
                'position': {'bottom': 160, 'left': 20}
            },
            ButtonType.BLOOD_SUGAR.value: {
                'title': 'قياس السكر',
                'description': 'تسجيل قراءة السكر في الدم',
                'icon': 'droplet',
                'color': '#795548',
                'action': 'blood_sugar_log',
                'priority': ButtonPriority.MEDIUM.value,
                'visibility': ButtonVisibility.CONDITION_BASED.value,
                'contexts': [ButtonContext.HOME.value, ButtonContext.HEALTH_RECORDS.value],
                'conditions': {'has_diabetes': True},
                'position': {'bottom': 230, 'left': 20}
            },
            ButtonType.WATER_REMINDER.value: {
                'title': 'شرب الماء',
                'description': 'تسجيل شرب كوب ماء',
                'icon': 'water_drop',
                'color': '#00BCD4',
                'action': 'water_intake',
                'priority': ButtonPriority.LOW.value,
                'visibility': ButtonVisibility.TIME_BASED.value,
                'contexts': [ButtonContext.HOME.value],
                'conditions': {'water_reminder_enabled': True},
                'position': {'bottom': 300, 'left': 20}
            },
            ButtonType.MOOD_TRACKER.value: {
                'title': 'تسجيل المزاج',
                'description': 'تسجيل الحالة المزاجية',
                'icon': 'mood',
                'color': '#FFEB3B',
                'action': 'mood_log',
                'priority': ButtonPriority.LOW.value,
                'visibility': ButtonVisibility.TIME_BASED.value,
                'contexts': [ButtonContext.HOME.value],
                'conditions': {'mood_tracking_enabled': True},
                'position': {'bottom': 370, 'left': 20}
            },
            ButtonType.FAMILY_HEALTH.value: {
                'title': 'صحة العائلة',
                'description': 'عرض حالة أفراد العائلة الصحية',
                'icon': 'family',
                'color': '#607D8B',
                'action': 'family_health',
                'priority': ButtonPriority.MEDIUM.value,
                'visibility': ButtonVisibility.CONTEXT_BASED.value,
                'contexts': [ButtonContext.HOME.value, ButtonContext.FAMILY.value],
                'conditions': {'has_family_members': True},
                'position': {'top': 100, 'right': 20}
            }
        }
        
        # قواعد الذكاء الاصطناعي للأزرار
        self.ai_rules = {
            'emergency_detection': {
                'keywords': ['طوارئ', 'ألم شديد', 'نزيف', 'صعوبة تنفس', 'فقدان وعي'],
                'actions': ['show_emergency_button', 'highlight_emergency_button']
            },
            'medication_time': {
                'conditions': ['current_time_matches_medication_schedule'],
                'actions': ['show_medication_reminder', 'send_notification']
            },
            'appointment_reminder': {
                'conditions': ['appointment_in_next_24_hours'],
                'actions': ['show_appointment_reminder', 'enable_quick_reschedule']
            },
            'health_check_due': {
                'conditions': ['last_checkup_over_6_months'],
                'actions': ['show_health_check_button', 'suggest_appointment']
            },
            'chronic_condition_management': {
                'conditions': ['has_chronic_condition', 'no_recent_readings'],
                'actions': ['show_monitoring_buttons', 'remind_measurements']
            }
        }
        
        # قاعدة بيانات الأزرار (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.user_buttons = {}
        self.button_actions = {}
        self.button_analytics = {}
        self.context_history = {}
    
    def get_user_buttons(self, user_data: Dict) -> Dict:
        """
        الحصول على الأزرار المناسبة للمستخدم
        
        Args:
            user_data: بيانات المستخدم والسياق
            
        Returns:
            Dict: قائمة الأزرار المناسبة
        """
        try:
            user_id = user_data.get('user_id')
            current_context = user_data.get('context', ButtonContext.HOME.value)
            user_profile = user_data.get('profile', {})
            current_time = datetime.now()
            
            # الحصول على الأزرار المخصصة للمستخدم
            user_custom_buttons = self.user_buttons.get(user_id, {})
            
            # تحديد الأزرار المناسبة حسب السياق والشروط
            suitable_buttons = []
            
            for button_type, template in self.button_templates.items():
                # فحص السياق
                if current_context in template['contexts']:
                    # فحص الشروط
                    if self._check_button_conditions(template['conditions'], user_profile):
                        # فحص الرؤية
                        if self._check_button_visibility(template, user_profile, current_time):
                            # إنشاء الزر
                            button = self._create_button_from_template(
                                button_type, template, user_id, current_context
                            )
                            
                            # تطبيق التخصيصات الشخصية
                            if button_type in user_custom_buttons:
                                button = self._apply_user_customizations(
                                    button, user_custom_buttons[button_type]
                                )
                            
                            suitable_buttons.append(button)
            
            # ترتيب الأزرار حسب الأولوية
            sorted_buttons = sorted(
                suitable_buttons, 
                key=lambda x: self._get_priority_score(x.priority), 
                reverse=True
            )
            
            # تطبيق الحد الأقصى
            final_buttons = sorted_buttons[:self.button_settings['max_buttons_per_screen']]
            
            # تطبيق الذكاء الاصطناعي للتحسين
            ai_optimized_buttons = self._apply_ai_optimization(final_buttons, user_data)
            
            # تحديث تاريخ السياق
            self._update_context_history(user_id, current_context, current_time)
            
            return {
                'success': True,
                'buttons': [button.__dict__ for button in ai_optimized_buttons],
                'context': current_context,
                'total_available': len(suitable_buttons),
                'ai_optimized': True,
                'settings': {
                    'animation_duration': self.button_settings['animation_duration_ms'],
                    'auto_hide_duration': self.button_settings['auto_hide_duration_seconds'],
                    'haptic_feedback': self.button_settings['enable_haptic_feedback']
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على أزرار المستخدم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الأزرار'
            }
    
    def execute_button_action(self, action_data: Dict) -> Dict:
        """
        تنفيذ إجراء الزر
        
        Args:
            action_data: بيانات الإجراء
            
        Returns:
            Dict: نتيجة تنفيذ الإجراء
        """
        try:
            user_id = action_data.get('user_id')
            button_id = action_data.get('button_id')
            action_type = action_data.get('action_type')
            parameters = action_data.get('parameters', {})
            
            # إنشاء معرف الإجراء
            action_id = str(uuid.uuid4())
            
            # تنفيذ الإجراء حسب النوع
            result = self._execute_specific_action(action_type, parameters, user_id)
            
            # تسجيل الإجراء
            button_action = ButtonAction(
                action_id=action_id,
                button_id=button_id,
                user_id=user_id,
                action_type=action_type,
                parameters=parameters,
                executed_at=datetime.now(),
                result=result,
                success=result.get('success', False)
            )
            
            # حفظ الإجراء
            if user_id not in self.button_actions:
                self.button_actions[user_id] = []
            self.button_actions[user_id].append(button_action)
            
            # تحديث الإحصائيات
            self._update_button_analytics(button_id, action_type, result.get('success', False))
            
            # تحديث آخر استخدام للزر
            self._update_button_last_used(button_id, user_id)
            
            return {
                'success': True,
                'action_id': action_id,
                'result': result,
                'executed_at': button_action.executed_at.isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تنفيذ إجراء الزر: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تنفيذ الإجراء'
            }
    
    def customize_button(self, customization_data: Dict) -> Dict:
        """
        تخصيص زر للمستخدم
        
        Args:
            customization_data: بيانات التخصيص
            
        Returns:
            Dict: نتيجة التخصيص
        """
        try:
            user_id = customization_data.get('user_id')
            button_type = customization_data.get('button_type')
            customizations = customization_data.get('customizations', {})
            
            # التحقق من صحة نوع الزر
            if button_type not in self.button_templates:
                return {
                    'success': False,
                    'error': 'نوع زر غير صالح'
                }
            
            # تهيئة أزرار المستخدم إذا لم تكن موجودة
            if user_id not in self.user_buttons:
                self.user_buttons[user_id] = {}
            
            # حفظ التخصيصات
            self.user_buttons[user_id][button_type] = {
                'customizations': customizations,
                'created_at': datetime.now(),
                'last_updated': datetime.now()
            }
            
            return {
                'success': True,
                'message': 'تم تخصيص الزر بنجاح',
                'button_type': button_type,
                'customizations': customizations
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تخصيص الزر: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تخصيص الزر'
            }
    
    def get_button_analytics(self, user_id: str, period_days: int = 30) -> Dict:
        """
        الحصول على إحصائيات استخدام الأزرار
        
        Args:
            user_id: معرف المستخدم
            period_days: فترة الإحصائيات بالأيام
            
        Returns:
            Dict: إحصائيات الاستخدام
        """
        try:
            user_actions = self.button_actions.get(user_id, [])
            
            # فلترة الإجراءات حسب الفترة
            cutoff_date = datetime.now() - timedelta(days=period_days)
            recent_actions = [
                action for action in user_actions 
                if action.executed_at >= cutoff_date
            ]
            
            # تحليل الاستخدام
            usage_stats = self._analyze_button_usage(recent_actions)
            
            # إحصائيات الأزرار الأكثر استخداماً
            most_used_buttons = self._get_most_used_buttons(recent_actions)
            
            # أوقات الاستخدام
            usage_patterns = self._analyze_usage_patterns(recent_actions)
            
            # معدل النجاح
            success_rate = self._calculate_success_rate(recent_actions)
            
            return {
                'success': True,
                'period_days': period_days,
                'total_actions': len(recent_actions),
                'usage_stats': usage_stats,
                'most_used_buttons': most_used_buttons,
                'usage_patterns': usage_patterns,
                'success_rate': success_rate,
                'recommendations': self._generate_usage_recommendations(usage_stats)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على إحصائيات الأزرار: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الإحصائيات'
            }
    
    def smart_button_suggestions(self, user_data: Dict) -> Dict:
        """
        اقتراحات ذكية للأزرار
        
        Args:
            user_data: بيانات المستخدم
            
        Returns:
            Dict: اقتراحات الأزرار الذكية
        """
        try:
            user_id = user_data.get('user_id')
            current_context = user_data.get('context')
            user_profile = user_data.get('profile', {})
            recent_activity = user_data.get('recent_activity', [])
            
            suggestions = []
            
            # اقتراحات حسب النشاط الأخير
            activity_suggestions = self._get_activity_based_suggestions(recent_activity)
            suggestions.extend(activity_suggestions)
            
            # اقتراحات حسب الملف الصحي
            health_suggestions = self._get_health_based_suggestions(user_profile)
            suggestions.extend(health_suggestions)
            
            # اقتراحات حسب الوقت
            time_suggestions = self._get_time_based_suggestions(user_profile)
            suggestions.extend(time_suggestions)
            
            # اقتراحات حسب السياق
            context_suggestions = self._get_context_based_suggestions(current_context, user_profile)
            suggestions.extend(context_suggestions)
            
            # ترتيب الاقتراحات حسب الأولوية
            sorted_suggestions = sorted(
                suggestions, 
                key=lambda x: x.get('relevance_score', 0), 
                reverse=True
            )
            
            return {
                'success': True,
                'suggestions': sorted_suggestions[:5],
                'total_suggestions': len(suggestions),
                'context': current_context
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في اقتراحات الأزرار الذكية: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الاقتراحات الذكية'
            }
    
    def update_button_positions(self, position_data: Dict) -> Dict:
        """
        تحديث مواضع الأزرار
        
        Args:
            position_data: بيانات المواضع
            
        Returns:
            Dict: نتيجة التحديث
        """
        try:
            user_id = position_data.get('user_id')
            button_positions = position_data.get('positions', {})
            
            # تحديث مواضع الأزرار للمستخدم
            if user_id not in self.user_buttons:
                self.user_buttons[user_id] = {}
            
            for button_id, position in button_positions.items():
                if button_id not in self.user_buttons[user_id]:
                    self.user_buttons[user_id][button_id] = {}
                
                self.user_buttons[user_id][button_id]['position'] = position
                self.user_buttons[user_id][button_id]['last_updated'] = datetime.now()
            
            return {
                'success': True,
                'message': 'تم تحديث مواضع الأزرار بنجاح',
                'updated_buttons': len(button_positions)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحديث مواضع الأزرار: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تحديث المواضع'
            }
    
    # الدوال المساعدة
    def _check_button_conditions(self, conditions: Dict, user_profile: Dict) -> bool:
        """فحص شروط عرض الزر"""
        if not conditions:
            return True
        
        for condition, required_value in conditions.items():
            user_value = user_profile.get(condition)
            
            if isinstance(required_value, bool):
                if bool(user_value) != required_value:
                    return False
            elif isinstance(required_value, (int, float)):
                if user_value != required_value:
                    return False
            elif isinstance(required_value, str):
                if str(user_value) != required_value:
                    return False
            elif isinstance(required_value, list):
                if user_value not in required_value:
                    return False
        
        return True
    
    def _check_button_visibility(self, template: Dict, user_profile: Dict, current_time: datetime) -> bool:
        """فحص رؤية الزر"""
        visibility = template['visibility']
        
        if visibility == ButtonVisibility.ALWAYS.value:
            return True
        elif visibility == ButtonVisibility.CONTEXT_BASED.value:
            # فحص السياق (تم فحصه مسبقاً)
            return True
        elif visibility == ButtonVisibility.TIME_BASED.value:
            return self._check_time_based_visibility(template, current_time)
        elif visibility == ButtonVisibility.CONDITION_BASED.value:
            return self._check_condition_based_visibility(template, user_profile)
        elif visibility == ButtonVisibility.USER_PREFERENCE.value:
            return user_profile.get(f"{template['title']}_enabled", True)
        
        return True
    
    def _check_time_based_visibility(self, template: Dict, current_time: datetime) -> bool:
        """فحص الرؤية المبنية على الوقت"""
        button_type = template.get('title')
        
        if button_type == 'تذكير دواء':
            # عرض في أوقات الأدوية
            hour = current_time.hour
            return hour in [8, 12, 18, 22]  # أوقات الأدوية الشائعة
        elif button_type == 'شرب الماء':
            # عرض كل ساعتين في النهار
            hour = current_time.hour
            return 6 <= hour <= 22 and hour % 2 == 0
        elif button_type == 'تسجيل المزاج':
            # عرض مرة في اليوم
            hour = current_time.hour
            return hour == 20  # في المساء
        
        return True
    
    def _check_condition_based_visibility(self, template: Dict, user_profile: Dict) -> bool:
        """فحص الرؤية المبنية على الحالة"""
        conditions = template.get('conditions', {})
        
        for condition, required_value in conditions.items():
            if condition == 'has_hypertension':
                return user_profile.get('medical_conditions', {}).get('hypertension', False)
            elif condition == 'has_diabetes':
                return user_profile.get('medical_conditions', {}).get('diabetes', False)
            elif condition == 'has_family_members':
                return len(user_profile.get('family_members', [])) > 0
        
        return True
    
    def _create_button_from_template(self, button_type: str, template: Dict, 
                                   user_id: str, context: str) -> FloatingButton:
        """إنشاء زر من القالب"""
        button_id = f"{user_id}_{button_type}_{context}"
        
        return FloatingButton(
            button_id=button_id,
            button_type=button_type,
            title=template['title'],
            description=template['description'],
            icon=template['icon'],
            color=template['color'],
            action=template['action'],
            context=template['contexts'],
            priority=template['priority'],
            visibility=template['visibility'],
            conditions=template['conditions'],
            position=template['position'].copy(),
            is_active=True,
            created_at=datetime.now(),
            last_used=None
        )
    
    def _apply_user_customizations(self, button: FloatingButton, customizations: Dict) -> FloatingButton:
        """تطبيق التخصيصات الشخصية"""
        custom_data = customizations.get('customizations', {})
        
        if 'title' in custom_data:
            button.title = custom_data['title']
        if 'color' in custom_data:
            button.color = custom_data['color']
        if 'position' in custom_data:
            button.position = custom_data['position']
        if 'is_active' in custom_data:
            button.is_active = custom_data['is_active']
        
        return button
    
    def _get_priority_score(self, priority: str) -> int:
        """الحصول على نقاط الأولوية"""
        priority_scores = {
            ButtonPriority.CRITICAL.value: 4,
            ButtonPriority.HIGH.value: 3,
            ButtonPriority.MEDIUM.value: 2,
            ButtonPriority.LOW.value: 1
        }
        return priority_scores.get(priority, 1)
    
    def _apply_ai_optimization(self, buttons: List[FloatingButton], user_data: Dict) -> List[FloatingButton]:
        """تطبيق تحسين الذكاء الاصطناعي"""
        user_id = user_data.get('user_id')
        user_profile = user_data.get('profile', {})
        
        # تحليل سلوك المستخدم
        user_actions = self.button_actions.get(user_id, [])
        
        # تعديل ترتيب الأزرار حسب الاستخدام
        for button in buttons:
            usage_count = len([
                action for action in user_actions 
                if action.button_id == button.button_id
            ])
            
            # زيادة الأولوية للأزرار المستخدمة كثيراً
            if usage_count > 10:
                button.priority = ButtonPriority.HIGH.value
            elif usage_count > 5:
                button.priority = ButtonPriority.MEDIUM.value
        
        # تطبيق قواعد الذكاء الاصطناعي
        for rule_name, rule_data in self.ai_rules.items():
            if self._check_ai_rule_conditions(rule_data, user_profile, user_data):
                buttons = self._apply_ai_rule_actions(buttons, rule_data)
        
        return buttons
    
    def _check_ai_rule_conditions(self, rule_data: Dict, user_profile: Dict, user_data: Dict) -> bool:
        """فحص شروط قواعد الذكاء الاصطناعي"""
        conditions = rule_data.get('conditions', [])
        keywords = rule_data.get('keywords', [])
        
        # فحص الكلمات المفتاحية في النشاط الأخير
        recent_activity = user_data.get('recent_activity', [])
        for activity in recent_activity:
            activity_text = activity.get('description', '').lower()
            for keyword in keywords:
                if keyword in activity_text:
                    return True
        
        # فحص الشروط
        for condition in conditions:
            if condition == 'current_time_matches_medication_schedule':
                # فحص مواعيد الأدوية
                current_hour = datetime.now().hour
                medication_times = user_profile.get('medication_schedule', [])
                if current_hour in medication_times:
                    return True
            elif condition == 'appointment_in_next_24_hours':
                # فحص المواعيد القادمة
                upcoming_appointments = user_profile.get('upcoming_appointments', [])
                if upcoming_appointments:
                    return True
            elif condition == 'last_checkup_over_6_months':
                # فحص آخر فحص طبي
                last_checkup = user_profile.get('last_checkup_date')
                if last_checkup:
                    last_checkup_date = datetime.fromisoformat(last_checkup)
                    if datetime.now() - last_checkup_date > timedelta(days=180):
                        return True
        
        return False
    
    def _apply_ai_rule_actions(self, buttons: List[FloatingButton], rule_data: Dict) -> List[FloatingButton]:
        """تطبيق إجراءات قواعد الذكاء الاصطناعي"""
        actions = rule_data.get('actions', [])
        
        for action in actions:
            if action == 'show_emergency_button':
                # إظهار زر الطوارئ
                for button in buttons:
                    if button.button_type == ButtonType.EMERGENCY.value:
                        button.priority = ButtonPriority.CRITICAL.value
            elif action == 'highlight_emergency_button':
                # تمييز زر الطوارئ
                for button in buttons:
                    if button.button_type == ButtonType.EMERGENCY.value:
                        button.color = '#FF0000'  # أحمر فاتح
            elif action == 'show_medication_reminder':
                # إظهار تذكير الدواء
                for button in buttons:
                    if button.button_type == ButtonType.MEDICATION_REMINDER.value:
                        button.priority = ButtonPriority.HIGH.value
        
        return buttons
    
    def _execute_specific_action(self, action_type: str, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ إجراء محدد"""
        try:
            if action_type == 'emergency_call':
                return self._execute_emergency_call(parameters, user_id)
            elif action_type == 'quick_appointment':
                return self._execute_quick_appointment(parameters, user_id)
            elif action_type == 'medication_reminder':
                return self._execute_medication_reminder(parameters, user_id)
            elif action_type == 'ai_assistant':
                return self._execute_ai_assistant(parameters, user_id)
            elif action_type == 'symptom_checker':
                return self._execute_symptom_checker(parameters, user_id)
            elif action_type == 'blood_pressure_log':
                return self._execute_blood_pressure_log(parameters, user_id)
            elif action_type == 'blood_sugar_log':
                return self._execute_blood_sugar_log(parameters, user_id)
            elif action_type == 'water_intake':
                return self._execute_water_intake(parameters, user_id)
            elif action_type == 'mood_log':
                return self._execute_mood_log(parameters, user_id)
            elif action_type == 'family_health':
                return self._execute_family_health(parameters, user_id)
            else:
                return {
                    'success': False,
                    'error': 'نوع إجراء غير مدعوم'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ في تنفيذ الإجراء: {str(e)}'
            }
    
    def _execute_emergency_call(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ اتصال الطوارئ"""
        emergency_number = parameters.get('number', '123')  # رقم الطوارئ
        location = parameters.get('location')
        
        # في التطبيق الحقيقي، سيتم الاتصال الفعلي
        return {
            'success': True,
            'action': 'emergency_call_initiated',
            'emergency_number': emergency_number,
            'location_sent': bool(location),
            'message': 'تم بدء اتصال الطوارئ'
        }
    
    def _execute_quick_appointment(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ حجز موعد سريع"""
        doctor_id = parameters.get('doctor_id')
        specialty = parameters.get('specialty')
        
        # محاكاة حجز موعد
        return {
            'success': True,
            'action': 'appointment_booked',
            'appointment_id': str(uuid.uuid4()),
            'doctor_id': doctor_id,
            'specialty': specialty,
            'scheduled_time': (datetime.now() + timedelta(days=1)).isoformat(),
            'message': 'تم حجز موعد سريع'
        }
    
    def _execute_medication_reminder(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ تذكير الدواء"""
        medication_id = parameters.get('medication_id')
        taken = parameters.get('taken', True)
        
        return {
            'success': True,
            'action': 'medication_logged',
            'medication_id': medication_id,
            'taken': taken,
            'logged_at': datetime.now().isoformat(),
            'message': 'تم تسجيل تناول الدواء' if taken else 'تم تسجيل عدم تناول الدواء'
        }
    
    def _execute_ai_assistant(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ المساعد الذكي"""
        query = parameters.get('query', '')
        
        return {
            'success': True,
            'action': 'ai_assistant_opened',
            'query': query,
            'session_id': str(uuid.uuid4()),
            'message': 'تم فتح المساعد الذكي'
        }
    
    def _execute_symptom_checker(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ فحص الأعراض"""
        symptoms = parameters.get('symptoms', [])
        
        return {
            'success': True,
            'action': 'symptom_check_started',
            'symptoms': symptoms,
            'check_id': str(uuid.uuid4()),
            'message': 'تم بدء فحص الأعراض'
        }
    
    def _execute_blood_pressure_log(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ تسجيل ضغط الدم"""
        systolic = parameters.get('systolic')
        diastolic = parameters.get('diastolic')
        
        return {
            'success': True,
            'action': 'blood_pressure_logged',
            'systolic': systolic,
            'diastolic': diastolic,
            'logged_at': datetime.now().isoformat(),
            'message': 'تم تسجيل قراءة ضغط الدم'
        }
    
    def _execute_blood_sugar_log(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ تسجيل السكر"""
        glucose_level = parameters.get('glucose_level')
        meal_relation = parameters.get('meal_relation', 'fasting')
        
        return {
            'success': True,
            'action': 'blood_sugar_logged',
            'glucose_level': glucose_level,
            'meal_relation': meal_relation,
            'logged_at': datetime.now().isoformat(),
            'message': 'تم تسجيل قراءة السكر'
        }
    
    def _execute_water_intake(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ تسجيل شرب الماء"""
        amount_ml = parameters.get('amount_ml', 250)
        
        return {
            'success': True,
            'action': 'water_intake_logged',
            'amount_ml': amount_ml,
            'logged_at': datetime.now().isoformat(),
            'message': f'تم تسجيل شرب {amount_ml} مل من الماء'
        }
    
    def _execute_mood_log(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ تسجيل المزاج"""
        mood_score = parameters.get('mood_score', 5)  # 1-10
        notes = parameters.get('notes', '')
        
        return {
            'success': True,
            'action': 'mood_logged',
            'mood_score': mood_score,
            'notes': notes,
            'logged_at': datetime.now().isoformat(),
            'message': 'تم تسجيل الحالة المزاجية'
        }
    
    def _execute_family_health(self, parameters: Dict, user_id: str) -> Dict:
        """تنفيذ عرض صحة العائلة"""
        return {
            'success': True,
            'action': 'family_health_opened',
            'family_members_count': 4,  # محاكاة
            'health_alerts': 1,
            'message': 'تم فتح صفحة صحة العائلة'
        }
    
    def _update_button_analytics(self, button_id: str, action_type: str, success: bool):
        """تحديث إحصائيات الزر"""
        if button_id not in self.button_analytics:
            self.button_analytics[button_id] = {
                'total_uses': 0,
                'successful_uses': 0,
                'action_types': {},
                'last_used': None
            }
        
        analytics = self.button_analytics[button_id]
        analytics['total_uses'] += 1
        if success:
            analytics['successful_uses'] += 1
        
        if action_type not in analytics['action_types']:
            analytics['action_types'][action_type] = 0
        analytics['action_types'][action_type] += 1
        
        analytics['last_used'] = datetime.now()
    
    def _update_button_last_used(self, button_id: str, user_id: str):
        """تحديث آخر استخدام للزر"""
        # في التطبيق الحقيقي، سيتم تحديث قاعدة البيانات
        pass
    
    def _update_context_history(self, user_id: str, context: str, timestamp: datetime):
        """تحديث تاريخ السياق"""
        if user_id not in self.context_history:
            self.context_history[user_id] = []
        
        self.context_history[user_id].append({
            'context': context,
            'timestamp': timestamp
        })
        
        # الحفاظ على آخر 100 سياق
        if len(self.context_history[user_id]) > 100:
            self.context_history[user_id] = self.context_history[user_id][-100:]
    
    def _analyze_button_usage(self, actions: List[ButtonAction]) -> Dict:
        """تحليل استخدام الأزرار"""
        if not actions:
            return {}
        
        # تحليل أنواع الإجراءات
        action_counts = {}
        for action in actions:
            action_type = action.action_type
            if action_type not in action_counts:
                action_counts[action_type] = 0
            action_counts[action_type] += 1
        
        # الإجراءات الأكثر استخداماً
        most_used = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_actions': len(actions),
            'unique_action_types': len(action_counts),
            'most_used_actions': most_used[:5],
            'average_actions_per_day': len(actions) / 30  # تقدير
        }
    
    def _get_most_used_buttons(self, actions: List[ButtonAction]) -> List[Dict]:
        """الحصول على الأزرار الأكثر استخداماً"""
        button_counts = {}
        for action in actions:
            button_id = action.button_id
            if button_id not in button_counts:
                button_counts[button_id] = 0
            button_counts[button_id] += 1
        
        most_used = sorted(button_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'button_id': button_id, 'usage_count': count}
            for button_id, count in most_used[:5]
        ]
    
    def _analyze_usage_patterns(self, actions: List[ButtonAction]) -> Dict:
        """تحليل أنماط الاستخدام"""
        if not actions:
            return {}
        
        # تحليل الاستخدام حسب الساعة
        hourly_usage = [0] * 24
        for action in actions:
            hour = action.executed_at.hour
            hourly_usage[hour] += 1
        
        # أكثر الساعات استخداماً
        peak_hours = []
        max_usage = max(hourly_usage)
        for hour, usage in enumerate(hourly_usage):
            if usage == max_usage:
                peak_hours.append(hour)
        
        return {
            'hourly_usage': hourly_usage,
            'peak_hours': peak_hours,
            'most_active_hour': peak_hours[0] if peak_hours else 0
        }
    
    def _calculate_success_rate(self, actions: List[ButtonAction]) -> float:
        """حساب معدل النجاح"""
        if not actions:
            return 0.0
        
        successful_actions = sum(1 for action in actions if action.success)
        return (successful_actions / len(actions)) * 100
    
    def _generate_usage_recommendations(self, usage_stats: Dict) -> List[str]:
        """إنشاء توصيات الاستخدام"""
        recommendations = []
        
        total_actions = usage_stats.get('total_actions', 0)
        
        if total_actions < 10:
            recommendations.append('جرب استخدام الأزرار العائمة أكثر لتسهيل الوصول للميزات')
        
        most_used = usage_stats.get('most_used_actions', [])
        if most_used:
            top_action = most_used[0][0]
            recommendations.append(f'أكثر إجراءاتك استخداماً هو {top_action}، يمكنك تخصيص زر سريع له')
        
        return recommendations
    
    # دوال الاقتراحات الذكية
    def _get_activity_based_suggestions(self, recent_activity: List[Dict]) -> List[Dict]:
        """اقتراحات حسب النشاط الأخير"""
        suggestions = []
        
        for activity in recent_activity:
            activity_type = activity.get('type')
            
            if activity_type == 'symptom_reported':
                suggestions.append({
                    'button_type': ButtonType.SYMPTOM_CHECKER.value,
                    'reason': 'لديك أعراض مسجلة حديثاً',
                    'relevance_score': 0.9
                })
            elif activity_type == 'medication_missed':
                suggestions.append({
                    'button_type': ButtonType.MEDICATION_REMINDER.value,
                    'reason': 'فاتك تناول دواء مؤخراً',
                    'relevance_score': 0.8
                })
            elif activity_type == 'appointment_scheduled':
                suggestions.append({
                    'button_type': ButtonType.QUICK_APPOINTMENT.value,
                    'reason': 'لديك مواعيد طبية قادمة',
                    'relevance_score': 0.7
                })
        
        return suggestions
    
    def _get_health_based_suggestions(self, user_profile: Dict) -> List[Dict]:
        """اقتراحات حسب الملف الصحي"""
        suggestions = []
        
        medical_conditions = user_profile.get('medical_conditions', {})
        
        if medical_conditions.get('hypertension'):
            suggestions.append({
                'button_type': ButtonType.BLOOD_PRESSURE.value,
                'reason': 'لديك ضغط دم مرتفع، راقب قراءاتك',
                'relevance_score': 0.8
            })
        
        if medical_conditions.get('diabetes'):
            suggestions.append({
                'button_type': ButtonType.BLOOD_SUGAR.value,
                'reason': 'لديك سكري، راقب مستوى السكر',
                'relevance_score': 0.8
            })
        
        if user_profile.get('age', 0) > 60:
            suggestions.append({
                'button_type': ButtonType.EMERGENCY.value,
                'reason': 'زر الطوارئ مهم لكبار السن',
                'relevance_score': 0.7
            })
        
        return suggestions
    
    def _get_time_based_suggestions(self, user_profile: Dict) -> List[Dict]:
        """اقتراحات حسب الوقت"""
        suggestions = []
        current_hour = datetime.now().hour
        
        if 6 <= current_hour <= 10:
            suggestions.append({
                'button_type': ButtonType.MOOD_TRACKER.value,
                'reason': 'وقت مناسب لتسجيل مزاجك الصباحي',
                'relevance_score': 0.6
            })
        
        if 12 <= current_hour <= 14:
            suggestions.append({
                'button_type': ButtonType.WATER_REMINDER.value,
                'reason': 'تذكر شرب الماء في منتصف اليوم',
                'relevance_score': 0.5
            })
        
        if 18 <= current_hour <= 22:
            suggestions.append({
                'button_type': ButtonType.MEDICATION_REMINDER.value,
                'reason': 'وقت أدوية المساء',
                'relevance_score': 0.7
            })
        
        return suggestions
    
    def _get_context_based_suggestions(self, current_context: str, user_profile: Dict) -> List[Dict]:
        """اقتراحات حسب السياق"""
        suggestions = []
        
        if current_context == ButtonContext.HOME.value:
            suggestions.append({
                'button_type': ButtonType.AI_ASSISTANT.value,
                'reason': 'المساعد الذكي متاح للاستشارات',
                'relevance_score': 0.6
            })
        
        if current_context == ButtonContext.FAMILY.value:
            suggestions.append({
                'button_type': ButtonType.FAMILY_HEALTH.value,
                'reason': 'راجع صحة أفراد عائلتك',
                'relevance_score': 0.8
            })
        
        if current_context == ButtonContext.EMERGENCY.value:
            suggestions.append({
                'button_type': ButtonType.EMERGENCY.value,
                'reason': 'زر الطوارئ جاهز للاستخدام',
                'relevance_score': 0.9
            })
        
        return suggestions

