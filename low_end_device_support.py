"""
خدمة دعم الأجهزة الضعيفة وتحسين الأداء
"""

import os
import json
import gzip
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app, request
from dataclasses import dataclass
from enum import Enum
import threading
import time
from PIL import Image
import io

class DeviceType(Enum):
    HIGH_END = "جهاز متقدم"
    MEDIUM_END = "جهاز متوسط"
    LOW_END = "جهاز ضعيف"
    VERY_LOW_END = "جهاز ضعيف جداً"

class ConnectionType(Enum):
    WIFI_FAST = "واي فاي سريع"
    WIFI_SLOW = "واي فاي بطيء"
    MOBILE_4G = "بيانات 4G"
    MOBILE_3G = "بيانات 3G"
    MOBILE_2G = "بيانات 2G"

class OptimizationLevel(Enum):
    NONE = "بدون تحسين"
    BASIC = "تحسين أساسي"
    MODERATE = "تحسين متوسط"
    AGGRESSIVE = "تحسين قوي"
    EXTREME = "تحسين قصوى"

@dataclass
class DeviceProfile:
    device_id: str
    device_type: str
    ram_mb: int
    storage_gb: int
    cpu_cores: int
    screen_width: int
    screen_height: int
    connection_type: str
    connection_speed_kbps: int
    battery_level: int
    is_low_power_mode: bool
    optimization_level: str
    created_at: datetime
    last_updated: datetime

@dataclass
class OptimizationSettings:
    compress_images: bool
    image_quality: int
    max_image_width: int
    max_image_height: int
    enable_lazy_loading: bool
    reduce_animations: bool
    minimize_javascript: bool
    compress_responses: bool
    cache_aggressively: bool
    preload_critical_resources: bool
    defer_non_critical_resources: bool
    use_webp_format: bool
    enable_offline_mode: bool

class LowEndDeviceSupportService:
    def __init__(self):
        """تهيئة خدمة دعم الأجهزة الضعيفة"""
        
        # معايير تصنيف الأجهزة
        self.device_classification = {
            DeviceType.VERY_LOW_END.value: {
                'ram_mb_max': 1024,
                'storage_gb_max': 8,
                'cpu_cores_max': 2,
                'connection_speed_max': 256
            },
            DeviceType.LOW_END.value: {
                'ram_mb_max': 2048,
                'storage_gb_max': 16,
                'cpu_cores_max': 4,
                'connection_speed_max': 1024
            },
            DeviceType.MEDIUM_END.value: {
                'ram_mb_max': 4096,
                'storage_gb_max': 64,
                'cpu_cores_max': 6,
                'connection_speed_max': 5120
            },
            DeviceType.HIGH_END.value: {
                'ram_mb_max': float('inf'),
                'storage_gb_max': float('inf'),
                'cpu_cores_max': float('inf'),
                'connection_speed_max': float('inf')
            }
        }
        
        # إعدادات التحسين لكل نوع جهاز
        self.optimization_presets = {
            DeviceType.VERY_LOW_END.value: OptimizationSettings(
                compress_images=True,
                image_quality=30,
                max_image_width=320,
                max_image_height=240,
                enable_lazy_loading=True,
                reduce_animations=True,
                minimize_javascript=True,
                compress_responses=True,
                cache_aggressively=True,
                preload_critical_resources=False,
                defer_non_critical_resources=True,
                use_webp_format=True,
                enable_offline_mode=True
            ),
            DeviceType.LOW_END.value: OptimizationSettings(
                compress_images=True,
                image_quality=50,
                max_image_width=480,
                max_image_height=360,
                enable_lazy_loading=True,
                reduce_animations=True,
                minimize_javascript=True,
                compress_responses=True,
                cache_aggressively=True,
                preload_critical_resources=True,
                defer_non_critical_resources=True,
                use_webp_format=True,
                enable_offline_mode=True
            ),
            DeviceType.MEDIUM_END.value: OptimizationSettings(
                compress_images=True,
                image_quality=70,
                max_image_width=720,
                max_image_height=540,
                enable_lazy_loading=True,
                reduce_animations=False,
                minimize_javascript=False,
                compress_responses=True,
                cache_aggressively=False,
                preload_critical_resources=True,
                defer_non_critical_resources=False,
                use_webp_format=True,
                enable_offline_mode=False
            ),
            DeviceType.HIGH_END.value: OptimizationSettings(
                compress_images=False,
                image_quality=90,
                max_image_width=1920,
                max_image_height=1080,
                enable_lazy_loading=False,
                reduce_animations=False,
                minimize_javascript=False,
                compress_responses=False,
                cache_aggressively=False,
                preload_critical_resources=True,
                defer_non_critical_resources=False,
                use_webp_format=False,
                enable_offline_mode=False
            )
        }
        
        # ميزات مبسطة للأجهزة الضعيفة
        self.simplified_features = {
            'basic_ui': {
                'description': 'واجهة مبسطة بدون تأثيرات',
                'enabled_for': [DeviceType.VERY_LOW_END.value, DeviceType.LOW_END.value]
            },
            'text_only_mode': {
                'description': 'وضع النص فقط بدون صور',
                'enabled_for': [DeviceType.VERY_LOW_END.value]
            },
            'offline_sync': {
                'description': 'مزامنة البيانات عند توفر الاتصال',
                'enabled_for': [DeviceType.VERY_LOW_END.value, DeviceType.LOW_END.value]
            },
            'progressive_loading': {
                'description': 'تحميل تدريجي للمحتوى',
                'enabled_for': [DeviceType.VERY_LOW_END.value, DeviceType.LOW_END.value, DeviceType.MEDIUM_END.value]
            },
            'data_saver_mode': {
                'description': 'وضع توفير البيانات',
                'enabled_for': [DeviceType.VERY_LOW_END.value, DeviceType.LOW_END.value]
            }
        }
        
        # قاعدة بيانات الأجهزة (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.device_profiles = {}
        self.performance_metrics = {}
        self.optimization_cache = {}
        
        # إحصائيات الاستخدام
        self.usage_stats = {
            'device_types': {},
            'connection_types': {},
            'optimization_levels': {},
            'feature_usage': {}
        }
    
    def detect_device_capabilities(self, device_info: Dict) -> Dict:
        """
        كشف قدرات الجهاز وتصنيفه
        
        Args:
            device_info: معلومات الجهاز
            
        Returns:
            Dict: تصنيف الجهاز وقدراته
        """
        try:
            # استخراج معلومات الجهاز
            user_agent = device_info.get('user_agent', '')
            screen_width = device_info.get('screen_width', 0)
            screen_height = device_info.get('screen_height', 0)
            ram_mb = device_info.get('ram_mb', 0)
            storage_gb = device_info.get('storage_gb', 0)
            cpu_cores = device_info.get('cpu_cores', 0)
            connection_speed = device_info.get('connection_speed_kbps', 0)
            battery_level = device_info.get('battery_level', 100)
            is_low_power_mode = device_info.get('is_low_power_mode', False)
            
            # تحليل User Agent لاستخراج معلومات إضافية
            device_analysis = self._analyze_user_agent(user_agent)
            
            # تقدير قدرات الجهاز إذا لم تكن متوفرة
            if ram_mb == 0:
                ram_mb = self._estimate_ram_from_device(device_analysis)
            if cpu_cores == 0:
                cpu_cores = self._estimate_cpu_cores(device_analysis)
            if connection_speed == 0:
                connection_speed = self._estimate_connection_speed(device_info)
            
            # تصنيف الجهاز
            device_type = self._classify_device(ram_mb, storage_gb, cpu_cores, connection_speed)
            
            # تحديد نوع الاتصال
            connection_type = self._determine_connection_type(connection_speed, device_info)
            
            # تحديد مستوى التحسين المطلوب
            optimization_level = self._determine_optimization_level(
                device_type, connection_type, battery_level, is_low_power_mode
            )
            
            # إنشاء ملف الجهاز
            device_id = device_info.get('device_id') or self._generate_device_id(device_info)
            
            device_profile = DeviceProfile(
                device_id=device_id,
                device_type=device_type,
                ram_mb=ram_mb,
                storage_gb=storage_gb,
                cpu_cores=cpu_cores,
                screen_width=screen_width,
                screen_height=screen_height,
                connection_type=connection_type,
                connection_speed_kbps=connection_speed,
                battery_level=battery_level,
                is_low_power_mode=is_low_power_mode,
                optimization_level=optimization_level,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            # حفظ ملف الجهاز
            self.device_profiles[device_id] = device_profile
            
            # تحديث الإحصائيات
            self._update_usage_stats(device_profile)
            
            return {
                'success': True,
                'device_id': device_id,
                'device_type': device_type,
                'connection_type': connection_type,
                'optimization_level': optimization_level,
                'capabilities': {
                    'ram_mb': ram_mb,
                    'storage_gb': storage_gb,
                    'cpu_cores': cpu_cores,
                    'screen_resolution': f"{screen_width}x{screen_height}",
                    'connection_speed_kbps': connection_speed
                },
                'recommended_features': self._get_recommended_features(device_type),
                'optimization_settings': self._get_optimization_settings(device_type)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في كشف قدرات الجهاز: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في كشف قدرات الجهاز'
            }
    
    def optimize_content_for_device(self, content: Dict, device_id: str) -> Dict:
        """
        تحسين المحتوى للجهاز
        
        Args:
            content: المحتوى المراد تحسينه
            device_id: معرف الجهاز
            
        Returns:
            Dict: المحتوى المحسن
        """
        try:
            # الحصول على ملف الجهاز
            if device_id not in self.device_profiles:
                return {
                    'success': False,
                    'error': 'ملف الجهاز غير موجود'
                }
            
            device_profile = self.device_profiles[device_id]
            optimization_settings = self.optimization_presets[device_profile.device_type]
            
            optimized_content = content.copy()
            
            # تحسين الصور
            if 'images' in content and optimization_settings.compress_images:
                optimized_content['images'] = self._optimize_images(
                    content['images'], optimization_settings
                )
            
            # تحسين النصوص
            if 'text' in content:
                optimized_content['text'] = self._optimize_text(
                    content['text'], optimization_settings
                )
            
            # تحسين البيانات
            if optimization_settings.compress_responses:
                optimized_content = self._compress_data(optimized_content)
            
            # إضافة معلومات التحسين
            optimized_content['optimization_info'] = {
                'device_type': device_profile.device_type,
                'optimization_level': device_profile.optimization_level,
                'optimized_at': datetime.now().isoformat(),
                'original_size': len(json.dumps(content)),
                'optimized_size': len(json.dumps(optimized_content))
            }
            
            return {
                'success': True,
                'optimized_content': optimized_content,
                'optimization_applied': True
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحسين المحتوى: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تحسين المحتوى'
            }
    
    def get_adaptive_ui_config(self, device_id: str) -> Dict:
        """
        الحصول على إعدادات الواجهة التكيفية
        
        Args:
            device_id: معرف الجهاز
            
        Returns:
            Dict: إعدادات الواجهة
        """
        try:
            if device_id not in self.device_profiles:
                return {
                    'success': False,
                    'error': 'ملف الجهاز غير موجود'
                }
            
            device_profile = self.device_profiles[device_id]
            device_type = device_profile.device_type
            
            # إعدادات الواجهة حسب نوع الجهاز
            ui_config = {
                'theme': 'light',  # الثيم الافتراضي
                'layout': 'responsive',
                'animations': True,
                'transitions': True,
                'shadows': True,
                'gradients': True,
                'icons': 'full',
                'font_size': 'medium',
                'button_size': 'medium',
                'spacing': 'normal',
                'image_quality': 'high',
                'lazy_loading': False,
                'infinite_scroll': True,
                'preload_pages': True,
                'cache_strategy': 'normal',
                'offline_support': False
            }
            
            # تخصيص الإعدادات للأجهزة الضعيفة
            if device_type == DeviceType.VERY_LOW_END.value:
                ui_config.update({
                    'theme': 'minimal',
                    'layout': 'simple',
                    'animations': False,
                    'transitions': False,
                    'shadows': False,
                    'gradients': False,
                    'icons': 'minimal',
                    'font_size': 'large',
                    'button_size': 'large',
                    'spacing': 'compact',
                    'image_quality': 'low',
                    'lazy_loading': True,
                    'infinite_scroll': False,
                    'preload_pages': False,
                    'cache_strategy': 'aggressive',
                    'offline_support': True
                })
            
            elif device_type == DeviceType.LOW_END.value:
                ui_config.update({
                    'theme': 'simple',
                    'animations': False,
                    'transitions': True,
                    'shadows': False,
                    'gradients': False,
                    'icons': 'simple',
                    'image_quality': 'medium',
                    'lazy_loading': True,
                    'infinite_scroll': False,
                    'preload_pages': False,
                    'cache_strategy': 'aggressive',
                    'offline_support': True
                })
            
            elif device_type == DeviceType.MEDIUM_END.value:
                ui_config.update({
                    'animations': True,
                    'shadows': True,
                    'image_quality': 'medium',
                    'lazy_loading': True,
                    'cache_strategy': 'smart'
                })
            
            # تخصيص إضافي حسب حجم الشاشة
            if device_profile.screen_width < 480:
                ui_config.update({
                    'layout': 'mobile_first',
                    'font_size': 'large',
                    'button_size': 'large',
                    'spacing': 'compact'
                })
            
            # تخصيص حسب مستوى البطارية
            if device_profile.battery_level < 20 or device_profile.is_low_power_mode:
                ui_config.update({
                    'animations': False,
                    'transitions': False,
                    'theme': 'dark',  # توفير البطارية
                    'image_quality': 'low',
                    'cache_strategy': 'aggressive'
                })
            
            return {
                'success': True,
                'device_id': device_id,
                'device_type': device_type,
                'ui_config': ui_config,
                'adaptive_features': self._get_adaptive_features(device_profile)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على إعدادات الواجهة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على إعدادات الواجهة'
            }
    
    def enable_offline_mode(self, device_id: str, offline_data: Dict = None) -> Dict:
        """
        تفعيل الوضع غير المتصل
        
        Args:
            device_id: معرف الجهاز
            offline_data: البيانات للوضع غير المتصل
            
        Returns:
            Dict: نتيجة التفعيل
        """
        try:
            if device_id not in self.device_profiles:
                return {
                    'success': False,
                    'error': 'ملف الجهاز غير موجود'
                }
            
            device_profile = self.device_profiles[device_id]
            
            # البيانات الأساسية للوضع غير المتصل
            offline_package = {
                'device_id': device_id,
                'enabled_at': datetime.now().isoformat(),
                'essential_data': {
                    'user_profile': offline_data.get('user_profile', {}),
                    'medical_records': offline_data.get('medical_records', []),
                    'medications': offline_data.get('medications', []),
                    'emergency_contacts': offline_data.get('emergency_contacts', []),
                    'recent_appointments': offline_data.get('recent_appointments', [])
                },
                'cached_pages': [
                    'dashboard',
                    'profile',
                    'medications',
                    'emergency'
                ],
                'offline_features': [
                    'view_medical_records',
                    'medication_reminders',
                    'emergency_contacts',
                    'basic_health_calculator'
                ],
                'sync_queue': [],
                'last_sync': datetime.now().isoformat()
            }
            
            # ضغط البيانات للأجهزة الضعيفة
            if device_profile.device_type in [DeviceType.VERY_LOW_END.value, DeviceType.LOW_END.value]:
                offline_package = self._compress_offline_data(offline_package)
            
            return {
                'success': True,
                'device_id': device_id,
                'offline_package': offline_package,
                'package_size_kb': len(json.dumps(offline_package)) / 1024,
                'estimated_storage_mb': self._estimate_offline_storage(offline_package),
                'sync_instructions': self._get_sync_instructions(device_profile)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تفعيل الوضع غير المتصل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تفعيل الوضع غير المتصل'
            }
    
    def sync_offline_data(self, device_id: str, sync_data: Dict) -> Dict:
        """
        مزامنة البيانات من الوضع غير المتصل
        
        Args:
            device_id: معرف الجهاز
            sync_data: البيانات للمزامنة
            
        Returns:
            Dict: نتيجة المزامنة
        """
        try:
            if device_id not in self.device_profiles:
                return {
                    'success': False,
                    'error': 'ملف الجهاز غير موجود'
                }
            
            device_profile = self.device_profiles[device_id]
            
            # معالجة البيانات المرسلة
            sync_queue = sync_data.get('sync_queue', [])
            last_sync = sync_data.get('last_sync')
            
            sync_results = {
                'synced_items': 0,
                'failed_items': 0,
                'conflicts': 0,
                'sync_details': []
            }
            
            # معالجة كل عنصر في قائمة المزامنة
            for item in sync_queue:
                try:
                    item_type = item.get('type')
                    item_data = item.get('data')
                    timestamp = item.get('timestamp')
                    
                    # معالجة حسب نوع البيانات
                    if item_type == 'medication_taken':
                        # تسجيل تناول دواء
                        result = self._sync_medication_record(item_data)
                    elif item_type == 'health_measurement':
                        # قياس صحي
                        result = self._sync_health_measurement(item_data)
                    elif item_type == 'profile_update':
                        # تحديث الملف الشخصي
                        result = self._sync_profile_update(item_data)
                    elif item_type == 'appointment_note':
                        # ملاحظة موعد
                        result = self._sync_appointment_note(item_data)
                    else:
                        result = {'success': False, 'error': 'نوع بيانات غير مدعوم'}
                    
                    if result['success']:
                        sync_results['synced_items'] += 1
                    else:
                        sync_results['failed_items'] += 1
                    
                    sync_results['sync_details'].append({
                        'item_type': item_type,
                        'timestamp': timestamp,
                        'success': result['success'],
                        'error': result.get('error')
                    })
                    
                except Exception as e:
                    sync_results['failed_items'] += 1
                    sync_results['sync_details'].append({
                        'item_type': item.get('type', 'unknown'),
                        'timestamp': item.get('timestamp'),
                        'success': False,
                        'error': str(e)
                    })
            
            # إنشاء حزمة التحديث للجهاز
            update_package = self._create_update_package(device_id, last_sync)
            
            return {
                'success': True,
                'device_id': device_id,
                'sync_results': sync_results,
                'update_package': update_package,
                'next_sync_recommended': (datetime.now() + timedelta(hours=6)).isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في مزامنة البيانات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في المزامنة'
            }
    
    def get_performance_metrics(self, device_id: str = None) -> Dict:
        """
        الحصول على مقاييس الأداء
        
        Args:
            device_id: معرف جهاز محدد (اختياري)
            
        Returns:
            Dict: مقاييس الأداء
        """
        try:
            if device_id:
                # مقاييس جهاز محدد
                if device_id not in self.device_profiles:
                    return {
                        'success': False,
                        'error': 'ملف الجهاز غير موجود'
                    }
                
                device_profile = self.device_profiles[device_id]
                device_metrics = self.performance_metrics.get(device_id, {})
                
                return {
                    'success': True,
                    'device_id': device_id,
                    'device_type': device_profile.device_type,
                    'metrics': device_metrics,
                    'optimization_effectiveness': self._calculate_optimization_effectiveness(device_id)
                }
            
            else:
                # مقاييس عامة لجميع الأجهزة
                total_devices = len(self.device_profiles)
                
                # توزيع أنواع الأجهزة
                device_type_distribution = {}
                for profile in self.device_profiles.values():
                    device_type = profile.device_type
                    if device_type not in device_type_distribution:
                        device_type_distribution[device_type] = 0
                    device_type_distribution[device_type] += 1
                
                # توزيع أنواع الاتصال
                connection_type_distribution = {}
                for profile in self.device_profiles.values():
                    connection_type = profile.connection_type
                    if connection_type not in connection_type_distribution:
                        connection_type_distribution[connection_type] = 0
                    connection_type_distribution[connection_type] += 1
                
                # حساب متوسط الأداء
                avg_performance = self._calculate_average_performance()
                
                return {
                    'success': True,
                    'total_devices': total_devices,
                    'device_type_distribution': device_type_distribution,
                    'connection_type_distribution': connection_type_distribution,
                    'average_performance': avg_performance,
                    'optimization_stats': self._get_optimization_stats(),
                    'recommendations': self._get_performance_recommendations()
                }
                
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على مقاييس الأداء: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على المقاييس'
            }
    
    # الدوال المساعدة
    def _analyze_user_agent(self, user_agent: str) -> Dict:
        """تحليل User Agent لاستخراج معلومات الجهاز"""
        analysis = {
            'is_mobile': False,
            'is_tablet': False,
            'is_desktop': True,
            'os': 'unknown',
            'browser': 'unknown',
            'device_model': 'unknown'
        }
        
        user_agent_lower = user_agent.lower()
        
        # كشف نوع الجهاز
        if any(keyword in user_agent_lower for keyword in ['mobile', 'android', 'iphone']):
            analysis['is_mobile'] = True
            analysis['is_desktop'] = False
        elif any(keyword in user_agent_lower for keyword in ['tablet', 'ipad']):
            analysis['is_tablet'] = True
            analysis['is_desktop'] = False
        
        # كشف نظام التشغيل
        if 'android' in user_agent_lower:
            analysis['os'] = 'android'
        elif 'ios' in user_agent_lower or 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
            analysis['os'] = 'ios'
        elif 'windows' in user_agent_lower:
            analysis['os'] = 'windows'
        elif 'mac' in user_agent_lower:
            analysis['os'] = 'macos'
        elif 'linux' in user_agent_lower:
            analysis['os'] = 'linux'
        
        # كشف المتصفح
        if 'chrome' in user_agent_lower:
            analysis['browser'] = 'chrome'
        elif 'firefox' in user_agent_lower:
            analysis['browser'] = 'firefox'
        elif 'safari' in user_agent_lower:
            analysis['browser'] = 'safari'
        elif 'edge' in user_agent_lower:
            analysis['browser'] = 'edge'
        
        return analysis
    
    def _estimate_ram_from_device(self, device_analysis: Dict) -> int:
        """تقدير ذاكرة الوصول العشوائي من معلومات الجهاز"""
        if device_analysis['is_mobile']:
            if device_analysis['os'] == 'android':
                return 3072  # متوسط أجهزة أندرويد
            elif device_analysis['os'] == 'ios':
                return 4096  # متوسط أجهزة iOS
        elif device_analysis['is_tablet']:
            return 4096
        else:
            return 8192  # متوسط أجهزة سطح المكتب
    
    def _estimate_cpu_cores(self, device_analysis: Dict) -> int:
        """تقدير عدد أنوية المعالج"""
        if device_analysis['is_mobile']:
            return 4  # متوسط الهواتف الذكية
        elif device_analysis['is_tablet']:
            return 6
        else:
            return 8  # متوسط أجهزة سطح المكتب
    
    def _estimate_connection_speed(self, device_info: Dict) -> int:
        """تقدير سرعة الاتصال"""
        connection_type = device_info.get('connection_type', '')
        
        if 'wifi' in connection_type.lower():
            return 10240  # 10 Mbps
        elif '4g' in connection_type.lower():
            return 5120   # 5 Mbps
        elif '3g' in connection_type.lower():
            return 1024   # 1 Mbps
        elif '2g' in connection_type.lower():
            return 256    # 256 Kbps
        else:
            return 2048   # افتراضي 2 Mbps
    
    def _classify_device(self, ram_mb: int, storage_gb: int, cpu_cores: int, connection_speed: int) -> str:
        """تصنيف الجهاز حسب قدراته"""
        for device_type, limits in self.device_classification.items():
            if (ram_mb <= limits['ram_mb_max'] and
                storage_gb <= limits['storage_gb_max'] and
                cpu_cores <= limits['cpu_cores_max'] and
                connection_speed <= limits['connection_speed_max']):
                return device_type
        
        return DeviceType.HIGH_END.value
    
    def _determine_connection_type(self, connection_speed: int, device_info: Dict) -> str:
        """تحديد نوع الاتصال"""
        if connection_speed >= 10240:
            return ConnectionType.WIFI_FAST.value
        elif connection_speed >= 2048:
            return ConnectionType.WIFI_SLOW.value
        elif connection_speed >= 1024:
            return ConnectionType.MOBILE_4G.value
        elif connection_speed >= 512:
            return ConnectionType.MOBILE_3G.value
        else:
            return ConnectionType.MOBILE_2G.value
    
    def _determine_optimization_level(self, device_type: str, connection_type: str, 
                                    battery_level: int, is_low_power_mode: bool) -> str:
        """تحديد مستوى التحسين المطلوب"""
        if device_type == DeviceType.VERY_LOW_END.value:
            return OptimizationLevel.EXTREME.value
        elif device_type == DeviceType.LOW_END.value:
            return OptimizationLevel.AGGRESSIVE.value
        elif (device_type == DeviceType.MEDIUM_END.value and 
              (battery_level < 20 or is_low_power_mode or 
               connection_type in [ConnectionType.MOBILE_2G.value, ConnectionType.MOBILE_3G.value])):
            return OptimizationLevel.MODERATE.value
        elif device_type == DeviceType.MEDIUM_END.value:
            return OptimizationLevel.BASIC.value
        else:
            return OptimizationLevel.NONE.value
    
    def _generate_device_id(self, device_info: Dict) -> str:
        """إنشاء معرف فريد للجهاز"""
        import hashlib
        
        # استخدام معلومات الجهاز لإنشاء معرف فريد
        device_string = f"{device_info.get('user_agent', '')}{device_info.get('screen_width', 0)}{device_info.get('screen_height', 0)}"
        return hashlib.md5(device_string.encode()).hexdigest()[:16]
    
    def _update_usage_stats(self, device_profile: DeviceProfile):
        """تحديث إحصائيات الاستخدام"""
        # تحديث إحصائيات أنواع الأجهزة
        device_type = device_profile.device_type
        if device_type not in self.usage_stats['device_types']:
            self.usage_stats['device_types'][device_type] = 0
        self.usage_stats['device_types'][device_type] += 1
        
        # تحديث إحصائيات أنواع الاتصال
        connection_type = device_profile.connection_type
        if connection_type not in self.usage_stats['connection_types']:
            self.usage_stats['connection_types'][connection_type] = 0
        self.usage_stats['connection_types'][connection_type] += 1
        
        # تحديث إحصائيات مستويات التحسين
        optimization_level = device_profile.optimization_level
        if optimization_level not in self.usage_stats['optimization_levels']:
            self.usage_stats['optimization_levels'][optimization_level] = 0
        self.usage_stats['optimization_levels'][optimization_level] += 1
    
    def _get_recommended_features(self, device_type: str) -> List[str]:
        """الحصول على الميزات الموصى بها للجهاز"""
        recommended = []
        
        for feature_name, feature_info in self.simplified_features.items():
            if device_type in feature_info['enabled_for']:
                recommended.append({
                    'name': feature_name,
                    'description': feature_info['description']
                })
        
        return recommended
    
    def _get_optimization_settings(self, device_type: str) -> Dict:
        """الحصول على إعدادات التحسين للجهاز"""
        if device_type in self.optimization_presets:
            settings = self.optimization_presets[device_type]
            return {
                'compress_images': settings.compress_images,
                'image_quality': settings.image_quality,
                'max_image_width': settings.max_image_width,
                'max_image_height': settings.max_image_height,
                'enable_lazy_loading': settings.enable_lazy_loading,
                'reduce_animations': settings.reduce_animations,
                'minimize_javascript': settings.minimize_javascript,
                'compress_responses': settings.compress_responses,
                'cache_aggressively': settings.cache_aggressively,
                'use_webp_format': settings.use_webp_format,
                'enable_offline_mode': settings.enable_offline_mode
            }
        
        return {}
    
    def _optimize_images(self, images: List[Dict], optimization_settings: OptimizationSettings) -> List[Dict]:
        """تحسين الصور للجهاز"""
        optimized_images = []
        
        for image in images:
            try:
                # تحسين حجم الصورة
                if optimization_settings.compress_images:
                    optimized_image = self._resize_and_compress_image(
                        image, 
                        optimization_settings.max_image_width,
                        optimization_settings.max_image_height,
                        optimization_settings.image_quality
                    )
                    optimized_images.append(optimized_image)
                else:
                    optimized_images.append(image)
                    
            except Exception as e:
                current_app.logger.error(f"خطأ في تحسين الصورة: {str(e)}")
                optimized_images.append(image)  # استخدام الصورة الأصلية في حالة الخطأ
        
        return optimized_images
    
    def _resize_and_compress_image(self, image_data: Dict, max_width: int, max_height: int, quality: int) -> Dict:
        """تغيير حجم وضغط الصورة"""
        try:
            # في التطبيق الحقيقي، سيتم معالجة الصورة الفعلية
            # هنا نحاكي العملية
            
            original_size = image_data.get('size_bytes', 0)
            
            # محاكاة تقليل الحجم
            compression_ratio = quality / 100
            new_size = int(original_size * compression_ratio)
            
            optimized_image = image_data.copy()
            optimized_image.update({
                'width': min(image_data.get('width', max_width), max_width),
                'height': min(image_data.get('height', max_height), max_height),
                'size_bytes': new_size,
                'quality': quality,
                'optimized': True
            })
            
            return optimized_image
            
        except Exception as e:
            current_app.logger.error(f"خطأ في معالجة الصورة: {str(e)}")
            return image_data
    
    def _optimize_text(self, text_data: Dict, optimization_settings: OptimizationSettings) -> Dict:
        """تحسين النصوص للجهاز"""
        optimized_text = text_data.copy()
        
        # تقليل النصوص للأجهزة الضعيفة جداً
        if optimization_settings.minimize_javascript:
            # إزالة النصوص غير الضرورية
            if 'description' in optimized_text and len(optimized_text['description']) > 200:
                optimized_text['description'] = optimized_text['description'][:200] + '...'
        
        return optimized_text
    
    def _compress_data(self, data: Dict) -> Dict:
        """ضغط البيانات"""
        try:
            # تحويل البيانات إلى JSON
            json_data = json.dumps(data, ensure_ascii=False)
            
            # ضغط البيانات
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            # تحويل إلى base64 للنقل
            compressed_base64 = base64.b64encode(compressed_data).decode('utf-8')
            
            return {
                'compressed': True,
                'data': compressed_base64,
                'original_size': len(json_data),
                'compressed_size': len(compressed_base64),
                'compression_ratio': len(compressed_base64) / len(json_data)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في ضغط البيانات: {str(e)}")
            return data
    
    def _get_adaptive_features(self, device_profile: DeviceProfile) -> List[str]:
        """الحصول على الميزات التكيفية للجهاز"""
        features = []
        
        if device_profile.device_type in [DeviceType.VERY_LOW_END.value, DeviceType.LOW_END.value]:
            features.extend([
                'text_only_mode',
                'offline_sync',
                'data_saver_mode',
                'simplified_navigation',
                'reduced_animations'
            ])
        
        if device_profile.connection_speed_kbps < 1024:
            features.extend([
                'progressive_loading',
                'image_compression',
                'lazy_loading'
            ])
        
        if device_profile.battery_level < 30 or device_profile.is_low_power_mode:
            features.extend([
                'dark_mode',
                'reduced_background_activity',
                'minimal_animations'
            ])
        
        return list(set(features))  # إزالة التكرارات
    
    def _compress_offline_data(self, offline_package: Dict) -> Dict:
        """ضغط بيانات الوضع غير المتصل"""
        try:
            # ضغط البيانات الأساسية
            essential_data = offline_package['essential_data']
            
            # تقليل البيانات للحد الأدنى
            compressed_data = {
                'user_profile': {
                    'id': essential_data['user_profile'].get('id'),
                    'name': essential_data['user_profile'].get('name'),
                    'age': essential_data['user_profile'].get('age'),
                    'blood_type': essential_data['user_profile'].get('blood_type')
                },
                'medications': [
                    {
                        'id': med.get('id'),
                        'name': med.get('name'),
                        'dosage': med.get('dosage'),
                        'schedule': med.get('schedule')
                    }
                    for med in essential_data.get('medications', [])[:10]  # أول 10 أدوية فقط
                ],
                'emergency_contacts': essential_data.get('emergency_contacts', [])[:5]  # أول 5 جهات اتصال
            }
            
            offline_package['essential_data'] = compressed_data
            offline_package['compressed'] = True
            
            return offline_package
            
        except Exception as e:
            current_app.logger.error(f"خطأ في ضغط البيانات غير المتصلة: {str(e)}")
            return offline_package
    
    def _estimate_offline_storage(self, offline_package: Dict) -> float:
        """تقدير مساحة التخزين المطلوبة للوضع غير المتصل"""
        try:
            package_size = len(json.dumps(offline_package))
            return round(package_size / (1024 * 1024), 2)  # بالميجابايت
        except:
            return 1.0  # تقدير افتراضي
    
    def _get_sync_instructions(self, device_profile: DeviceProfile) -> Dict:
        """الحصول على تعليمات المزامنة للجهاز"""
        instructions = {
            'sync_frequency': 'كل 6 ساعات',
            'sync_on_wifi_only': True,
            'compress_sync_data': True,
            'batch_size': 50
        }
        
        if device_profile.device_type == DeviceType.VERY_LOW_END.value:
            instructions.update({
                'sync_frequency': 'كل 12 ساعة',
                'batch_size': 20,
                'sync_critical_only': True
            })
        elif device_profile.device_type == DeviceType.LOW_END.value:
            instructions.update({
                'sync_frequency': 'كل 8 ساعات',
                'batch_size': 30
            })
        
        return instructions
    
    def _sync_medication_record(self, data: Dict) -> Dict:
        """مزامنة سجل تناول الدواء"""
        try:
            # في التطبيق الحقيقي، سيتم حفظ البيانات في قاعدة البيانات
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _sync_health_measurement(self, data: Dict) -> Dict:
        """مزامنة القياس الصحي"""
        try:
            # في التطبيق الحقيقي، سيتم حفظ البيانات في قاعدة البيانات
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _sync_profile_update(self, data: Dict) -> Dict:
        """مزامنة تحديث الملف الشخصي"""
        try:
            # في التطبيق الحقيقي، سيتم تحديث البيانات في قاعدة البيانات
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _sync_appointment_note(self, data: Dict) -> Dict:
        """مزامنة ملاحظة الموعد"""
        try:
            # في التطبيق الحقيقي، سيتم حفظ البيانات في قاعدة البيانات
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _create_update_package(self, device_id: str, last_sync: str) -> Dict:
        """إنشاء حزمة التحديث للجهاز"""
        try:
            # في التطبيق الحقيقي، سيتم جمع التحديثات من قاعدة البيانات
            update_package = {
                'device_id': device_id,
                'updates': [],
                'new_notifications': [],
                'medication_reminders': [],
                'appointment_updates': [],
                'system_messages': []
            }
            
            return update_package
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء حزمة التحديث: {str(e)}")
            return {}
    
    def _calculate_optimization_effectiveness(self, device_id: str) -> Dict:
        """حساب فعالية التحسين للجهاز"""
        try:
            # في التطبيق الحقيقي، سيتم حساب المقاييس الفعلية
            return {
                'load_time_improvement': '45%',
                'data_usage_reduction': '60%',
                'battery_savings': '25%',
                'user_satisfaction': '85%'
            }
        except:
            return {}
    
    def _calculate_average_performance(self) -> Dict:
        """حساب متوسط الأداء لجميع الأجهزة"""
        try:
            # في التطبيق الحقيقي، سيتم حساب المتوسطات الفعلية
            return {
                'average_load_time_ms': 2500,
                'average_data_usage_mb': 15,
                'average_battery_usage_percent': 8,
                'average_user_rating': 4.2
            }
        except:
            return {}
    
    def _get_optimization_stats(self) -> Dict:
        """الحصول على إحصائيات التحسين"""
        try:
            total_optimizations = sum(self.usage_stats['optimization_levels'].values())
            
            return {
                'total_optimizations_applied': total_optimizations,
                'optimization_level_distribution': self.usage_stats['optimization_levels'],
                'most_common_optimization': max(self.usage_stats['optimization_levels'], key=self.usage_stats['optimization_levels'].get) if self.usage_stats['optimization_levels'] else 'لا يوجد',
                'optimization_success_rate': '92%'
            }
        except:
            return {}
    
    def _get_performance_recommendations(self) -> List[str]:
        """الحصول على توصيات الأداء"""
        recommendations = []
        
        # تحليل توزيع الأجهزة
        device_stats = self.usage_stats['device_types']
        total_devices = sum(device_stats.values()) if device_stats else 1
        
        low_end_percentage = (device_stats.get(DeviceType.LOW_END.value, 0) + 
                             device_stats.get(DeviceType.VERY_LOW_END.value, 0)) / total_devices * 100
        
        if low_end_percentage > 30:
            recommendations.append("نسبة عالية من الأجهزة الضعيفة، يُنصح بتحسين الأداء العام")
        
        # تحليل أنواع الاتصال
        connection_stats = self.usage_stats['connection_types']
        slow_connection_percentage = (connection_stats.get(ConnectionType.MOBILE_2G.value, 0) + 
                                    connection_stats.get(ConnectionType.MOBILE_3G.value, 0)) / total_devices * 100
        
        if slow_connection_percentage > 20:
            recommendations.append("نسبة عالية من الاتصالات البطيئة، يُنصح بتحسين ضغط البيانات")
        
        if not recommendations:
            recommendations.append("الأداء العام جيد، استمر في المراقبة")
        
        return recommendations

