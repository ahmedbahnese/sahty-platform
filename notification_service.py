"""
خدمة التنبيهات والإشعارات المتقدمة
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import schedule
import time
from threading import Thread

class NotificationService:
    def __init__(self):
        """تهيئة خدمة التنبيهات"""
        # إعدادات البريد الإلكتروني
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_ADDRESS', 'sahty@example.com'),
            'password': os.getenv('EMAIL_PASSWORD', 'your_password'),
            'sender_name': 'صحتك في أمان'
        }
        
        # إعدادات الرسائل النصية
        self.sms_config = {
            'api_key': os.getenv('SMS_API_KEY', 'your_api_key'),
            'sender_id': os.getenv('SMS_SENDER_ID', 'SAHTY'),
            'base_url': os.getenv('SMS_BASE_URL', 'https://api.sms.com/')
        }
        
        # إعدادات الإشعارات المدفوعة (Push Notifications)
        self.push_config = {
            'firebase_key': os.getenv('FIREBASE_SERVER_KEY', 'your_firebase_key'),
            'fcm_url': 'https://fcm.googleapis.com/fcm/send'
        }
        
        # إعدادات WhatsApp Business API
        self.whatsapp_config = {
            'api_key': os.getenv('WHATSAPP_API_KEY', 'your_api_key'),
            'phone_number_id': os.getenv('WHATSAPP_PHONE_ID', 'your_phone_id'),
            'base_url': 'https://graph.facebook.com/v17.0/'
        }
        
        # قوالب الرسائل
        self.message_templates = {
            'appointment_reminder': {
                'title': 'تذكير بالموعد',
                'body': 'لديك موعد مع {doctor_name} في {appointment_time}',
                'type': 'reminder'
            },
            'medication_reminder': {
                'title': 'تذكير بالدواء',
                'body': 'حان وقت تناول {medication_name} - الجرعة: {dosage}',
                'type': 'medication'
            },
            'test_result': {
                'title': 'نتائج الفحص جاهزة',
                'body': 'نتائج فحص {test_name} أصبحت متاحة. يرجى مراجعة التطبيق.',
                'type': 'result'
            },
            'emergency_alert': {
                'title': 'تنبيه طوارئ',
                'body': 'تم تسجيل حالة طوارئ. يرجى التواصل فوراً.',
                'type': 'emergency'
            },
            'health_tip': {
                'title': 'نصيحة صحية',
                'body': '{tip_content}',
                'type': 'tip'
            }
        }
    
    def send_notification(self, user_id: str, notification_type: str, 
                         channels: List[str], data: Dict = None, 
                         schedule_time: datetime = None) -> Dict:
        """
        إرسال إشعار متعدد القنوات
        
        Args:
            user_id: معرف المستخدم
            notification_type: نوع الإشعار
            channels: قنوات الإرسال (email, sms, push, whatsapp)
            data: بيانات الإشعار
            schedule_time: وقت الإرسال المجدول
            
        Returns:
            Dict: نتيجة الإرسال
        """
        try:
            if notification_type not in self.message_templates:
                raise Exception(f"نوع إشعار غير مدعوم: {notification_type}")
            
            template = self.message_templates[notification_type]
            
            # تخصيص الرسالة
            message_data = self._customize_message(template, data or {})
            
            # إذا كان مجدولاً، حفظه للإرسال لاحقاً
            if schedule_time:
                return self._schedule_notification(
                    user_id, notification_type, channels, message_data, schedule_time
                )
            
            # إرسال فوري
            results = {}
            for channel in channels:
                if channel == 'email':
                    results['email'] = self._send_email(user_id, message_data)
                elif channel == 'sms':
                    results['sms'] = self._send_sms(user_id, message_data)
                elif channel == 'push':
                    results['push'] = self._send_push_notification(user_id, message_data)
                elif channel == 'whatsapp':
                    results['whatsapp'] = self._send_whatsapp(user_id, message_data)
            
            # حفظ سجل الإشعار
            notification_log = {
                'user_id': user_id,
                'type': notification_type,
                'channels': channels,
                'message': message_data,
                'results': results,
                'sent_at': datetime.now().isoformat(),
                'status': 'sent'
            }
            
            return {
                'success': True,
                'notification_log': notification_log,
                'results': results
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال الإشعار: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _customize_message(self, template: Dict, data: Dict) -> Dict:
        """تخصيص الرسالة بناءً على البيانات"""
        customized = template.copy()
        
        # استبدال المتغيرات في العنوان والمحتوى
        for key in ['title', 'body']:
            if key in customized:
                message = customized[key]
                for data_key, data_value in data.items():
                    placeholder = f"{{{data_key}}}"
                    if placeholder in message:
                        message = message.replace(placeholder, str(data_value))
                customized[key] = message
        
        return customized
    
    def _send_email(self, user_id: str, message_data: Dict) -> Dict:
        """إرسال بريد إلكتروني"""
        try:
            # في التطبيق الحقيقي، سيتم الحصول على بريد المستخدم من قاعدة البيانات
            user_email = f"user_{user_id}@example.com"  # محاكاة
            
            # إنشاء الرسالة
            msg = MIMEMultipart()
            msg['From'] = f"{self.email_config['sender_name']} <{self.email_config['email']}>"
            msg['To'] = user_email
            msg['Subject'] = message_data['title']
            
            # محتوى HTML
            html_body = f"""
            <html>
                <body dir="rtl" style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                   color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                            <h1 style="margin: 0; text-align: center;">صحتك في أمان</h1>
                        </div>
                        <div style="background: white; padding: 30px; border: 1px solid #ddd; 
                                   border-radius: 0 0 10px 10px;">
                            <h2 style="color: #333; margin-bottom: 20px;">{message_data['title']}</h2>
                            <p style="color: #666; line-height: 1.6; font-size: 16px;">
                                {message_data['body']}
                            </p>
                            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                                <p style="color: #999; font-size: 14px; text-align: center;">
                                    هذه رسالة تلقائية من تطبيق صحتك في أمان
                                </p>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # إرسال الرسالة (محاكاة)
            # في التطبيق الحقيقي:
            # server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            # server.starttls()
            # server.login(self.email_config['email'], self.email_config['password'])
            # server.send_message(msg)
            # server.quit()
            
            return {
                'success': True,
                'message': 'تم إرسال البريد الإلكتروني بنجاح',
                'recipient': user_email
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_sms(self, user_id: str, message_data: Dict) -> Dict:
        """إرسال رسالة نصية"""
        try:
            # في التطبيق الحقيقي، سيتم الحصول على رقم المستخدم من قاعدة البيانات
            user_phone = f"+20100000{user_id}"  # محاكاة
            
            # إعداد الرسالة
            sms_text = f"{message_data['title']}\n{message_data['body']}"
            
            # إرسال الرسالة (محاكاة)
            # في التطبيق الحقيقي:
            # response = requests.post(
            #     f"{self.sms_config['base_url']}send",
            #     json={
            #         'api_key': self.sms_config['api_key'],
            #         'sender': self.sms_config['sender_id'],
            #         'to': user_phone,
            #         'message': sms_text
            #     }
            # )
            
            return {
                'success': True,
                'message': 'تم إرسال الرسالة النصية بنجاح',
                'recipient': user_phone
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_push_notification(self, user_id: str, message_data: Dict) -> Dict:
        """إرسال إشعار مدفوع"""
        try:
            # في التطبيق الحقيقي، سيتم الحصول على FCM token من قاعدة البيانات
            fcm_token = f"fcm_token_{user_id}"  # محاكاة
            
            # إعداد الإشعار
            notification_payload = {
                'to': fcm_token,
                'notification': {
                    'title': message_data['title'],
                    'body': message_data['body'],
                    'icon': 'ic_notification',
                    'sound': 'default'
                },
                'data': {
                    'type': message_data['type'],
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # إرسال الإشعار (محاكاة)
            # في التطبيق الحقيقي:
            # headers = {
            #     'Authorization': f"key={self.push_config['firebase_key']}",
            #     'Content-Type': 'application/json'
            # }
            # response = requests.post(
            #     self.push_config['fcm_url'],
            #     json=notification_payload,
            #     headers=headers
            # )
            
            return {
                'success': True,
                'message': 'تم إرسال الإشعار المدفوع بنجاح',
                'recipient': fcm_token
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_whatsapp(self, user_id: str, message_data: Dict) -> Dict:
        """إرسال رسالة واتساب"""
        try:
            # في التطبيق الحقيقي، سيتم الحصول على رقم المستخدم من قاعدة البيانات
            user_phone = f"20100000{user_id}"  # محاكاة
            
            # إعداد الرسالة
            whatsapp_message = {
                'messaging_product': 'whatsapp',
                'to': user_phone,
                'type': 'text',
                'text': {
                    'body': f"*{message_data['title']}*\n\n{message_data['body']}\n\n_صحتك في أمان_"
                }
            }
            
            # إرسال الرسالة (محاكاة)
            # في التطبيق الحقيقي:
            # headers = {
            #     'Authorization': f"Bearer {self.whatsapp_config['api_key']}",
            #     'Content-Type': 'application/json'
            # }
            # response = requests.post(
            #     f"{self.whatsapp_config['base_url']}{self.whatsapp_config['phone_number_id']}/messages",
            #     json=whatsapp_message,
            #     headers=headers
            # )
            
            return {
                'success': True,
                'message': 'تم إرسال رسالة واتساب بنجاح',
                'recipient': user_phone
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _schedule_notification(self, user_id: str, notification_type: str,
                             channels: List[str], message_data: Dict,
                             schedule_time: datetime) -> Dict:
        """جدولة إشعار للإرسال لاحقاً"""
        try:
            scheduled_notification = {
                'id': f"scheduled_{user_id}_{int(schedule_time.timestamp())}",
                'user_id': user_id,
                'type': notification_type,
                'channels': channels,
                'message': message_data,
                'schedule_time': schedule_time.isoformat(),
                'status': 'scheduled',
                'created_at': datetime.now().isoformat()
            }
            
            # في التطبيق الحقيقي، سيتم حفظ الإشعار في قاعدة البيانات
            # وسيتم تشغيل مهمة مجدولة للإرسال
            
            return {
                'success': True,
                'scheduled_notification': scheduled_notification,
                'message': f'تم جدولة الإشعار للإرسال في {schedule_time.strftime("%Y-%m-%d %H:%M")}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_medication_reminders(self, user_id: str, medication_schedule: Dict) -> Dict:
        """إنشاء تذكيرات الأدوية"""
        try:
            reminders = []
            
            for medication in medication_schedule.get('medications', []):
                med_name = medication['name']
                dosage = medication['dosage']
                times = medication['times']  # قائمة أوقات التناول
                
                for time_str in times:
                    # تحويل الوقت إلى datetime
                    time_obj = datetime.strptime(time_str, '%H:%M').time()
                    
                    # إنشاء تذكير يومي
                    reminder_data = {
                        'medication_name': med_name,
                        'dosage': dosage,
                        'time': time_str
                    }
                    
                    reminder = self._schedule_notification(
                        user_id=user_id,
                        notification_type='medication_reminder',
                        channels=['push', 'sms'],
                        message_data=reminder_data,
                        schedule_time=datetime.combine(datetime.now().date(), time_obj)
                    )
                    
                    reminders.append(reminder)
            
            return {
                'success': True,
                'reminders_created': len(reminders),
                'reminders': reminders
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_appointment_reminder(self, user_id: str, appointment_details: Dict,
                                reminder_times: List[int] = [24, 2]) -> Dict:
        """إرسال تذكيرات المواعيد"""
        try:
            appointment_time = datetime.fromisoformat(appointment_details['appointment_time'])
            reminders_sent = []
            
            for hours_before in reminder_times:
                reminder_time = appointment_time - timedelta(hours=hours_before)
                
                # تخطي التذكيرات في الماضي
                if reminder_time <= datetime.now():
                    continue
                
                reminder_data = {
                    'doctor_name': appointment_details['doctor_name'],
                    'appointment_time': appointment_time.strftime('%Y-%m-%d %H:%M'),
                    'location': appointment_details.get('location', ''),
                    'hours_before': hours_before
                }
                
                reminder = self._schedule_notification(
                    user_id=user_id,
                    notification_type='appointment_reminder',
                    channels=['push', 'email'],
                    message_data=reminder_data,
                    schedule_time=reminder_time
                )
                
                reminders_sent.append(reminder)
            
            return {
                'success': True,
                'reminders_scheduled': len(reminders_sent),
                'reminders': reminders_sent
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_health_tips(self, user_segments: List[str], tip_content: str) -> Dict:
        """إرسال نصائح صحية لمجموعات المستخدمين"""
        try:
            # في التطبيق الحقيقي، سيتم الحصول على المستخدمين من قاعدة البيانات
            # بناءً على التصنيفات المحددة
            
            results = []
            
            # محاكاة إرسال للمستخدمين
            for segment in user_segments:
                # الحصول على مستخدمي هذا التصنيف
                segment_users = self._get_users_by_segment(segment)
                
                for user_id in segment_users:
                    result = self.send_notification(
                        user_id=user_id,
                        notification_type='health_tip',
                        channels=['push'],
                        data={'tip_content': tip_content}
                    )
                    results.append(result)
            
            return {
                'success': True,
                'total_sent': len(results),
                'segments': user_segments,
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_users_by_segment(self, segment: str) -> List[str]:
        """الحصول على المستخدمين حسب التصنيف"""
        # محاكاة تصنيفات المستخدمين
        segments = {
            'diabetes_patients': ['user_1', 'user_5', 'user_12'],
            'heart_patients': ['user_2', 'user_8', 'user_15'],
            'pregnant_women': ['user_3', 'user_9'],
            'elderly': ['user_4', 'user_10', 'user_16'],
            'all_users': ['user_1', 'user_2', 'user_3', 'user_4', 'user_5']
        }
        
        return segments.get(segment, [])
    
    def get_notification_preferences(self, user_id: str) -> Dict:
        """الحصول على تفضيلات الإشعارات للمستخدم"""
        # في التطبيق الحقيقي، سيتم الحصول على التفضيلات من قاعدة البيانات
        default_preferences = {
            'email_enabled': True,
            'sms_enabled': True,
            'push_enabled': True,
            'whatsapp_enabled': False,
            'medication_reminders': True,
            'appointment_reminders': True,
            'health_tips': True,
            'emergency_alerts': True,
            'quiet_hours': {
                'enabled': True,
                'start_time': '22:00',
                'end_time': '07:00'
            }
        }
        
        return default_preferences
    
    def update_notification_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """تحديث تفضيلات الإشعارات"""
        try:
            # في التطبيق الحقيقي، سيتم حفظ التفضيلات في قاعدة البيانات
            
            return {
                'success': True,
                'message': 'تم تحديث تفضيلات الإشعارات بنجاح',
                'preferences': preferences
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

