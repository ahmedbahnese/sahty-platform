"""
خدمة الخرائط والمواقع الجغرافية
"""

import os
import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from flask import current_app
import math

class MapsService:
    def __init__(self):
        """تهيئة خدمة الخرائط"""
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_API_KEY')
        self.mapbox_api_key = os.getenv('MAPBOX_API_KEY', 'YOUR_API_KEY')
        
        # إعدادات الخرائط
        self.default_zoom = 15
        self.search_radius = 10000  # 10 كم
        
        # مواقع المستشفيات والعيادات في مصر (بيانات وهمية)
        self.healthcare_facilities = [
            {
                'id': 1,
                'name': 'مستشفى القاهرة الجديدة',
                'type': 'hospital',
                'lat': 30.0444,
                'lng': 31.2357,
                'address': 'التجمع الأول، القاهرة الجديدة',
                'phone': '0227584000',
                'emergency': True,
                'specialties': ['طوارئ', 'قلب', 'جراحة', 'أطفال'],
                'rating': 4.5,
                'working_hours': '24/7'
            },
            {
                'id': 2,
                'name': 'مستشفى دار الفؤاد',
                'type': 'hospital',
                'lat': 30.0626,
                'lng': 31.2497,
                'address': 'مدينة نصر، القاهرة',
                'phone': '0225555555',
                'emergency': True,
                'specialties': ['قلب', 'أعصاب', 'عظام'],
                'rating': 4.8,
                'working_hours': '24/7'
            },
            {
                'id': 3,
                'name': 'عيادة الدكتور أحمد محمد',
                'type': 'clinic',
                'lat': 30.0505,
                'lng': 31.2400,
                'address': 'شارع التحرير، وسط البلد',
                'phone': '0223456789',
                'emergency': False,
                'specialties': ['باطنة', 'قلب'],
                'rating': 4.2,
                'working_hours': '9:00 AM - 9:00 PM'
            },
            {
                'id': 4,
                'name': 'مستشفى الإسكندرية الدولي',
                'type': 'hospital',
                'lat': 31.2001,
                'lng': 29.9187,
                'address': 'سموحة، الإسكندرية',
                'phone': '0334567890',
                'emergency': True,
                'specialties': ['طوارئ', 'جراحة', 'نساء وتوليد'],
                'rating': 4.6,
                'working_hours': '24/7'
            },
            {
                'id': 5,
                'name': 'صيدلية العزبي',
                'type': 'pharmacy',
                'lat': 30.0444,
                'lng': 31.2357,
                'address': 'شارع الجامعة، الجيزة',
                'phone': '0233334444',
                'emergency': False,
                'specialties': ['أدوية عامة', 'مستحضرات تجميل'],
                'rating': 4.0,
                'working_hours': '8:00 AM - 12:00 AM'
            }
        ]
    
    def find_nearby_facilities(self, lat: float, lng: float, facility_type: str = None, 
                             specialty: str = None, radius: int = None) -> List[Dict]:
        """
        البحث عن المرافق الطبية القريبة
        
        Args:
            lat: خط العرض
            lng: خط الطول
            facility_type: نوع المرفق (hospital, clinic, pharmacy)
            specialty: التخصص المطلوب
            radius: نطاق البحث بالمتر
            
        Returns:
            List[Dict]: قائمة المرافق القريبة
        """
        try:
            search_radius = radius or self.search_radius
            nearby_facilities = []
            
            for facility in self.healthcare_facilities:
                # حساب المسافة
                distance = self._calculate_distance(
                    lat, lng, facility['lat'], facility['lng']
                )
                
                # فلترة حسب المسافة
                if distance <= search_radius:
                    # فلترة حسب النوع
                    if facility_type and facility['type'] != facility_type:
                        continue
                    
                    # فلترة حسب التخصص
                    if specialty and specialty not in facility['specialties']:
                        continue
                    
                    facility_with_distance = facility.copy()
                    facility_with_distance['distance'] = distance
                    facility_with_distance['distance_text'] = self._format_distance(distance)
                    
                    # حساب وقت الوصول التقديري
                    facility_with_distance['estimated_time'] = self._estimate_travel_time(distance)
                    
                    nearby_facilities.append(facility_with_distance)
            
            # ترتيب حسب المسافة
            nearby_facilities.sort(key=lambda x: x['distance'])
            
            return nearby_facilities
            
        except Exception as e:
            current_app.logger.error(f"خطأ في البحث عن المرافق القريبة: {str(e)}")
            return []
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """حساب المسافة بين نقطتين باستخدام معادلة Haversine"""
        R = 6371000  # نصف قطر الأرض بالمتر
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) * math.sin(delta_lng / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def _format_distance(self, distance: float) -> str:
        """تنسيق المسافة للعرض"""
        if distance < 1000:
            return f"{int(distance)} متر"
        else:
            return f"{distance / 1000:.1f} كم"
    
    def _estimate_travel_time(self, distance: float) -> str:
        """تقدير وقت الوصول"""
        # افتراض سرعة متوسطة 30 كم/ساعة في المدينة
        time_hours = distance / 1000 / 30
        time_minutes = time_hours * 60
        
        if time_minutes < 60:
            return f"{int(time_minutes)} دقيقة"
        else:
            hours = int(time_minutes // 60)
            minutes = int(time_minutes % 60)
            return f"{hours} ساعة {minutes} دقيقة"
    
    def get_directions(self, origin_lat: float, origin_lng: float, 
                      dest_lat: float, dest_lng: float, mode: str = 'driving') -> Dict:
        """
        الحصول على اتجاهات الطريق
        
        Args:
            origin_lat: خط عرض نقطة البداية
            origin_lng: خط طول نقطة البداية
            dest_lat: خط عرض الوجهة
            dest_lng: خط طول الوجهة
            mode: وسيلة النقل (driving, walking, transit)
            
        Returns:
            Dict: تفاصيل الطريق
        """
        try:
            # في التطبيق الحقيقي، سيتم استدعاء Google Directions API
            # هنا محاكاة للاستجابة
            
            distance = self._calculate_distance(origin_lat, origin_lng, dest_lat, dest_lng)
            
            # محاكاة خطوات الطريق
            steps = [
                {
                    'instruction': 'اتجه شمالاً في شارع التحرير',
                    'distance': '500 متر',
                    'duration': '2 دقيقة'
                },
                {
                    'instruction': 'انعطف يميناً إلى شارع قصر العيني',
                    'distance': '1.2 كم',
                    'duration': '5 دقائق'
                },
                {
                    'instruction': 'استمر مستقيماً حتى تصل للوجهة',
                    'distance': '800 متر',
                    'duration': '3 دقائق'
                }
            ]
            
            return {
                'success': True,
                'route': {
                    'distance': self._format_distance(distance),
                    'duration': self._estimate_travel_time(distance),
                    'steps': steps,
                    'polyline': self._generate_polyline(origin_lat, origin_lng, dest_lat, dest_lng)
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على الاتجاهات: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_polyline(self, lat1: float, lng1: float, lat2: float, lng2: float) -> str:
        """إنتاج polyline للطريق (مبسط)"""
        # في التطبيق الحقيقي، سيتم الحصول على polyline من API الخرائط
        return f"polyline_from_{lat1}_{lng1}_to_{lat2}_{lng2}"
    
    def geocode_address(self, address: str) -> Dict:
        """
        تحويل العنوان إلى إحداثيات
        
        Args:
            address: العنوان النصي
            
        Returns:
            Dict: الإحداثيات والمعلومات
        """
        try:
            # في التطبيق الحقيقي، سيتم استدعاء Geocoding API
            # هنا محاكاة للاستجابة
            
            # قاموس العناوين المعروفة (للمحاكاة)
            known_addresses = {
                'التحرير': {'lat': 30.0444, 'lng': 31.2357, 'formatted_address': 'ميدان التحرير، القاهرة'},
                'مدينة نصر': {'lat': 30.0626, 'lng': 31.2497, 'formatted_address': 'مدينة نصر، القاهرة'},
                'الإسكندرية': {'lat': 31.2001, 'lng': 29.9187, 'formatted_address': 'الإسكندرية، مصر'},
                'الجيزة': {'lat': 30.0131, 'lng': 31.2089, 'formatted_address': 'الجيزة، مصر'}
            }
            
            # البحث عن العنوان
            for key, location in known_addresses.items():
                if key.lower() in address.lower():
                    return {
                        'success': True,
                        'location': location
                    }
            
            # إذا لم يتم العثور على العنوان، إرجاع موقع افتراضي
            return {
                'success': True,
                'location': {
                    'lat': 30.0444,
                    'lng': 31.2357,
                    'formatted_address': 'القاهرة، مصر'
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحويل العنوان: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def reverse_geocode(self, lat: float, lng: float) -> Dict:
        """
        تحويل الإحداثيات إلى عنوان
        
        Args:
            lat: خط العرض
            lng: خط الطول
            
        Returns:
            Dict: العنوان والمعلومات
        """
        try:
            # في التطبيق الحقيقي، سيتم استدعاء Reverse Geocoding API
            # هنا محاكاة للاستجابة
            
            # تحديد المنطقة بناءً على الإحداثيات
            if 30.0 <= lat <= 30.1 and 31.2 <= lng <= 31.3:
                area = "القاهرة"
            elif 31.1 <= lat <= 31.3 and 29.8 <= lng <= 30.0:
                area = "الإسكندرية"
            elif 29.9 <= lat <= 30.1 and 31.1 <= lng <= 31.3:
                area = "الجيزة"
            else:
                area = "مصر"
            
            return {
                'success': True,
                'address': {
                    'formatted_address': f"{area}، مصر",
                    'city': area,
                    'country': 'مصر',
                    'postal_code': '12345'
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحويل الإحداثيات: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_traffic_info(self, lat: float, lng: float, radius: int = 5000) -> Dict:
        """
        الحصول على معلومات حركة المرور
        
        Args:
            lat: خط العرض
            lng: خط الطول
            radius: نطاق البحث بالمتر
            
        Returns:
            Dict: معلومات حركة المرور
        """
        try:
            # محاكاة معلومات حركة المرور
            traffic_conditions = [
                {
                    'road': 'شارع التحرير',
                    'condition': 'كثيف',
                    'speed': 15,  # كم/ساعة
                    'delay': '10 دقائق إضافية'
                },
                {
                    'road': 'كوبري قصر النيل',
                    'condition': 'متوسط',
                    'speed': 25,
                    'delay': '5 دقائق إضافية'
                },
                {
                    'road': 'شارع الهرم',
                    'condition': 'سلس',
                    'speed': 40,
                    'delay': 'لا توجد تأخيرات'
                }
            ]
            
            return {
                'success': True,
                'traffic_info': {
                    'overall_condition': 'متوسط',
                    'average_speed': 27,
                    'roads': traffic_conditions,
                    'last_updated': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على معلومات المرور: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def find_parking(self, lat: float, lng: float, radius: int = 1000) -> List[Dict]:
        """
        البحث عن أماكن الانتظار القريبة
        
        Args:
            lat: خط العرض
            lng: خط الطول
            radius: نطاق البحث بالمتر
            
        Returns:
            List[Dict]: قائمة أماكن الانتظار
        """
        try:
            # محاكاة أماكن الانتظار
            parking_spots = [
                {
                    'id': 1,
                    'name': 'موقف مستشفى القاهرة الجديدة',
                    'lat': 30.0440,
                    'lng': 31.2360,
                    'type': 'hospital_parking',
                    'capacity': 200,
                    'available_spots': 45,
                    'hourly_rate': 5.0,
                    'max_hours': 24,
                    'features': ['مظلل', 'أمان', 'قريب من المدخل']
                },
                {
                    'id': 2,
                    'name': 'موقف عام - شارع التحرير',
                    'lat': 30.0450,
                    'lng': 31.2350,
                    'type': 'public_parking',
                    'capacity': 50,
                    'available_spots': 12,
                    'hourly_rate': 3.0,
                    'max_hours': 8,
                    'features': ['مراقب', 'إضاءة ليلية']
                }
            ]
            
            # فلترة حسب المسافة
            nearby_parking = []
            for spot in parking_spots:
                distance = self._calculate_distance(lat, lng, spot['lat'], spot['lng'])
                if distance <= radius:
                    spot['distance'] = distance
                    spot['distance_text'] = self._format_distance(distance)
                    nearby_parking.append(spot)
            
            # ترتيب حسب المسافة
            nearby_parking.sort(key=lambda x: x['distance'])
            
            return nearby_parking
            
        except Exception as e:
            current_app.logger.error(f"خطأ في البحث عن أماكن الانتظار: {str(e)}")
            return []
    
    def get_public_transport(self, origin_lat: float, origin_lng: float,
                           dest_lat: float, dest_lng: float) -> Dict:
        """
        الحصول على خيارات النقل العام
        
        Args:
            origin_lat: خط عرض نقطة البداية
            origin_lng: خط طول نقطة البداية
            dest_lat: خط عرض الوجهة
            dest_lng: خط طول الوجهة
            
        Returns:
            Dict: خيارات النقل العام
        """
        try:
            # محاكاة خيارات النقل العام
            transport_options = [
                {
                    'type': 'metro',
                    'route': 'الخط الأول - المرج ← حلوان',
                    'stations': ['السادات', 'جمال عبد الناصر', 'أحمد عرابي'],
                    'duration': '25 دقيقة',
                    'cost': 3.0,
                    'walking_distance': '400 متر'
                },
                {
                    'type': 'bus',
                    'route': 'خط 54 - التحرير ← مدينة نصر',
                    'stops': ['ميدان التحرير', 'رمسيس', 'مدينة نصر'],
                    'duration': '35 دقيقة',
                    'cost': 2.0,
                    'walking_distance': '200 متر'
                },
                {
                    'type': 'microbus',
                    'route': 'ميكروباص - التحرير ← النزهة',
                    'duration': '20 دقيقة',
                    'cost': 5.0,
                    'walking_distance': '100 متر'
                }
            ]
            
            return {
                'success': True,
                'transport_options': transport_options,
                'total_options': len(transport_options)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على النقل العام: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

