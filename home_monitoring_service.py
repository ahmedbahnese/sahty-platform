"""
خدمة المتابعة المنزلية والرعاية الصحية عن بُعد
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class VitalSignType(Enum):
    BLOOD_PRESSURE = "ضغط الدم"
    HEART_RATE = "معدل النبض"
    TEMPERATURE = "درجة الحرارة"
    BLOOD_SUGAR = "سكر الدم"
    OXYGEN_SATURATION = "تشبع الأكسجين"
    WEIGHT = "الوزن"
    BMI = "مؤشر كتلة الجسم"

class MonitoringFrequency(Enum):
    DAILY = "يومياً"
    TWICE_DAILY = "مرتين يومياً"
    WEEKLY = "أسبوعياً"
    MONTHLY = "شهرياً"
    AS_NEEDED = "عند الحاجة"

@dataclass
class VitalSignReading:
    reading_id: str
    patient_id: str
    vital_type: str
    value: float
    unit: str
    timestamp: datetime
    device_id: Optional[str] = None
    notes: Optional[str] = None
    is_normal: bool = True
    alert_level: str = "normal"

class HomeMonitoringService:
    def __init__(self):
        """تهيئة خدمة المتابعة المنزلية"""
        
        # المعايير الطبيعية للعلامات الحيوية
        self.normal_ranges = {
            VitalSignType.BLOOD_PRESSURE.value: {
                'systolic': {'min': 90, 'max': 140, 'unit': 'mmHg'},
                'diastolic': {'min': 60, 'max': 90, 'unit': 'mmHg'}
            },
            VitalSignType.HEART_RATE.value: {
                'adult': {'min': 60, 'max': 100, 'unit': 'bpm'},
                'elderly': {'min': 50, 'max': 90, 'unit': 'bpm'}
            },
            VitalSignType.TEMPERATURE.value: {
                'normal': {'min': 36.1, 'max': 37.2, 'unit': '°C'}
            },
            VitalSignType.BLOOD_SUGAR.value: {
                'fasting': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
                'post_meal': {'min': 70, 'max': 140, 'unit': 'mg/dL'}
            },
            VitalSignType.OXYGEN_SATURATION.value: {
                'normal': {'min': 95, 'max': 100, 'unit': '%'}
            },
            VitalSignType.WEIGHT.value: {
                'varies': True  # يعتمد على الشخص
            }
        }
        
        # الأجهزة المتوافقة
        self.compatible_devices = [
            {
                'device_id': 'omron_bp_monitor',
                'name': 'جهاز قياس ضغط الدم أومرون',
                'type': 'blood_pressure',
                'manufacturer': 'Omron',
                'model': 'HEM-7120',
                'connectivity': ['bluetooth', 'wifi'],
                'supported_vitals': ['blood_pressure', 'heart_rate']
            },
            {
                'device_id': 'accu_chek_glucose',
                'name': 'جهاز قياس السكر أكيو تشيك',
                'type': 'glucose_meter',
                'manufacturer': 'Roche',
                'model': 'Accu-Chek Guide',
                'connectivity': ['bluetooth'],
                'supported_vitals': ['blood_sugar']
            },
            {
                'device_id': 'xiaomi_scale',
                'name': 'ميزان ذكي شاومي',
                'type': 'smart_scale',
                'manufacturer': 'Xiaomi',
                'model': 'Mi Body Composition Scale 2',
                'connectivity': ['bluetooth', 'wifi'],
                'supported_vitals': ['weight', 'bmi', 'body_fat']
            },
            {
                'device_id': 'pulse_oximeter',
                'name': 'جهاز قياس الأكسجين',
                'type': 'pulse_oximeter',
                'manufacturer': 'Generic',
                'model': 'PO-100',
                'connectivity': ['bluetooth'],
                'supported_vitals': ['oxygen_saturation', 'heart_rate']
            }
        ]
    
    def create_monitoring_plan(self, patient_id: str, condition: str, 
                             vital_signs: List[str], frequency: str) -> Dict:
        """
        إنشاء خطة متابعة منزلية
        
        Args:
            patient_id: معرف المريض
            condition: الحالة المرضية
            vital_signs: العلامات الحيوية المطلوب متابعتها
            frequency: تكرار القياس
            
        Returns:
            Dict: خطة المتابعة
        """
        try:
            plan_id = str(uuid.uuid4())
            
            # إنشاء جدول القياسات
            measurement_schedule = self._create_measurement_schedule(
                vital_signs, frequency
            )
            
            # تحديد الأجهزة المطلوبة
            required_devices = self._get_required_devices(vital_signs)
            
            # إنشاء خطة المتابعة
            monitoring_plan = {
                'plan_id': plan_id,
                'patient_id': patient_id,
                'condition': condition,
                'vital_signs': vital_signs,
                'frequency': frequency,
                'measurement_schedule': measurement_schedule,
                'required_devices': required_devices,
                'start_date': datetime.now().date().isoformat(),
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'next_measurement': self._get_next_measurement_time(measurement_schedule),
                'adherence_score': 0.0,
                'total_measurements': 0,
                'completed_measurements': 0
            }
            
            return {
                'success': True,
                'monitoring_plan': monitoring_plan
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء خطة المتابعة: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_measurement_schedule(self, vital_signs: List[str], frequency: str) -> List[Dict]:
        """إنشاء جدول القياسات"""
        schedule = []
        
        # تحديد أوقات القياس حسب التكرار
        if frequency == MonitoringFrequency.DAILY.value:
            times = ['08:00']
        elif frequency == MonitoringFrequency.TWICE_DAILY.value:
            times = ['08:00', '20:00']
        elif frequency == MonitoringFrequency.WEEKLY.value:
            times = ['08:00']  # مرة واحدة أسبوعياً
        else:
            times = ['08:00']  # افتراضي
        
        # إنشاء الجدول لكل علامة حيوية
        for vital_sign in vital_signs:
            for time_str in times:
                schedule_entry = {
                    'schedule_id': str(uuid.uuid4()),
                    'vital_sign': vital_sign,
                    'time': time_str,
                    'frequency': frequency,
                    'reminder_enabled': True,
                    'auto_sync': True
                }
                schedule.append(schedule_entry)
        
        return schedule
    
    def _get_required_devices(self, vital_signs: List[str]) -> List[Dict]:
        """تحديد الأجهزة المطلوبة"""
        required_devices = []
        
        for vital_sign in vital_signs:
            for device in self.compatible_devices:
                if vital_sign.lower().replace(' ', '_') in device['supported_vitals']:
                    if device not in required_devices:
                        required_devices.append(device)
        
        return required_devices
    
    def _get_next_measurement_time(self, schedule: List[Dict]) -> Optional[str]:
        """الحصول على وقت القياس التالي"""
        now = datetime.now()
        next_times = []
        
        for entry in schedule:
            time_obj = datetime.strptime(entry['time'], '%H:%M').time()
            next_datetime = datetime.combine(now.date(), time_obj)
            
            # إذا كان الوقت قد مر اليوم، اجعله غداً
            if next_datetime <= now:
                next_datetime = datetime.combine(now.date() + timedelta(days=1), time_obj)
            
            next_times.append(next_datetime)
        
        if next_times:
            return min(next_times).isoformat()
        return None
    
    def record_vital_sign(self, patient_id: str, vital_type: str, 
                         value: float, unit: str, device_id: str = None,
                         notes: str = None) -> Dict:
        """
        تسجيل قراءة العلامات الحيوية
        
        Args:
            patient_id: معرف المريض
            vital_type: نوع العلامة الحيوية
            value: القيمة
            unit: الوحدة
            device_id: معرف الجهاز
            notes: ملاحظات
            
        Returns:
            Dict: نتيجة التسجيل
        """
        try:
            reading_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # تحليل القراءة
            analysis = self._analyze_vital_sign(vital_type, value, patient_id)
            
            # إنشاء سجل القراءة
            vital_reading = {
                'reading_id': reading_id,
                'patient_id': patient_id,
                'vital_type': vital_type,
                'value': value,
                'unit': unit,
                'timestamp': timestamp.isoformat(),
                'device_id': device_id,
                'notes': notes,
                'is_normal': analysis['is_normal'],
                'alert_level': analysis['alert_level'],
                'interpretation': analysis['interpretation'],
                'recommendations': analysis['recommendations']
            }
            
            # إرسال تنبيه إذا كانت القراءة غير طبيعية
            if not analysis['is_normal']:
                self._send_abnormal_reading_alert(patient_id, vital_reading)
            
            return {
                'success': True,
                'vital_reading': vital_reading,
                'analysis': analysis
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تسجيل العلامة الحيوية: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_vital_sign(self, vital_type: str, value: float, patient_id: str) -> Dict:
        """تحليل قراءة العلامة الحيوية"""
        analysis = {
            'is_normal': True,
            'alert_level': 'normal',
            'interpretation': 'القراءة طبيعية',
            'recommendations': []
        }
        
        # تحليل حسب نوع العلامة الحيوية
        if vital_type == VitalSignType.BLOOD_PRESSURE.value:
            # افتراض أن القيمة هي الضغط الانقباضي
            if value < 90:
                analysis.update({
                    'is_normal': False,
                    'alert_level': 'low',
                    'interpretation': 'ضغط الدم منخفض',
                    'recommendations': ['شرب السوائل', 'تجنب الوقوف المفاجئ', 'استشارة الطبيب']
                })
            elif value > 140:
                analysis.update({
                    'is_normal': False,
                    'alert_level': 'high',
                    'interpretation': 'ضغط الدم مرتفع',
                    'recommendations': ['تقليل الملح', 'ممارسة الرياضة', 'استشارة الطبيب فوراً']
                })
        
        elif vital_type == VitalSignType.BLOOD_SUGAR.value:
            if value < 70:
                analysis.update({
                    'is_normal': False,
                    'alert_level': 'low',
                    'interpretation': 'انخفاض سكر الدم',
                    'recommendations': ['تناول سكريات سريعة', 'قياس السكر مرة أخرى', 'اتصل بالطبيب']
                })
            elif value > 200:
                analysis.update({
                    'is_normal': False,
                    'alert_level': 'critical',
                    'interpretation': 'ارتفاع خطير في سكر الدم',
                    'recommendations': ['اتصل بالطوارئ فوراً', 'تناول الأدوية حسب التعليمات']
                })
        
        elif vital_type == VitalSignType.TEMPERATURE.value:
            if value < 36.1:
                analysis.update({
                    'is_normal': False,
                    'alert_level': 'low',
                    'interpretation': 'انخفاض درجة الحرارة',
                    'recommendations': ['التدفئة', 'مراقبة الأعراض', 'استشارة الطبيب']
                })
            elif value > 38.0:
                analysis.update({
                    'is_normal': False,
                    'alert_level': 'high',
                    'interpretation': 'ارتفاع درجة الحرارة (حمى)',
                    'recommendations': ['راحة في السرير', 'شرب السوائل', 'خافض حرارة', 'استشارة الطبيب']
                })
        
        elif vital_type == VitalSignType.OXYGEN_SATURATION.value:
            if value < 95:
                analysis.update({
                    'is_normal': False,
                    'alert_level': 'critical',
                    'interpretation': 'انخفاض تشبع الأكسجين',
                    'recommendations': ['اتصل بالطوارئ فوراً', 'تنفس عميق', 'تجنب المجهود']
                })
        
        return analysis
    
    def _send_abnormal_reading_alert(self, patient_id: str, vital_reading: Dict):
        """إرسال تنبيه للقراءات غير الطبيعية"""
        try:
            # في التطبيق الحقيقي، سيتم استدعاء خدمة الإشعارات
            alert_data = {
                'patient_id': patient_id,
                'vital_type': vital_reading['vital_type'],
                'value': vital_reading['value'],
                'alert_level': vital_reading['alert_level'],
                'interpretation': vital_reading['interpretation'],
                'timestamp': vital_reading['timestamp']
            }
            
            # إرسال للمريض والطبيب المعالج
            current_app.logger.info(f"تنبيه: قراءة غير طبيعية للمريض {patient_id}")
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال التنبيه: {str(e)}")
    
    def get_vital_signs_history(self, patient_id: str, vital_type: str = None,
                               start_date: str = None, end_date: str = None) -> Dict:
        """الحصول على تاريخ العلامات الحيوية"""
        try:
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            # هنا محاكاة للبيانات
            
            history_data = {
                'patient_id': patient_id,
                'vital_type': vital_type,
                'period': {
                    'start_date': start_date or (datetime.now() - timedelta(days=30)).date().isoformat(),
                    'end_date': end_date or datetime.now().date().isoformat()
                },
                'readings': [
                    {
                        'reading_id': str(uuid.uuid4()),
                        'vital_type': 'ضغط الدم',
                        'value': 120,
                        'unit': 'mmHg',
                        'timestamp': '2024-01-15T08:00:00',
                        'is_normal': True,
                        'alert_level': 'normal'
                    },
                    {
                        'reading_id': str(uuid.uuid4()),
                        'vital_type': 'سكر الدم',
                        'value': 95,
                        'unit': 'mg/dL',
                        'timestamp': '2024-01-15T08:30:00',
                        'is_normal': True,
                        'alert_level': 'normal'
                    },
                    {
                        'reading_id': str(uuid.uuid4()),
                        'vital_type': 'الوزن',
                        'value': 75.5,
                        'unit': 'kg',
                        'timestamp': '2024-01-15T07:00:00',
                        'is_normal': True,
                        'alert_level': 'normal'
                    }
                ],
                'statistics': {
                    'total_readings': 3,
                    'normal_readings': 3,
                    'abnormal_readings': 0,
                    'average_value': 96.83,
                    'trend': 'stable'
                }
            }
            
            return {
                'success': True,
                'history': history_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_health_report(self, patient_id: str, period_days: int = 30) -> Dict:
        """إنتاج تقرير صحي شامل"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=period_days)
            
            # جمع البيانات من مصادر مختلفة
            vital_signs_data = self.get_vital_signs_history(
                patient_id, start_date=start_date.isoformat(), 
                end_date=end_date.isoformat()
            )
            
            # تحليل الاتجاهات
            trends_analysis = self._analyze_health_trends(patient_id, period_days)
            
            # توصيات صحية
            health_recommendations = self._generate_health_recommendations(patient_id)
            
            # إنشاء التقرير
            health_report = {
                'report_id': str(uuid.uuid4()),
                'patient_id': patient_id,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': period_days
                },
                'vital_signs_summary': vital_signs_data.get('history', {}),
                'trends_analysis': trends_analysis,
                'health_score': self._calculate_health_score(patient_id),
                'recommendations': health_recommendations,
                'generated_at': datetime.now().isoformat(),
                'next_checkup_due': (datetime.now() + timedelta(days=90)).date().isoformat()
            }
            
            return {
                'success': True,
                'health_report': health_report
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_health_trends(self, patient_id: str, period_days: int) -> Dict:
        """تحليل الاتجاهات الصحية"""
        # محاكاة تحليل الاتجاهات
        return {
            'blood_pressure_trend': 'مستقر',
            'weight_trend': 'انخفاض طفيف',
            'blood_sugar_trend': 'تحسن',
            'overall_trend': 'إيجابي',
            'risk_factors': ['قلة النشاط البدني'],
            'improvements': ['انتظام في تناول الأدوية', 'تحسن في النظام الغذائي']
        }
    
    def _generate_health_recommendations(self, patient_id: str) -> List[str]:
        """إنتاج توصيات صحية مخصصة"""
        return [
            'الاستمرار في قياس ضغط الدم يومياً',
            'زيادة النشاط البدني إلى 30 دقيقة يومياً',
            'تقليل تناول الملح في الطعام',
            'شرب 8 أكواب ماء يومياً',
            'المتابعة مع الطبيب كل 3 أشهر'
        ]
    
    def _calculate_health_score(self, patient_id: str) -> float:
        """حساب النقاط الصحية الإجمالية"""
        # محاكاة حساب النقاط بناءً على عوامل مختلفة
        factors = {
            'vital_signs_stability': 85,
            'medication_adherence': 90,
            'lifestyle_factors': 75,
            'risk_management': 80
        }
        
        total_score = sum(factors.values()) / len(factors)
        return round(total_score, 1)
    
    def setup_device_integration(self, patient_id: str, device_id: str, 
                               connection_type: str) -> Dict:
        """إعداد تكامل الأجهزة الطبية"""
        try:
            # البحث عن الجهاز
            device_info = None
            for device in self.compatible_devices:
                if device['device_id'] == device_id:
                    device_info = device
                    break
            
            if not device_info:
                raise Exception('جهاز غير مدعوم')
            
            # إعداد الاتصال
            integration_config = {
                'integration_id': str(uuid.uuid4()),
                'patient_id': patient_id,
                'device_id': device_id,
                'device_info': device_info,
                'connection_type': connection_type,
                'status': 'connected',
                'last_sync': datetime.now().isoformat(),
                'auto_sync_enabled': True,
                'sync_frequency': 'real_time',
                'data_encryption': True
            }
            
            return {
                'success': True,
                'integration_config': integration_config,
                'message': 'تم ربط الجهاز بنجاح'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_monitoring_dashboard(self, patient_id: str) -> Dict:
        """الحصول على لوحة تحكم المتابعة"""
        try:
            # جمع البيانات من مصادر مختلفة
            current_vitals = self._get_current_vitals(patient_id)
            recent_trends = self._get_recent_trends(patient_id)
            upcoming_measurements = self._get_upcoming_measurements(patient_id)
            alerts = self._get_active_alerts(patient_id)
            
            dashboard = {
                'patient_id': patient_id,
                'last_updated': datetime.now().isoformat(),
                'current_vitals': current_vitals,
                'recent_trends': recent_trends,
                'upcoming_measurements': upcoming_measurements,
                'active_alerts': alerts,
                'health_score': self._calculate_health_score(patient_id),
                'adherence_rate': 92.5,
                'connected_devices': 3,
                'total_measurements_today': 5
            }
            
            return {
                'success': True,
                'dashboard': dashboard
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_current_vitals(self, patient_id: str) -> List[Dict]:
        """الحصول على آخر قراءات العلامات الحيوية"""
        return [
            {
                'vital_type': 'ضغط الدم',
                'value': '120/80',
                'unit': 'mmHg',
                'status': 'normal',
                'last_reading': '2024-01-15T08:00:00'
            },
            {
                'vital_type': 'سكر الدم',
                'value': 95,
                'unit': 'mg/dL',
                'status': 'normal',
                'last_reading': '2024-01-15T08:30:00'
            },
            {
                'vital_type': 'الوزن',
                'value': 75.5,
                'unit': 'kg',
                'status': 'normal',
                'last_reading': '2024-01-15T07:00:00'
            }
        ]
    
    def _get_recent_trends(self, patient_id: str) -> Dict:
        """الحصول على الاتجاهات الحديثة"""
        return {
            'blood_pressure': 'مستقر',
            'weight': 'انخفاض طفيف',
            'blood_sugar': 'تحسن',
            'overall': 'إيجابي'
        }
    
    def _get_upcoming_measurements(self, patient_id: str) -> List[Dict]:
        """الحصول على القياسات القادمة"""
        return [
            {
                'vital_type': 'ضغط الدم',
                'scheduled_time': '2024-01-16T08:00:00',
                'reminder_set': True
            },
            {
                'vital_type': 'سكر الدم',
                'scheduled_time': '2024-01-16T08:30:00',
                'reminder_set': True
            }
        ]
    
    def _get_active_alerts(self, patient_id: str) -> List[Dict]:
        """الحصول على التنبيهات النشطة"""
        return [
            {
                'alert_id': str(uuid.uuid4()),
                'type': 'medication_reminder',
                'message': 'حان وقت تناول دواء الضغط',
                'priority': 'medium',
                'created_at': datetime.now().isoformat()
            }
        ]

