"""
المركز الشخصي الشامل
لوحة تحكم شخصية شاملة لكل مستخدم تجمع جميع معلوماته وأنشطته في مكان واحد
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum
import base64

class DashboardWidget(Enum):
    HEALTH_SUMMARY = "ملخص الصحة"
    APPOINTMENTS = "المواعيد"
    MEDICATIONS = "الأدوية"
    VITAL_SIGNS = "العلامات الحيوية"
    NOTIFICATIONS = "الإشعارات"
    QUICK_ACTIONS = "الإجراءات السريعة"
    HEALTH_GOALS = "الأهداف الصحية"
    RECENT_ACTIVITY = "النشاط الأخير"
    FAMILY_HEALTH = "صحة العائلة"
    HEALTH_TIPS = "نصائح صحية"

class WidgetSize(Enum):
    SMALL = "صغير"
    MEDIUM = "متوسط"
    LARGE = "كبير"
    FULL_WIDTH = "عرض كامل"

class NotificationPriority(Enum):
    LOW = "منخفضة"
    MEDIUM = "متوسطة"
    HIGH = "عالية"
    URGENT = "عاجلة"

@dataclass
class PersonalWidget:
    widget_id: str
    widget_type: str
    title: str
    size: str
    position: Dict  # {row: int, col: int}
    is_visible: bool
    settings: Dict
    data_source: str
    refresh_interval: int  # بالثواني
    last_updated: datetime

@dataclass
class HealthGoal:
    goal_id: str
    title: str
    description: str
    target_value: float
    current_value: float
    unit: str
    target_date: datetime
    category: str  # وزن، ضغط، سكر، نشاط، إلخ
    progress_percentage: float
    is_achieved: bool
    milestones: List[Dict]
    created_at: datetime

@dataclass
class PersonalNotification:
    notification_id: str
    title: str
    message: str
    priority: str
    category: str
    is_read: bool
    action_required: bool
    action_url: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict

@dataclass
class QuickAction:
    action_id: str
    title: str
    description: str
    icon: str
    action_type: str  # navigate, api_call, modal, external
    action_data: Dict
    is_enabled: bool
    usage_count: int
    last_used: Optional[datetime]

@dataclass
class PersonalDashboard:
    user_id: str
    dashboard_name: str
    widgets: List[PersonalWidget]
    layout_settings: Dict
    theme_settings: Dict
    created_at: datetime
    updated_at: datetime

class PersonalCenterService:
    def __init__(self):
        """تهيئة خدمة المركز الشخصي"""
        
        # إعدادات الخدمة
        self.service_settings = {
            'max_widgets_per_dashboard': 20,
            'max_dashboards_per_user': 5,
            'default_refresh_interval': 300,  # 5 دقائق
            'max_notifications': 100,
            'notification_retention_days': 30,
            'max_quick_actions': 15,
            'auto_save_interval': 60  # ثانية
        }
        
        # قوالب الويدجت المتاحة
        self.widget_templates = {
            'health_summary': {
                'title': 'ملخص الصحة',
                'description': 'نظرة عامة على حالتك الصحية',
                'default_size': WidgetSize.LARGE.value,
                'data_sources': ['vital_signs', 'medications', 'appointments'],
                'settings': {
                    'show_trends': True,
                    'time_period': '30_days',
                    'include_family': False
                }
            },
            'upcoming_appointments': {
                'title': 'المواعيد القادمة',
                'description': 'مواعيدك الطبية القادمة',
                'default_size': WidgetSize.MEDIUM.value,
                'data_sources': ['appointments'],
                'settings': {
                    'days_ahead': 7,
                    'show_location': True,
                    'show_preparation': True
                }
            },
            'medication_reminders': {
                'title': 'تذكيرات الأدوية',
                'description': 'أدويتك اليومية والتذكيرات',
                'default_size': WidgetSize.MEDIUM.value,
                'data_sources': ['medications'],
                'settings': {
                    'show_next_dose': True,
                    'show_adherence': True,
                    'reminder_sound': True
                }
            },
            'vital_signs_chart': {
                'title': 'مخطط العلامات الحيوية',
                'description': 'تتبع العلامات الحيوية بالرسوم البيانية',
                'default_size': WidgetSize.LARGE.value,
                'data_sources': ['vital_signs'],
                'settings': {
                    'chart_type': 'line',
                    'time_period': '7_days',
                    'metrics': ['blood_pressure', 'heart_rate', 'weight']
                }
            },
            'health_goals_progress': {
                'title': 'تقدم الأهداف الصحية',
                'description': 'متابعة تحقيق أهدافك الصحية',
                'default_size': WidgetSize.MEDIUM.value,
                'data_sources': ['health_goals'],
                'settings': {
                    'show_all_goals': False,
                    'max_goals_displayed': 3,
                    'show_progress_bar': True
                }
            },
            'family_health_overview': {
                'title': 'نظرة على صحة العائلة',
                'description': 'ملخص صحة أفراد العائلة',
                'default_size': WidgetSize.LARGE.value,
                'data_sources': ['family_health'],
                'settings': {
                    'include_children': True,
                    'include_elderly': True,
                    'show_alerts_only': False
                }
            },
            'quick_actions_panel': {
                'title': 'الإجراءات السريعة',
                'description': 'أزرار للإجراءات الأكثر استخداماً',
                'default_size': WidgetSize.SMALL.value,
                'data_sources': ['user_preferences'],
                'settings': {
                    'max_actions': 6,
                    'auto_arrange': True,
                    'show_usage_count': False
                }
            },
            'health_tips_feed': {
                'title': 'نصائح صحية',
                'description': 'نصائح صحية مخصصة لك',
                'default_size': WidgetSize.MEDIUM.value,
                'data_sources': ['ai_recommendations'],
                'settings': {
                    'personalized': True,
                    'update_frequency': 'daily',
                    'categories': ['nutrition', 'exercise', 'mental_health']
                }
            },
            'recent_activity_feed': {
                'title': 'النشاط الأخير',
                'description': 'آخر أنشطتك في النظام',
                'default_size': WidgetSize.MEDIUM.value,
                'data_sources': ['activity_log'],
                'settings': {
                    'max_items': 10,
                    'time_period': '7_days',
                    'include_family_activity': False
                }
            },
            'notifications_center': {
                'title': 'مركز الإشعارات',
                'description': 'جميع إشعاراتك في مكان واحد',
                'default_size': WidgetSize.MEDIUM.value,
                'data_sources': ['notifications'],
                'settings': {
                    'show_unread_only': True,
                    'group_by_category': True,
                    'max_notifications': 15
                }
            }
        }
        
        # الإجراءات السريعة المتاحة
        self.available_quick_actions = {
            'book_appointment': {
                'title': 'حجز موعد',
                'description': 'احجز موعد مع طبيب',
                'icon': '📅',
                'action_type': 'navigate',
                'action_data': {'route': '/appointments/book'},
                'category': 'appointments'
            },
            'emergency_call': {
                'title': 'طوارئ',
                'description': 'اتصال طوارئ سريع',
                'icon': '🚨',
                'action_type': 'modal',
                'action_data': {'modal': 'emergency_contact'},
                'category': 'emergency'
            },
            'medication_reminder': {
                'title': 'تذكير دواء',
                'description': 'تسجيل تناول دواء',
                'icon': '💊',
                'action_type': 'api_call',
                'action_data': {'endpoint': '/medications/take'},
                'category': 'medications'
            },
            'vital_signs_entry': {
                'title': 'تسجيل علامات حيوية',
                'description': 'سجل قياساتك الحيوية',
                'icon': '📊',
                'action_type': 'navigate',
                'action_data': {'route': '/vital-signs/entry'},
                'category': 'monitoring'
            },
            'ai_consultation': {
                'title': 'استشارة ذكية',
                'description': 'اسأل المساعد الذكي',
                'icon': '🤖',
                'action_type': 'navigate',
                'action_data': {'route': '/ai-assistant'},
                'category': 'consultation'
            },
            'find_doctor': {
                'title': 'البحث عن طبيب',
                'description': 'ابحث عن طبيب مناسب',
                'icon': '👨‍⚕️',
                'action_type': 'navigate',
                'action_data': {'route': '/doctors/search'},
                'category': 'doctors'
            },
            'health_report': {
                'title': 'تقرير صحي',
                'description': 'احصل على تقرير صحي شامل',
                'icon': '📋',
                'action_type': 'api_call',
                'action_data': {'endpoint': '/reports/generate'},
                'category': 'reports'
            },
            'family_invite': {
                'title': 'دعوة عائلة',
                'description': 'ادع فرد من العائلة',
                'icon': '👨‍👩‍👧‍👦',
                'action_type': 'modal',
                'action_data': {'modal': 'family_invite'},
                'category': 'family'
            },
            'symptom_checker': {
                'title': 'فحص الأعراض',
                'description': 'تحليل الأعراض بالذكاء الاصطناعي',
                'icon': '🔍',
                'action_type': 'navigate',
                'action_data': {'route': '/symptom-checker'},
                'category': 'diagnosis'
            },
            'prescription_refill': {
                'title': 'تجديد وصفة',
                'description': 'اطلب تجديد وصفة طبية',
                'icon': '📝',
                'action_type': 'navigate',
                'action_data': {'route': '/prescriptions/refill'},
                'category': 'medications'
            }
        }
        
        # قوالب الأهداف الصحية
        self.health_goal_templates = {
            'weight_loss': {
                'title': 'فقدان الوزن',
                'description': 'الوصول للوزن المثالي',
                'category': 'وزن',
                'unit': 'كيلو',
                'default_duration_days': 90,
                'milestones': [
                    {'percentage': 25, 'reward': 'شارة البداية القوية'},
                    {'percentage': 50, 'reward': 'شارة منتصف الطريق'},
                    {'percentage': 75, 'reward': 'شارة الإنجاز المتقدم'},
                    {'percentage': 100, 'reward': 'شارة تحقيق الهدف'}
                ]
            },
            'blood_pressure_control': {
                'title': 'التحكم في ضغط الدم',
                'description': 'الحفاظ على ضغط دم صحي',
                'category': 'ضغط الدم',
                'unit': 'mmHg',
                'default_duration_days': 60,
                'milestones': [
                    {'percentage': 30, 'reward': 'شارة الانضباط'},
                    {'percentage': 60, 'reward': 'شارة التحسن المستمر'},
                    {'percentage': 100, 'reward': 'شارة السيطرة الكاملة'}
                ]
            },
            'exercise_routine': {
                'title': 'روتين التمارين',
                'description': 'ممارسة التمارين بانتظام',
                'category': 'نشاط بدني',
                'unit': 'دقيقة/أسبوع',
                'default_duration_days': 30,
                'milestones': [
                    {'percentage': 25, 'reward': 'شارة البداية النشطة'},
                    {'percentage': 50, 'reward': 'شارة الالتزام'},
                    {'percentage': 75, 'reward': 'شارة اللياقة المتقدمة'},
                    {'percentage': 100, 'reward': 'شارة الرياضي المثابر'}
                ]
            },
            'medication_adherence': {
                'title': 'الالتزام بالأدوية',
                'description': 'تناول الأدوية في مواعيدها',
                'category': 'أدوية',
                'unit': '% التزام',
                'default_duration_days': 30,
                'milestones': [
                    {'percentage': 50, 'reward': 'شارة الانضباط الأولي'},
                    {'percentage': 80, 'reward': 'شارة الالتزام الممتاز'},
                    {'percentage': 100, 'reward': 'شارة المريض المثالي'}
                ]
            }
        }
        
        # قاعدة بيانات المراكز الشخصية (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.user_dashboards = {}
        self.user_notifications = {}
        self.user_health_goals = {}
        self.user_quick_actions = {}
        
        # إحصائيات الاستخدام
        self.usage_analytics = {}
    
    def get_personal_dashboard(self, user_id: str, dashboard_name: str = "default") -> Dict:
        """
        الحصول على لوحة التحكم الشخصية
        
        Args:
            user_id: معرف المستخدم
            dashboard_name: اسم لوحة التحكم
            
        Returns:
            Dict: بيانات لوحة التحكم
        """
        try:
            dashboard_key = f"{user_id}_{dashboard_name}"
            
            # إنشاء لوحة تحكم افتراضية إذا لم تكن موجودة
            if dashboard_key not in self.user_dashboards:
                dashboard = self._create_default_dashboard(user_id, dashboard_name)
                self.user_dashboards[dashboard_key] = dashboard
            else:
                dashboard = self.user_dashboards[dashboard_key]
            
            # تحديث بيانات الويدجت
            updated_widgets = []
            for widget in dashboard.widgets:
                widget_data = self._get_widget_data(user_id, widget)
                updated_widgets.append(widget_data)
            
            # الحصول على الإشعارات الحديثة
            notifications = self._get_user_notifications(user_id, limit=10)
            
            # الحصول على الإجراءات السريعة
            quick_actions = self._get_user_quick_actions(user_id)
            
            return {
                'success': True,
                'dashboard': {
                    'dashboard_name': dashboard.dashboard_name,
                    'widgets': updated_widgets,
                    'layout_settings': dashboard.layout_settings,
                    'theme_settings': dashboard.theme_settings,
                    'last_updated': dashboard.updated_at.isoformat()
                },
                'notifications': notifications,
                'quick_actions': quick_actions,
                'user_stats': self._get_user_stats(user_id)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على لوحة التحكم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تحميل لوحة التحكم'
            }
    
    def customize_dashboard(self, user_id: str, customization_data: Dict) -> Dict:
        """
        تخصيص لوحة التحكم
        
        Args:
            user_id: معرف المستخدم
            customization_data: بيانات التخصيص
            
        Returns:
            Dict: نتيجة التخصيص
        """
        try:
            dashboard_name = customization_data.get('dashboard_name', 'default')
            dashboard_key = f"{user_id}_{dashboard_name}"
            
            if dashboard_key not in self.user_dashboards:
                return {
                    'success': False,
                    'error': 'لوحة التحكم غير موجودة'
                }
            
            dashboard = self.user_dashboards[dashboard_key]
            
            # تحديث إعدادات التخطيط
            if 'layout_settings' in customization_data:
                dashboard.layout_settings.update(customization_data['layout_settings'])
            
            # تحديث إعدادات المظهر
            if 'theme_settings' in customization_data:
                dashboard.theme_settings.update(customization_data['theme_settings'])
            
            # تحديث الويدجت
            if 'widgets' in customization_data:
                self._update_widgets(dashboard, customization_data['widgets'])
            
            dashboard.updated_at = datetime.now()
            
            return {
                'success': True,
                'message': 'تم تحديث لوحة التحكم بنجاح',
                'dashboard': {
                    'layout_settings': dashboard.layout_settings,
                    'theme_settings': dashboard.theme_settings,
                    'widgets_count': len(dashboard.widgets)
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تخصيص لوحة التحكم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تخصيص لوحة التحكم'
            }
    
    def add_widget(self, user_id: str, widget_config: Dict) -> Dict:
        """
        إضافة ويدجت جديد
        
        Args:
            user_id: معرف المستخدم
            widget_config: إعدادات الويدجت
            
        Returns:
            Dict: نتيجة الإضافة
        """
        try:
            dashboard_name = widget_config.get('dashboard_name', 'default')
            dashboard_key = f"{user_id}_{dashboard_name}"
            
            if dashboard_key not in self.user_dashboards:
                return {
                    'success': False,
                    'error': 'لوحة التحكم غير موجودة'
                }
            
            dashboard = self.user_dashboards[dashboard_key]
            
            # التحقق من الحد الأقصى للويدجت
            if len(dashboard.widgets) >= self.service_settings['max_widgets_per_dashboard']:
                return {
                    'success': False,
                    'error': f'تم الوصول للحد الأقصى من الويدجت ({self.service_settings["max_widgets_per_dashboard"]})'
                }
            
            # إنشاء ويدجت جديد
            widget = self._create_widget(widget_config)
            dashboard.widgets.append(widget)
            dashboard.updated_at = datetime.now()
            
            return {
                'success': True,
                'message': 'تم إضافة الويدجت بنجاح',
                'widget': {
                    'widget_id': widget.widget_id,
                    'title': widget.title,
                    'type': widget.widget_type,
                    'position': widget.position
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إضافة الويدجت: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إضافة الويدجت'
            }
    
    def remove_widget(self, user_id: str, widget_id: str) -> Dict:
        """
        إزالة ويدجت
        
        Args:
            user_id: معرف المستخدم
            widget_id: معرف الويدجت
            
        Returns:
            Dict: نتيجة الإزالة
        """
        try:
            # البحث عن الويدجت في جميع لوحات التحكم
            for dashboard_key, dashboard in self.user_dashboards.items():
                if dashboard.user_id == user_id:
                    for i, widget in enumerate(dashboard.widgets):
                        if widget.widget_id == widget_id:
                            removed_widget = dashboard.widgets.pop(i)
                            dashboard.updated_at = datetime.now()
                            
                            return {
                                'success': True,
                                'message': 'تم حذف الويدجت بنجاح',
                                'removed_widget': {
                                    'widget_id': removed_widget.widget_id,
                                    'title': removed_widget.title
                                }
                            }
            
            return {
                'success': False,
                'error': 'الويدجت غير موجود'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إزالة الويدجت: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إزالة الويدجت'
            }
    
    def create_health_goal(self, user_id: str, goal_data: Dict) -> Dict:
        """
        إنشاء هدف صحي جديد
        
        Args:
            user_id: معرف المستخدم
            goal_data: بيانات الهدف
            
        Returns:
            Dict: نتيجة الإنشاء
        """
        try:
            # التحقق من صحة البيانات
            required_fields = ['title', 'target_value', 'target_date', 'category']
            for field in required_fields:
                if field not in goal_data:
                    return {
                        'success': False,
                        'error': f'الحقل {field} مطلوب'
                    }
            
            # إنشاء الهدف
            goal = HealthGoal(
                goal_id=str(uuid.uuid4()),
                title=goal_data['title'],
                description=goal_data.get('description', ''),
                target_value=float(goal_data['target_value']),
                current_value=float(goal_data.get('current_value', 0)),
                unit=goal_data.get('unit', ''),
                target_date=datetime.fromisoformat(goal_data['target_date']),
                category=goal_data['category'],
                progress_percentage=0.0,
                is_achieved=False,
                milestones=goal_data.get('milestones', []),
                created_at=datetime.now()
            )
            
            # حفظ الهدف
            if user_id not in self.user_health_goals:
                self.user_health_goals[user_id] = []
            
            self.user_health_goals[user_id].append(goal)
            
            return {
                'success': True,
                'message': 'تم إنشاء الهدف الصحي بنجاح',
                'goal': {
                    'goal_id': goal.goal_id,
                    'title': goal.title,
                    'target_value': goal.target_value,
                    'target_date': goal.target_date.isoformat(),
                    'category': goal.category
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء الهدف الصحي: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء الهدف الصحي'
            }
    
    def update_health_goal_progress(self, user_id: str, goal_id: str, new_value: float) -> Dict:
        """
        تحديث تقدم الهدف الصحي
        
        Args:
            user_id: معرف المستخدم
            goal_id: معرف الهدف
            new_value: القيمة الجديدة
            
        Returns:
            Dict: نتيجة التحديث
        """
        try:
            if user_id not in self.user_health_goals:
                return {
                    'success': False,
                    'error': 'لا توجد أهداف صحية للمستخدم'
                }
            
            # البحث عن الهدف
            goal = None
            for g in self.user_health_goals[user_id]:
                if g.goal_id == goal_id:
                    goal = g
                    break
            
            if not goal:
                return {
                    'success': False,
                    'error': 'الهدف غير موجود'
                }
            
            # تحديث القيمة والتقدم
            goal.current_value = new_value
            
            # حساب نسبة التقدم
            if goal.target_value > 0:
                if goal.category in ['weight_loss']:  # للأهداف التي تتطلب تقليل القيمة
                    initial_value = goal.target_value + (goal.target_value * 0.2)  # افتراض قيمة ابتدائية
                    goal.progress_percentage = min(100, ((initial_value - goal.current_value) / (initial_value - goal.target_value)) * 100)
                else:  # للأهداف التي تتطلب زيادة القيمة
                    goal.progress_percentage = min(100, (goal.current_value / goal.target_value) * 100)
            
            # التحقق من تحقيق الهدف
            if goal.progress_percentage >= 100:
                goal.is_achieved = True
            
            # التحقق من الإنجازات الجديدة
            new_achievements = self._check_goal_milestones(goal)
            
            return {
                'success': True,
                'message': 'تم تحديث تقدم الهدف بنجاح',
                'goal_progress': {
                    'goal_id': goal.goal_id,
                    'current_value': goal.current_value,
                    'progress_percentage': round(goal.progress_percentage, 1),
                    'is_achieved': goal.is_achieved,
                    'remaining_to_target': goal.target_value - goal.current_value
                },
                'new_achievements': new_achievements
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحديث تقدم الهدف: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تحديث تقدم الهدف'
            }
    
    def add_notification(self, user_id: str, notification_data: Dict) -> Dict:
        """
        إضافة إشعار جديد
        
        Args:
            user_id: معرف المستخدم
            notification_data: بيانات الإشعار
            
        Returns:
            Dict: نتيجة الإضافة
        """
        try:
            notification = PersonalNotification(
                notification_id=str(uuid.uuid4()),
                title=notification_data['title'],
                message=notification_data['message'],
                priority=notification_data.get('priority', NotificationPriority.MEDIUM.value),
                category=notification_data.get('category', 'general'),
                is_read=False,
                action_required=notification_data.get('action_required', False),
                action_url=notification_data.get('action_url'),
                created_at=datetime.now(),
                expires_at=datetime.fromisoformat(notification_data['expires_at']) if notification_data.get('expires_at') else None,
                metadata=notification_data.get('metadata', {})
            )
            
            # إضافة الإشعار
            if user_id not in self.user_notifications:
                self.user_notifications[user_id] = []
            
            self.user_notifications[user_id].append(notification)
            
            # تنظيف الإشعارات القديمة
            self._cleanup_old_notifications(user_id)
            
            return {
                'success': True,
                'message': 'تم إضافة الإشعار بنجاح',
                'notification_id': notification.notification_id
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إضافة الإشعار: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إضافة الإشعار'
            }
    
    def mark_notification_read(self, user_id: str, notification_id: str) -> Dict:
        """
        تمييز الإشعار كمقروء
        
        Args:
            user_id: معرف المستخدم
            notification_id: معرف الإشعار
            
        Returns:
            Dict: نتيجة التمييز
        """
        try:
            if user_id not in self.user_notifications:
                return {
                    'success': False,
                    'error': 'لا توجد إشعارات للمستخدم'
                }
            
            # البحث عن الإشعار وتمييزه كمقروء
            for notification in self.user_notifications[user_id]:
                if notification.notification_id == notification_id:
                    notification.is_read = True
                    
                    return {
                        'success': True,
                        'message': 'تم تمييز الإشعار كمقروء'
                    }
            
            return {
                'success': False,
                'error': 'الإشعار غير موجود'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تمييز الإشعار: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تمييز الإشعار'
            }
    
    def customize_quick_actions(self, user_id: str, actions_config: List[Dict]) -> Dict:
        """
        تخصيص الإجراءات السريعة
        
        Args:
            user_id: معرف المستخدم
            actions_config: إعدادات الإجراءات
            
        Returns:
            Dict: نتيجة التخصيص
        """
        try:
            if len(actions_config) > self.service_settings['max_quick_actions']:
                return {
                    'success': False,
                    'error': f'الحد الأقصى للإجراءات السريعة هو {self.service_settings["max_quick_actions"]}'
                }
            
            # إنشاء الإجراءات السريعة المخصصة
            custom_actions = []
            for action_config in actions_config:
                if action_config['action_id'] in self.available_quick_actions:
                    base_action = self.available_quick_actions[action_config['action_id']]
                    
                    custom_action = QuickAction(
                        action_id=action_config['action_id'],
                        title=action_config.get('title', base_action['title']),
                        description=action_config.get('description', base_action['description']),
                        icon=action_config.get('icon', base_action['icon']),
                        action_type=base_action['action_type'],
                        action_data=base_action['action_data'],
                        is_enabled=action_config.get('is_enabled', True),
                        usage_count=0,
                        last_used=None
                    )
                    
                    custom_actions.append(custom_action)
            
            # حفظ الإجراءات المخصصة
            self.user_quick_actions[user_id] = custom_actions
            
            return {
                'success': True,
                'message': 'تم تخصيص الإجراءات السريعة بنجاح',
                'actions_count': len(custom_actions)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تخصيص الإجراءات السريعة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تخصيص الإجراءات السريعة'
            }
    
    def execute_quick_action(self, user_id: str, action_id: str, action_data: Dict = None) -> Dict:
        """
        تنفيذ إجراء سريع
        
        Args:
            user_id: معرف المستخدم
            action_id: معرف الإجراء
            action_data: بيانات إضافية للإجراء
            
        Returns:
            Dict: نتيجة التنفيذ
        """
        try:
            # البحث عن الإجراء
            action = None
            if user_id in self.user_quick_actions:
                for a in self.user_quick_actions[user_id]:
                    if a.action_id == action_id:
                        action = a
                        break
            
            if not action:
                return {
                    'success': False,
                    'error': 'الإجراء غير موجود'
                }
            
            if not action.is_enabled:
                return {
                    'success': False,
                    'error': 'الإجراء غير مفعل'
                }
            
            # تحديث إحصائيات الاستخدام
            action.usage_count += 1
            action.last_used = datetime.now()
            
            # تنفيذ الإجراء حسب نوعه
            result = self._execute_action_by_type(action, action_data)
            
            return {
                'success': True,
                'action_result': result,
                'action_info': {
                    'title': action.title,
                    'type': action.action_type,
                    'usage_count': action.usage_count
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تنفيذ الإجراء السريع: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تنفيذ الإجراء'
            }
    
    def get_analytics_summary(self, user_id: str) -> Dict:
        """
        الحصول على ملخص التحليلات
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: ملخص التحليلات
        """
        try:
            # إحصائيات لوحة التحكم
            dashboard_stats = self._get_dashboard_analytics(user_id)
            
            # إحصائيات الأهداف الصحية
            goals_stats = self._get_goals_analytics(user_id)
            
            # إحصائيات الإشعارات
            notifications_stats = self._get_notifications_analytics(user_id)
            
            # إحصائيات الإجراءات السريعة
            actions_stats = self._get_actions_analytics(user_id)
            
            return {
                'success': True,
                'analytics': {
                    'dashboard': dashboard_stats,
                    'health_goals': goals_stats,
                    'notifications': notifications_stats,
                    'quick_actions': actions_stats,
                    'overall_engagement': self._calculate_engagement_score(user_id)
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على التحليلات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على التحليلات'
            }
    
    # الدوال المساعدة
    def _create_default_dashboard(self, user_id: str, dashboard_name: str) -> PersonalDashboard:
        """إنشاء لوحة تحكم افتراضية"""
        
        default_widgets = [
            PersonalWidget(
                widget_id=str(uuid.uuid4()),
                widget_type='health_summary',
                title='ملخص الصحة',
                size=WidgetSize.LARGE.value,
                position={'row': 0, 'col': 0},
                is_visible=True,
                settings=self.widget_templates['health_summary']['settings'].copy(),
                data_source='health_data',
                refresh_interval=300,
                last_updated=datetime.now()
            ),
            PersonalWidget(
                widget_id=str(uuid.uuid4()),
                widget_type='upcoming_appointments',
                title='المواعيد القادمة',
                size=WidgetSize.MEDIUM.value,
                position={'row': 0, 'col': 1},
                is_visible=True,
                settings=self.widget_templates['upcoming_appointments']['settings'].copy(),
                data_source='appointments',
                refresh_interval=300,
                last_updated=datetime.now()
            ),
            PersonalWidget(
                widget_id=str(uuid.uuid4()),
                widget_type='medication_reminders',
                title='تذكيرات الأدوية',
                size=WidgetSize.MEDIUM.value,
                position={'row': 1, 'col': 0},
                is_visible=True,
                settings=self.widget_templates['medication_reminders']['settings'].copy(),
                data_source='medications',
                refresh_interval=60,
                last_updated=datetime.now()
            ),
            PersonalWidget(
                widget_id=str(uuid.uuid4()),
                widget_type='quick_actions_panel',
                title='الإجراءات السريعة',
                size=WidgetSize.SMALL.value,
                position={'row': 1, 'col': 1},
                is_visible=True,
                settings=self.widget_templates['quick_actions_panel']['settings'].copy(),
                data_source='user_preferences',
                refresh_interval=3600,
                last_updated=datetime.now()
            )
        ]
        
        return PersonalDashboard(
            user_id=user_id,
            dashboard_name=dashboard_name,
            widgets=default_widgets,
            layout_settings={
                'grid_columns': 3,
                'grid_rows': 4,
                'widget_spacing': 16,
                'responsive_breakpoints': {
                    'mobile': 768,
                    'tablet': 1024,
                    'desktop': 1200
                }
            },
            theme_settings={
                'primary_color': '#2563eb',
                'secondary_color': '#64748b',
                'background_color': '#f8fafc',
                'text_color': '#1e293b',
                'border_radius': 8,
                'font_family': 'Cairo, sans-serif'
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _get_widget_data(self, user_id: str, widget: PersonalWidget) -> Dict:
        """الحصول على بيانات الويدجت"""
        
        # محاكاة بيانات الويدجت (في التطبيق الحقيقي ستأتي من مصادر البيانات الفعلية)
        widget_data = {
            'widget_id': widget.widget_id,
            'widget_type': widget.widget_type,
            'title': widget.title,
            'size': widget.size,
            'position': widget.position,
            'is_visible': widget.is_visible,
            'settings': widget.settings,
            'last_updated': widget.last_updated.isoformat(),
            'data': {}
        }
        
        # إضافة البيانات حسب نوع الويدجت
        if widget.widget_type == 'health_summary':
            widget_data['data'] = {
                'overall_health_score': 85,
                'recent_vitals': {
                    'blood_pressure': '120/80',
                    'heart_rate': 72,
                    'weight': 70.5,
                    'last_updated': '2024-01-20'
                },
                'health_trends': {
                    'improving': ['blood_pressure', 'weight'],
                    'stable': ['heart_rate'],
                    'needs_attention': []
                }
            }
        elif widget.widget_type == 'upcoming_appointments':
            widget_data['data'] = {
                'appointments': [
                    {
                        'id': '1',
                        'doctor_name': 'د. أحمد محمد',
                        'specialty': 'طب الباطنة',
                        'date': '2024-01-25',
                        'time': '10:00',
                        'location': 'عيادة النيل الطبية'
                    },
                    {
                        'id': '2',
                        'doctor_name': 'د. فاطمة علي',
                        'specialty': 'طب الأسرة',
                        'date': '2024-01-28',
                        'time': '14:30',
                        'location': 'مستشفى الشفاء'
                    }
                ],
                'total_upcoming': 2
            }
        elif widget.widget_type == 'medication_reminders':
            widget_data['data'] = {
                'next_medication': {
                    'name': 'أسبرين 100 مجم',
                    'time': '20:00',
                    'remaining_time': '2 ساعة و 30 دقيقة'
                },
                'today_medications': [
                    {'name': 'أسبرين 100 مجم', 'time': '08:00', 'taken': True},
                    {'name': 'فيتامين د', 'time': '12:00', 'taken': True},
                    {'name': 'أسبرين 100 مجم', 'time': '20:00', 'taken': False}
                ],
                'adherence_rate': 92
            }
        elif widget.widget_type == 'quick_actions_panel':
            widget_data['data'] = {
                'actions': [
                    {'id': 'book_appointment', 'title': 'حجز موعد', 'icon': '📅'},
                    {'id': 'emergency_call', 'title': 'طوارئ', 'icon': '🚨'},
                    {'id': 'medication_reminder', 'title': 'تذكير دواء', 'icon': '💊'},
                    {'id': 'vital_signs_entry', 'title': 'تسجيل علامات', 'icon': '📊'},
                    {'id': 'ai_consultation', 'title': 'استشارة ذكية', 'icon': '🤖'},
                    {'id': 'find_doctor', 'title': 'البحث عن طبيب', 'icon': '👨‍⚕️'}
                ]
            }
        
        return widget_data
    
    def _get_user_notifications(self, user_id: str, limit: int = 10) -> List[Dict]:
        """الحصول على إشعارات المستخدم"""
        
        if user_id not in self.user_notifications:
            return []
        
        notifications = self.user_notifications[user_id]
        
        # ترتيب حسب التاريخ والأولوية
        sorted_notifications = sorted(
            notifications,
            key=lambda x: (x.priority == NotificationPriority.URGENT.value, x.created_at),
            reverse=True
        )
        
        # تحويل إلى قاموس
        result = []
        for notification in sorted_notifications[:limit]:
            result.append({
                'notification_id': notification.notification_id,
                'title': notification.title,
                'message': notification.message,
                'priority': notification.priority,
                'category': notification.category,
                'is_read': notification.is_read,
                'action_required': notification.action_required,
                'action_url': notification.action_url,
                'created_at': notification.created_at.isoformat(),
                'time_ago': self._calculate_time_ago(notification.created_at)
            })
        
        return result
    
    def _get_user_quick_actions(self, user_id: str) -> List[Dict]:
        """الحصول على الإجراءات السريعة للمستخدم"""
        
        if user_id not in self.user_quick_actions:
            # إنشاء إجراءات افتراضية
            default_actions = ['book_appointment', 'emergency_call', 'medication_reminder', 
                             'vital_signs_entry', 'ai_consultation', 'find_doctor']
            
            actions = []
            for action_id in default_actions:
                if action_id in self.available_quick_actions:
                    base_action = self.available_quick_actions[action_id]
                    action = QuickAction(
                        action_id=action_id,
                        title=base_action['title'],
                        description=base_action['description'],
                        icon=base_action['icon'],
                        action_type=base_action['action_type'],
                        action_data=base_action['action_data'],
                        is_enabled=True,
                        usage_count=0,
                        last_used=None
                    )
                    actions.append(action)
            
            self.user_quick_actions[user_id] = actions
        
        actions = self.user_quick_actions[user_id]
        
        # تحويل إلى قاموس
        result = []
        for action in actions:
            if action.is_enabled:
                result.append({
                    'action_id': action.action_id,
                    'title': action.title,
                    'description': action.description,
                    'icon': action.icon,
                    'action_type': action.action_type,
                    'action_data': action.action_data,
                    'usage_count': action.usage_count,
                    'last_used': action.last_used.isoformat() if action.last_used else None
                })
        
        return result
    
    def _get_user_stats(self, user_id: str) -> Dict:
        """الحصول على إحصائيات المستخدم"""
        
        # حساب الإحصائيات
        total_notifications = len(self.user_notifications.get(user_id, []))
        unread_notifications = len([n for n in self.user_notifications.get(user_id, []) if not n.is_read])
        total_goals = len(self.user_health_goals.get(user_id, []))
        achieved_goals = len([g for g in self.user_health_goals.get(user_id, []) if g.is_achieved])
        
        return {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'total_health_goals': total_goals,
            'achieved_goals': achieved_goals,
            'goal_achievement_rate': (achieved_goals / total_goals * 100) if total_goals > 0 else 0,
            'dashboard_last_updated': datetime.now().isoformat()
        }
    
    def _create_widget(self, widget_config: Dict) -> PersonalWidget:
        """إنشاء ويدجت جديد"""
        
        widget_type = widget_config['widget_type']
        template = self.widget_templates.get(widget_type, {})
        
        return PersonalWidget(
            widget_id=str(uuid.uuid4()),
            widget_type=widget_type,
            title=widget_config.get('title', template.get('title', 'ويدجت')),
            size=widget_config.get('size', template.get('default_size', WidgetSize.MEDIUM.value)),
            position=widget_config.get('position', {'row': 0, 'col': 0}),
            is_visible=widget_config.get('is_visible', True),
            settings=widget_config.get('settings', template.get('settings', {})),
            data_source=template.get('data_sources', ['general'])[0],
            refresh_interval=widget_config.get('refresh_interval', self.service_settings['default_refresh_interval']),
            last_updated=datetime.now()
        )
    
    def _update_widgets(self, dashboard: PersonalDashboard, widgets_data: List[Dict]):
        """تحديث الويدجت"""
        
        for widget_data in widgets_data:
            widget_id = widget_data.get('widget_id')
            
            # البحث عن الويدجت
            for widget in dashboard.widgets:
                if widget.widget_id == widget_id:
                    # تحديث الخصائص
                    if 'position' in widget_data:
                        widget.position = widget_data['position']
                    if 'size' in widget_data:
                        widget.size = widget_data['size']
                    if 'is_visible' in widget_data:
                        widget.is_visible = widget_data['is_visible']
                    if 'settings' in widget_data:
                        widget.settings.update(widget_data['settings'])
                    
                    widget.last_updated = datetime.now()
                    break
    
    def _check_goal_milestones(self, goal: HealthGoal) -> List[Dict]:
        """التحقق من إنجازات الهدف"""
        
        new_achievements = []
        
        for milestone in goal.milestones:
            if goal.progress_percentage >= milestone['percentage']:
                # التحقق من عدم حصول المستخدم على هذا الإنجاز مسبقاً
                if not milestone.get('achieved', False):
                    milestone['achieved'] = True
                    milestone['achieved_at'] = datetime.now().isoformat()
                    
                    new_achievements.append({
                        'title': milestone['reward'],
                        'description': f'تم تحقيق {milestone["percentage"]}% من الهدف',
                        'goal_title': goal.title,
                        'achieved_at': milestone['achieved_at']
                    })
        
        return new_achievements
    
    def _cleanup_old_notifications(self, user_id: str):
        """تنظيف الإشعارات القديمة"""
        
        if user_id not in self.user_notifications:
            return
        
        notifications = self.user_notifications[user_id]
        retention_date = datetime.now() - timedelta(days=self.service_settings['notification_retention_days'])
        
        # إزالة الإشعارات القديمة
        self.user_notifications[user_id] = [
            n for n in notifications 
            if n.created_at > retention_date or not n.is_read
        ]
        
        # الحفاظ على الحد الأقصى للإشعارات
        if len(self.user_notifications[user_id]) > self.service_settings['max_notifications']:
            # ترتيب حسب التاريخ والاحتفاظ بالأحدث
            sorted_notifications = sorted(
                self.user_notifications[user_id],
                key=lambda x: x.created_at,
                reverse=True
            )
            self.user_notifications[user_id] = sorted_notifications[:self.service_settings['max_notifications']]
    
    def _execute_action_by_type(self, action: QuickAction, action_data: Dict = None) -> Dict:
        """تنفيذ الإجراء حسب نوعه"""
        
        if action.action_type == 'navigate':
            return {
                'type': 'navigation',
                'route': action.action_data['route'],
                'message': f'التوجه إلى {action.title}'
            }
        elif action.action_type == 'api_call':
            return {
                'type': 'api_call',
                'endpoint': action.action_data['endpoint'],
                'message': f'تم تنفيذ {action.title}',
                'data': action_data
            }
        elif action.action_type == 'modal':
            return {
                'type': 'modal',
                'modal': action.action_data['modal'],
                'message': f'فتح نافذة {action.title}'
            }
        elif action.action_type == 'external':
            return {
                'type': 'external',
                'url': action.action_data.get('url', ''),
                'message': f'فتح رابط خارجي لـ {action.title}'
            }
        else:
            return {
                'type': 'unknown',
                'message': 'نوع إجراء غير معروف'
            }
    
    def _calculate_time_ago(self, timestamp: datetime) -> str:
        """حساب الوقت المنقضي"""
        
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f'منذ {diff.days} يوم'
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f'منذ {hours} ساعة'
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f'منذ {minutes} دقيقة'
        else:
            return 'الآن'
    
    # دوال التحليلات
    def _get_dashboard_analytics(self, user_id: str) -> Dict:
        """تحليلات لوحة التحكم"""
        
        dashboards_count = len([k for k in self.user_dashboards.keys() if k.startswith(user_id)])
        
        return {
            'total_dashboards': dashboards_count,
            'total_widgets': sum(len(d.widgets) for k, d in self.user_dashboards.items() if k.startswith(user_id)),
            'most_used_widgets': ['health_summary', 'upcoming_appointments', 'medication_reminders'],
            'customization_level': 'متوسط'
        }
    
    def _get_goals_analytics(self, user_id: str) -> Dict:
        """تحليلات الأهداف الصحية"""
        
        goals = self.user_health_goals.get(user_id, [])
        
        if not goals:
            return {
                'total_goals': 0,
                'achieved_goals': 0,
                'achievement_rate': 0,
                'average_progress': 0
            }
        
        achieved = len([g for g in goals if g.is_achieved])
        avg_progress = sum(g.progress_percentage for g in goals) / len(goals)
        
        return {
            'total_goals': len(goals),
            'achieved_goals': achieved,
            'achievement_rate': (achieved / len(goals)) * 100,
            'average_progress': round(avg_progress, 1),
            'most_common_categories': ['وزن', 'نشاط بدني', 'أدوية']
        }
    
    def _get_notifications_analytics(self, user_id: str) -> Dict:
        """تحليلات الإشعارات"""
        
        notifications = self.user_notifications.get(user_id, [])
        
        if not notifications:
            return {
                'total_notifications': 0,
                'read_rate': 0,
                'response_rate': 0
            }
        
        read_count = len([n for n in notifications if n.is_read])
        
        return {
            'total_notifications': len(notifications),
            'read_rate': (read_count / len(notifications)) * 100,
            'response_rate': 85,  # محاكاة
            'most_common_categories': ['أدوية', 'مواعيد', 'نصائح صحية']
        }
    
    def _get_actions_analytics(self, user_id: str) -> Dict:
        """تحليلات الإجراءات السريعة"""
        
        actions = self.user_quick_actions.get(user_id, [])
        
        if not actions:
            return {
                'total_actions': 0,
                'total_usage': 0,
                'most_used_action': None
            }
        
        total_usage = sum(a.usage_count for a in actions)
        most_used = max(actions, key=lambda x: x.usage_count) if actions else None
        
        return {
            'total_actions': len(actions),
            'total_usage': total_usage,
            'most_used_action': most_used.title if most_used else None,
            'average_usage_per_action': total_usage / len(actions) if actions else 0
        }
    
    def _calculate_engagement_score(self, user_id: str) -> Dict:
        """حساب نقاط المشاركة"""
        
        # حساب النقاط بناءً على النشاط
        dashboard_score = len([k for k in self.user_dashboards.keys() if k.startswith(user_id)]) * 10
        goals_score = len(self.user_health_goals.get(user_id, [])) * 15
        actions_score = sum(a.usage_count for a in self.user_quick_actions.get(user_id, [])) * 2
        notifications_score = len([n for n in self.user_notifications.get(user_id, []) if n.is_read]) * 1
        
        total_score = dashboard_score + goals_score + actions_score + notifications_score
        
        # تحديد مستوى المشاركة
        if total_score >= 200:
            level = 'عالي جداً'
        elif total_score >= 150:
            level = 'عالي'
        elif total_score >= 100:
            level = 'متوسط'
        elif total_score >= 50:
            level = 'منخفض'
        else:
            level = 'منخفض جداً'
        
        return {
            'total_score': total_score,
            'level': level,
            'breakdown': {
                'dashboard_usage': dashboard_score,
                'health_goals': goals_score,
                'quick_actions': actions_score,
                'notifications_interaction': notifications_score
            }
        }

