"""
خدمة البحث الذكي الموحد والبحث المتقدم
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
import difflib
from collections import defaultdict
import math

class SearchType(Enum):
    DOCTORS = "أطباء"
    HOSPITALS = "مستشفيات"
    PHARMACIES = "صيدليات"
    MEDICATIONS = "أدوية"
    MEDICAL_CONDITIONS = "حالات طبية"
    SYMPTOMS = "أعراض"
    TESTS = "فحوصات"
    PROCEDURES = "إجراءات"
    INSURANCE = "تأمين"
    ARTICLES = "مقالات"
    VIDEOS = "فيديوهات"
    APPOINTMENTS = "مواعيد"
    USERS = "مستخدمين"
    LOCATIONS = "مواقع"

class SearchFilter(Enum):
    LOCATION = "موقع"
    SPECIALTY = "تخصص"
    RATING = "تقييم"
    PRICE = "سعر"
    AVAILABILITY = "متاح"
    INSURANCE_ACCEPTED = "يقبل التأمين"
    LANGUAGE = "لغة"
    GENDER = "جنس"
    EXPERIENCE = "خبرة"
    DISTANCE = "مسافة"

class SortBy(Enum):
    RELEVANCE = "صلة"
    RATING = "تقييم"
    DISTANCE = "مسافة"
    PRICE = "سعر"
    AVAILABILITY = "توفر"
    EXPERIENCE = "خبرة"
    REVIEWS = "مراجعات"
    RECENT = "حديث"

@dataclass
class SearchResult:
    result_id: str
    result_type: str
    title: str
    description: str
    relevance_score: float
    metadata: Dict
    thumbnail: Optional[str]
    url: Optional[str]

@dataclass
class SearchQuery:
    query_id: str
    user_id: str
    query_text: str
    search_types: List[str]
    filters: Dict
    sort_by: str
    location: Optional[Dict]
    timestamp: datetime

class SmartSearchService:
    def __init__(self):
        """تهيئة خدمة البحث الذكي"""
        
        # إعدادات البحث
        self.search_settings = {
            'max_results_per_type': 20,
            'min_relevance_score': 0.3,
            'fuzzy_match_threshold': 0.7,
            'auto_complete_min_chars': 2,
            'search_history_limit': 100,
            'trending_searches_limit': 50,
            'cache_duration_minutes': 30
        }
        
        # قواعد البيانات للبحث (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.search_index = {
            SearchType.DOCTORS.value: [],
            SearchType.HOSPITALS.value: [],
            SearchType.PHARMACIES.value: [],
            SearchType.MEDICATIONS.value: [],
            SearchType.MEDICAL_CONDITIONS.value: [],
            SearchType.SYMPTOMS.value: [],
            SearchType.TESTS.value: [],
            SearchType.PROCEDURES.value: [],
            SearchType.INSURANCE.value: [],
            SearchType.ARTICLES.value: [],
            SearchType.VIDEOS.value: [],
            SearchType.APPOINTMENTS.value: [],
            SearchType.USERS.value: [],
            SearchType.LOCATIONS.value: []
        }
        
        # فهرس الكلمات المفتاحية
        self.keyword_index = defaultdict(list)
        
        # تاريخ البحث
        self.search_history = {}
        self.trending_searches = []
        self.search_analytics = {}
        
        # ذاكرة التخزين المؤقت
        self.search_cache = {}
        
        # المرادفات والكلمات ذات الصلة
        self.synonyms = {
            'طبيب': ['دكتور', 'استشاري', 'أخصائي', 'طبيبة'],
            'مستشفى': ['مستشفيات', 'مركز طبي', 'عيادة', 'مجمع طبي'],
            'صيدلية': ['صيدليات', 'أدوية', 'دواء'],
            'قلب': ['قلبية', 'قلبي', 'كارديو', 'قلوب'],
            'عظام': ['عظمية', 'عظمي', 'أورثو', 'عظم'],
            'أطفال': ['طفل', 'أطفال', 'بيدياتري', 'طفولة'],
            'نساء': ['نسائية', 'توليد', 'أمراض نساء', 'نسا'],
            'عيون': ['عينية', 'عين', 'بصر', 'رؤية'],
            'أسنان': ['سنية', 'سن', 'فم', 'أسنان'],
            'جلدية': ['جلد', 'تجميل', 'بشرة'],
            'نفسية': ['نفسي', 'عقلية', 'سلوكية'],
            'باطنة': ['باطني', 'داخلية', 'عامة'],
            'جراحة': ['جراح', 'عمليات', 'جراحي'],
            'أنف': ['أذن', 'حنجرة', 'أنف وأذن'],
            'مخ': ['أعصاب', 'عصبية', 'نيورو'],
            'كلى': ['كلوية', 'كلية', 'مسالك'],
            'صدر': ['صدرية', 'رئة', 'تنفسي'],
            'هضمي': ['معدة', 'أمعاء', 'كبد', 'هضم'],
            'غدد': ['هرمونات', 'سكري', 'غدة'],
            'دم': ['دموية', 'أورام', 'سرطان'],
            'تحليل': ['فحص', 'اختبار', 'تحاليل'],
            'أشعة': ['سونار', 'رنين', 'أشعة سينية', 'مقطعية'],
            'عملية': ['جراحة', 'إجراء', 'تدخل'],
            'دواء': ['علاج', 'حبوب', 'شراب', 'حقن'],
            'ألم': ['وجع', 'مؤلم', 'يؤلم'],
            'حمى': ['سخونة', 'حرارة', 'سخونية'],
            'صداع': ['رأس', 'صداع نصفي', 'شقيقة'],
            'سعال': ['كحة', 'سعلة', 'كح'],
            'إسهال': ['براز', 'معدة', 'أمعاء'],
            'إمساك': ['قبض', 'صعوبة إخراج'],
            'غثيان': ['قيء', 'استفراغ', 'ميل للقيء'],
            'دوخة': ['دوار', 'عدم توازن', 'دوران'],
            'تعب': ['إرهاق', 'إجهاد', 'تعب عام'],
            'أرق': ['سهر', 'عدم نوم', 'قلة نوم'],
            'اكتئاب': ['حزن', 'يأس', 'كآبة'],
            'قلق': ['توتر', 'خوف', 'قلق نفسي'],
            'ضغط': ['ضغط دم', 'هايبر تنشن'],
            'سكر': ['سكري', 'ديابيتس', 'جلوكوز'],
            'كوليسترول': ['دهون', 'شحوم', 'كوليستيرول'],
            'فيتامين': ['فيتامينات', 'مكملات', 'مقويات'],
            'مضاد': ['مضادات', 'أنتيبيوتيك', 'مضاد حيوي'],
            'مسكن': ['مسكنات', 'مخفف ألم', 'باراسيتامول'],
            'مضاد التهاب': ['مضادات التهاب', 'كورتيزون'],
            'حساسية': ['أليرجي', 'حساسيات', 'تحسس'],
            'تطعيم': ['تطعيمات', 'لقاح', 'تحصين'],
            'حمل': ['حامل', 'حوامل', 'ولادة'],
            'طفل': ['رضيع', 'مولود', 'طفولة'],
            'مسن': ['كبار السن', 'مسنين', 'شيخوخة'],
            'طوارئ': ['إسعاف', 'عاجل', 'حالة طارئة'],
            'عيادة': ['عيادات', 'مركز', 'مجمع'],
            'مختبر': ['معمل', 'تحاليل', 'فحوصات'],
            'أشعة': ['تصوير', 'سكان', 'رنين'],
            'تأمين': ['تأمينات', 'ضمان صحي', 'تغطية'],
            'تكلفة': ['سعر', 'تكاليف', 'رسوم'],
            'موعد': ['حجز', 'ميعاد', 'موعد طبي'],
            'استشارة': ['استشارات', 'رأي طبي', 'نصيحة'],
            'متابعة': ['مراجعة', 'كشف دوري', 'فحص دوري'],
            'علاج': ['معالجة', 'شفاء', 'دواء'],
            'وقاية': ['منع', 'حماية', 'تجنب'],
            'تشخيص': ['كشف', 'تحديد', 'معرفة المرض'],
            'أعراض': ['علامات', 'مؤشرات', 'دلائل'],
            'مرض': ['مشكلة صحية', 'حالة مرضية', 'علة'],
            'صحة': ['صحي', 'سلامة', 'عافية'],
            'لياقة': ['رياضة', 'تمارين', 'نشاط بدني'],
            'تغذية': ['طعام', 'غذاء', 'نظام غذائي'],
            'وزن': ['سمنة', 'نحافة', 'كتلة الجسم'],
            'ضغط نفسي': ['توتر', 'إجهاد نفسي', 'ضغوط'],
            'نوم': ['راحة', 'استرخاء', 'هدوء'],
            'تدخين': ['سجائر', 'تبغ', 'نيكوتين'],
            'كحول': ['خمر', 'مشروبات كحولية', 'إدمان'],
            'مخدرات': ['مواد مخدرة', 'إدمان', 'مؤثرات عقلية']
        }
        
        # تهيئة البيانات التجريبية
        self._initialize_sample_data()
    
    def search(self, search_data: Dict) -> Dict:
        """
        البحث الذكي الموحد
        
        Args:
            search_data: بيانات البحث
            
        Returns:
            Dict: نتائج البحث
        """
        try:
            user_id = search_data.get('user_id')
            query_text = search_data.get('query', '').strip()
            search_types = search_data.get('types', list(SearchType))
            filters = search_data.get('filters', {})
            sort_by = search_data.get('sort_by', SortBy.RELEVANCE.value)
            location = search_data.get('location')
            page = search_data.get('page', 1)
            per_page = search_data.get('per_page', 20)
            
            if not query_text:
                return {
                    'success': False,
                    'error': 'نص البحث مطلوب'
                }
            
            # إنشاء معرف البحث
            query_id = str(uuid.uuid4())
            
            # إنشاء كائن البحث
            search_query = SearchQuery(
                query_id=query_id,
                user_id=user_id,
                query_text=query_text,
                search_types=search_types,
                filters=filters,
                sort_by=sort_by,
                location=location,
                timestamp=datetime.now()
            )
            
            # فحص ذاكرة التخزين المؤقت
            cache_key = self._generate_cache_key(search_query)
            cached_results = self._get_cached_results(cache_key)
            if cached_results:
                return cached_results
            
            # معالجة النص وتحسينه
            processed_query = self._process_query_text(query_text)
            
            # البحث في جميع الأنواع المطلوبة
            all_results = []
            
            for search_type in search_types:
                if isinstance(search_type, str):
                    type_results = self._search_by_type(
                        search_type, processed_query, filters, location
                    )
                    all_results.extend(type_results)
            
            # ترتيب النتائج
            sorted_results = self._sort_results(all_results, sort_by, location)
            
            # تطبيق التصفح
            total_results = len(sorted_results)
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            paginated_results = sorted_results[start_index:end_index]
            
            # تجميع النتائج حسب النوع
            grouped_results = self._group_results_by_type(paginated_results)
            
            # إضافة اقتراحات ذكية
            suggestions = self._generate_suggestions(query_text, all_results)
            
            # حفظ البحث في التاريخ
            self._save_search_history(search_query, total_results)
            
            # تحديث الإحصائيات
            self._update_search_analytics(search_query, total_results)
            
            # حفظ في ذاكرة التخزين المؤقت
            search_results = {
                'success': True,
                'query_id': query_id,
                'query': query_text,
                'processed_query': processed_query,
                'total_results': total_results,
                'page': page,
                'per_page': per_page,
                'total_pages': math.ceil(total_results / per_page),
                'results': paginated_results,
                'grouped_results': grouped_results,
                'suggestions': suggestions,
                'search_time_ms': self._calculate_search_time(),
                'filters_applied': filters,
                'sort_by': sort_by
            }
            
            self._cache_results(cache_key, search_results)
            
            return search_results
            
        except Exception as e:
            current_app.logger.error(f"خطأ في البحث: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في البحث'
            }
    
    def auto_complete(self, query_data: Dict) -> Dict:
        """
        الإكمال التلقائي للبحث
        
        Args:
            query_data: بيانات الاستعلام
            
        Returns:
            Dict: اقتراحات الإكمال التلقائي
        """
        try:
            query_text = query_data.get('query', '').strip()
            search_types = query_data.get('types', list(SearchType))
            limit = query_data.get('limit', 10)
            
            if len(query_text) < self.search_settings['auto_complete_min_chars']:
                return {
                    'success': True,
                    'suggestions': [],
                    'message': f'اكتب على الأقل {self.search_settings["auto_complete_min_chars"]} أحرف'
                }
            
            # جمع الاقتراحات من مصادر مختلفة
            suggestions = []
            
            # اقتراحات من الكلمات المفتاحية
            keyword_suggestions = self._get_keyword_suggestions(query_text, search_types)
            suggestions.extend(keyword_suggestions)
            
            # اقتراحات من تاريخ البحث
            history_suggestions = self._get_history_suggestions(query_text)
            suggestions.extend(history_suggestions)
            
            # اقتراحات من البحثات الشائعة
            trending_suggestions = self._get_trending_suggestions(query_text)
            suggestions.extend(trending_suggestions)
            
            # اقتراحات من المرادفات
            synonym_suggestions = self._get_synonym_suggestions(query_text)
            suggestions.extend(synonym_suggestions)
            
            # إزالة التكرارات وترتيب حسب الصلة
            unique_suggestions = self._deduplicate_suggestions(suggestions)
            sorted_suggestions = sorted(
                unique_suggestions, 
                key=lambda x: x['relevance_score'], 
                reverse=True
            )
            
            # تطبيق الحد الأقصى
            final_suggestions = sorted_suggestions[:limit]
            
            return {
                'success': True,
                'query': query_text,
                'suggestions': final_suggestions,
                'total_suggestions': len(final_suggestions)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الإكمال التلقائي: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الإكمال التلقائي'
            }
    
    def get_trending_searches(self, user_id: str) -> Dict:
        """
        الحصول على البحثات الشائعة
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: البحثات الشائعة
        """
        try:
            # البحثات الشائعة العامة
            general_trending = self._get_general_trending_searches()
            
            # البحثات الشائعة الشخصية
            personal_trending = self._get_personal_trending_searches(user_id)
            
            # البحثات الشائعة حسب الموقع
            location_trending = self._get_location_trending_searches(user_id)
            
            # البحثات الشائعة حسب التخصص
            specialty_trending = self._get_specialty_trending_searches(user_id)
            
            return {
                'success': True,
                'general_trending': general_trending,
                'personal_trending': personal_trending,
                'location_trending': location_trending,
                'specialty_trending': specialty_trending,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على البحثات الشائعة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على البحثات الشائعة'
            }
    
    def get_search_history(self, user_id: str, limit: int = 50) -> Dict:
        """
        الحصول على تاريخ البحث للمستخدم
        
        Args:
            user_id: معرف المستخدم
            limit: عدد النتائج
            
        Returns:
            Dict: تاريخ البحث
        """
        try:
            user_history = self.search_history.get(user_id, [])
            
            # ترتيب حسب التاريخ (الأحدث أولاً)
            sorted_history = sorted(
                user_history, 
                key=lambda x: x['timestamp'], 
                reverse=True
            )
            
            # تطبيق الحد الأقصى
            limited_history = sorted_history[:limit]
            
            # تحليل الإحصائيات
            statistics = self._analyze_search_history(user_history)
            
            return {
                'success': True,
                'search_history': limited_history,
                'total_searches': len(user_history),
                'statistics': statistics
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على تاريخ البحث: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على تاريخ البحث'
            }
    
    def clear_search_history(self, user_id: str) -> Dict:
        """
        مسح تاريخ البحث للمستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: نتيجة المسح
        """
        try:
            if user_id in self.search_history:
                del self.search_history[user_id]
            
            return {
                'success': True,
                'message': 'تم مسح تاريخ البحث بنجاح'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في مسح تاريخ البحث: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في مسح تاريخ البحث'
            }
    
    def advanced_search(self, search_data: Dict) -> Dict:
        """
        البحث المتقدم مع فلاتر معقدة
        
        Args:
            search_data: بيانات البحث المتقدم
            
        Returns:
            Dict: نتائج البحث المتقدم
        """
        try:
            user_id = search_data.get('user_id')
            criteria = search_data.get('criteria', {})
            
            # معايير البحث المتقدم
            specialty = criteria.get('specialty')
            location = criteria.get('location')
            rating_min = criteria.get('rating_min', 0)
            price_range = criteria.get('price_range', {})
            availability = criteria.get('availability')
            insurance_accepted = criteria.get('insurance_accepted')
            language = criteria.get('language')
            gender = criteria.get('gender')
            experience_years = criteria.get('experience_years', 0)
            distance_km = criteria.get('distance_km')
            
            # تطبيق المعايير المعقدة
            filtered_results = []
            
            # البحث في الأطباء
            if criteria.get('search_doctors', True):
                doctor_results = self._advanced_search_doctors(criteria)
                filtered_results.extend(doctor_results)
            
            # البحث في المستشفيات
            if criteria.get('search_hospitals', True):
                hospital_results = self._advanced_search_hospitals(criteria)
                filtered_results.extend(hospital_results)
            
            # البحث في الصيدليات
            if criteria.get('search_pharmacies', True):
                pharmacy_results = self._advanced_search_pharmacies(criteria)
                filtered_results.extend(pharmacy_results)
            
            # ترتيب النتائج حسب المعايير المتقدمة
            sorted_results = self._advanced_sort_results(filtered_results, criteria)
            
            return {
                'success': True,
                'criteria': criteria,
                'results': sorted_results,
                'total_results': len(sorted_results),
                'search_type': 'advanced'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في البحث المتقدم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في البحث المتقدم'
            }
    
    def search_suggestions(self, query_data: Dict) -> Dict:
        """
        اقتراحات البحث الذكية
        
        Args:
            query_data: بيانات الاستعلام
            
        Returns:
            Dict: اقتراحات البحث
        """
        try:
            query_text = query_data.get('query', '').strip()
            user_id = query_data.get('user_id')
            context = query_data.get('context', 'general')
            
            suggestions = []
            
            # اقتراحات حسب السياق
            if context == 'symptoms':
                suggestions.extend(self._get_symptom_suggestions(query_text))
            elif context == 'conditions':
                suggestions.extend(self._get_condition_suggestions(query_text))
            elif context == 'medications':
                suggestions.extend(self._get_medication_suggestions(query_text))
            elif context == 'doctors':
                suggestions.extend(self._get_doctor_suggestions(query_text))
            else:
                suggestions.extend(self._get_general_suggestions(query_text))
            
            # اقتراحات شخصية حسب تاريخ المستخدم
            if user_id:
                personal_suggestions = self._get_personal_suggestions(user_id, query_text)
                suggestions.extend(personal_suggestions)
            
            # ترتيب الاقتراحات
            sorted_suggestions = sorted(
                suggestions, 
                key=lambda x: x.get('relevance_score', 0), 
                reverse=True
            )
            
            return {
                'success': True,
                'query': query_text,
                'context': context,
                'suggestions': sorted_suggestions[:10],
                'total_suggestions': len(sorted_suggestions)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في اقتراحات البحث: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في اقتراحات البحث'
            }
    
    # الدوال المساعدة
    def _initialize_sample_data(self):
        """تهيئة البيانات التجريبية للبحث"""
        
        # أطباء تجريبيون
        sample_doctors = [
            {
                'id': 'doc_001',
                'name': 'د. أحمد محمد علي',
                'specialty': 'قلب وأوعية دموية',
                'hospital': 'مستشفى القاهرة الجديدة',
                'location': 'القاهرة الجديدة',
                'rating': 4.8,
                'experience_years': 15,
                'consultation_fee': 300,
                'languages': ['العربية', 'الإنجليزية'],
                'gender': 'ذكر',
                'available_days': ['الأحد', 'الثلاثاء', 'الخميس'],
                'insurance_accepted': ['التأمين الصحي', 'بوبا', 'ميتلايف'],
                'keywords': ['قلب', 'أوعية دموية', 'ضغط', 'كوليسترول', 'قسطرة']
            },
            {
                'id': 'doc_002',
                'name': 'د. فاطمة أحمد حسن',
                'specialty': 'أطفال',
                'hospital': 'مستشفى الأطفال التخصصي',
                'location': 'المعادي',
                'rating': 4.9,
                'experience_years': 12,
                'consultation_fee': 250,
                'languages': ['العربية'],
                'gender': 'أنثى',
                'available_days': ['السبت', 'الاثنين', 'الأربعاء'],
                'insurance_accepted': ['التأمين الصحي', 'أليانز'],
                'keywords': ['أطفال', 'رضع', 'تطعيمات', 'نمو', 'تغذية']
            },
            {
                'id': 'doc_003',
                'name': 'د. محمد سعد الدين',
                'specialty': 'عظام ومفاصل',
                'hospital': 'مستشفى العظام والمفاصل',
                'location': 'مدينة نصر',
                'rating': 4.7,
                'experience_years': 20,
                'consultation_fee': 400,
                'languages': ['العربية', 'الإنجليزية', 'الفرنسية'],
                'gender': 'ذكر',
                'available_days': ['الأحد', 'الثلاثاء', 'الخميس', 'السبت'],
                'insurance_accepted': ['بوبا', 'ميتلايف', 'أليانز'],
                'keywords': ['عظام', 'مفاصل', 'كسور', 'غضاريف', 'عمود فقري']
            }
        ]
        
        # مستشفيات تجريبية
        sample_hospitals = [
            {
                'id': 'hosp_001',
                'name': 'مستشفى القاهرة الجديدة',
                'type': 'مستشفى عام',
                'location': 'القاهرة الجديدة',
                'rating': 4.6,
                'specialties': ['قلب', 'أطفال', 'جراحة', 'باطنة'],
                'emergency': True,
                'insurance_accepted': ['التأمين الصحي', 'بوبا', 'ميتلايف'],
                'phone': '0227584000',
                'address': 'التجمع الخامس، القاهرة الجديدة',
                'keywords': ['مستشفى', 'عام', 'طوارئ', 'جراحة']
            },
            {
                'id': 'hosp_002',
                'name': 'مستشفى الأطفال التخصصي',
                'type': 'مستشفى تخصصي',
                'location': 'المعادي',
                'rating': 4.8,
                'specialties': ['أطفال', 'حديثي الولادة', 'جراحة أطفال'],
                'emergency': True,
                'insurance_accepted': ['التأمين الصحي', 'أليانز'],
                'phone': '0225264000',
                'address': 'المعادي، القاهرة',
                'keywords': ['أطفال', 'رضع', 'حديثي الولادة', 'تخصصي']
            }
        ]
        
        # صيدليات تجريبية
        sample_pharmacies = [
            {
                'id': 'pharm_001',
                'name': 'صيدلية العزبي',
                'location': 'مدينة نصر',
                'rating': 4.5,
                'services': ['أدوية', 'مستحضرات تجميل', 'أجهزة طبية'],
                'delivery': True,
                'hours': '24 ساعة',
                'phone': '0224567890',
                'address': 'شارع عباس العقاد، مدينة نصر',
                'keywords': ['صيدلية', 'أدوية', 'توصيل', '24 ساعة']
            },
            {
                'id': 'pharm_002',
                'name': 'صيدلية سيف',
                'location': 'المعادي',
                'rating': 4.3,
                'services': ['أدوية', 'فيتامينات', 'مكملات غذائية'],
                'delivery': False,
                'hours': '8 صباحاً - 12 منتصف الليل',
                'phone': '0225123456',
                'address': 'شارع 9، المعادي',
                'keywords': ['صيدلية', 'فيتامينات', 'مكملات']
            }
        ]
        
        # إضافة البيانات للفهرس
        self.search_index[SearchType.DOCTORS.value] = sample_doctors
        self.search_index[SearchType.HOSPITALS.value] = sample_hospitals
        self.search_index[SearchType.PHARMACIES.value] = sample_pharmacies
        
        # بناء فهرس الكلمات المفتاحية
        self._build_keyword_index()
    
    def _build_keyword_index(self):
        """بناء فهرس الكلمات المفتاحية"""
        for search_type, items in self.search_index.items():
            for item in items:
                keywords = item.get('keywords', [])
                for keyword in keywords:
                    self.keyword_index[keyword.lower()].append({
                        'type': search_type,
                        'item': item
                    })
    
    def _process_query_text(self, query_text: str) -> Dict:
        """معالجة وتحسين نص البحث"""
        # تنظيف النص
        cleaned_text = re.sub(r'[^\w\s]', ' ', query_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # تقسيم إلى كلمات
        words = cleaned_text.split()
        
        # إضافة المرادفات
        expanded_words = []
        for word in words:
            expanded_words.append(word)
            if word in self.synonyms:
                expanded_words.extend(self.synonyms[word])
        
        # إزالة التكرارات
        unique_words = list(set(expanded_words))
        
        return {
            'original': query_text,
            'cleaned': cleaned_text,
            'words': words,
            'expanded_words': unique_words,
            'synonyms_used': len(expanded_words) > len(words)
        }
    
    def _search_by_type(self, search_type: str, processed_query: Dict, 
                       filters: Dict, location: Optional[Dict]) -> List[SearchResult]:
        """البحث حسب النوع"""
        results = []
        items = self.search_index.get(search_type, [])
        
        for item in items:
            relevance_score = self._calculate_relevance_score(item, processed_query)
            
            if relevance_score >= self.search_settings['min_relevance_score']:
                # تطبيق الفلاتر
                if self._apply_filters(item, filters, search_type):
                    result = SearchResult(
                        result_id=item.get('id', str(uuid.uuid4())),
                        result_type=search_type,
                        title=item.get('name', 'غير محدد'),
                        description=self._generate_description(item, search_type),
                        relevance_score=relevance_score,
                        metadata=item,
                        thumbnail=item.get('thumbnail'),
                        url=item.get('url')
                    )
                    results.append(result)
        
        return results
    
    def _calculate_relevance_score(self, item: Dict, processed_query: Dict) -> float:
        """حساب درجة الصلة"""
        score = 0.0
        query_words = processed_query['expanded_words']
        
        # البحث في الاسم (وزن عالي)
        name = item.get('name', '').lower()
        for word in query_words:
            if word.lower() in name:
                score += 0.4
        
        # البحث في التخصص (وزن متوسط)
        specialty = item.get('specialty', '').lower()
        for word in query_words:
            if word.lower() in specialty:
                score += 0.3
        
        # البحث في الكلمات المفتاحية (وزن متوسط)
        keywords = [k.lower() for k in item.get('keywords', [])]
        for word in query_words:
            if word.lower() in keywords:
                score += 0.2
        
        # البحث في الوصف (وزن منخفض)
        description = item.get('description', '').lower()
        for word in query_words:
            if word.lower() in description:
                score += 0.1
        
        # تعديل النتيجة حسب التقييم
        rating = item.get('rating', 0)
        if rating > 0:
            score *= (1 + rating / 10)
        
        return min(score, 1.0)  # الحد الأقصى 1.0
    
    def _apply_filters(self, item: Dict, filters: Dict, search_type: str) -> bool:
        """تطبيق الفلاتر"""
        # فلتر الموقع
        if 'location' in filters:
            item_location = item.get('location', '').lower()
            filter_location = filters['location'].lower()
            if filter_location not in item_location:
                return False
        
        # فلتر التقييم
        if 'rating_min' in filters:
            item_rating = item.get('rating', 0)
            if item_rating < filters['rating_min']:
                return False
        
        # فلتر السعر
        if 'price_max' in filters and search_type == SearchType.DOCTORS.value:
            item_price = item.get('consultation_fee', 0)
            if item_price > filters['price_max']:
                return False
        
        # فلتر التأمين
        if 'insurance' in filters:
            item_insurance = item.get('insurance_accepted', [])
            if filters['insurance'] not in item_insurance:
                return False
        
        # فلتر الجنس
        if 'gender' in filters and search_type == SearchType.DOCTORS.value:
            item_gender = item.get('gender', '')
            if item_gender != filters['gender']:
                return False
        
        # فلتر سنوات الخبرة
        if 'experience_min' in filters and search_type == SearchType.DOCTORS.value:
            item_experience = item.get('experience_years', 0)
            if item_experience < filters['experience_min']:
                return False
        
        return True
    
    def _sort_results(self, results: List[SearchResult], sort_by: str, 
                     location: Optional[Dict]) -> List[SearchResult]:
        """ترتيب النتائج"""
        if sort_by == SortBy.RELEVANCE.value:
            return sorted(results, key=lambda x: x.relevance_score, reverse=True)
        elif sort_by == SortBy.RATING.value:
            return sorted(results, key=lambda x: x.metadata.get('rating', 0), reverse=True)
        elif sort_by == SortBy.PRICE.value:
            return sorted(results, key=lambda x: x.metadata.get('consultation_fee', 0))
        elif sort_by == SortBy.EXPERIENCE.value:
            return sorted(results, key=lambda x: x.metadata.get('experience_years', 0), reverse=True)
        else:
            return results
    
    def _group_results_by_type(self, results: List[SearchResult]) -> Dict:
        """تجميع النتائج حسب النوع"""
        grouped = defaultdict(list)
        for result in results:
            grouped[result.result_type].append(result.__dict__)
        return dict(grouped)
    
    def _generate_suggestions(self, query_text: str, results: List[SearchResult]) -> List[str]:
        """إنشاء اقتراحات ذكية"""
        suggestions = []
        
        # اقتراحات حسب النتائج
        if results:
            # اقتراح تخصصات مشابهة
            specialties = set()
            for result in results[:5]:
                specialty = result.metadata.get('specialty')
                if specialty:
                    specialties.add(specialty)
            
            for specialty in specialties:
                suggestions.append(f"أطباء {specialty}")
        
        # اقتراحات من المرادفات
        words = query_text.split()
        for word in words:
            if word in self.synonyms:
                for synonym in self.synonyms[word][:2]:
                    suggestions.append(query_text.replace(word, synonym))
        
        return suggestions[:5]
    
    def _generate_description(self, item: Dict, search_type: str) -> str:
        """إنشاء وصف للعنصر"""
        if search_type == SearchType.DOCTORS.value:
            specialty = item.get('specialty', '')
            hospital = item.get('hospital', '')
            rating = item.get('rating', 0)
            return f"{specialty} - {hospital} - تقييم {rating}/5"
        elif search_type == SearchType.HOSPITALS.value:
            location = item.get('location', '')
            specialties = ', '.join(item.get('specialties', [])[:3])
            return f"{location} - التخصصات: {specialties}"
        elif search_type == SearchType.PHARMACIES.value:
            location = item.get('location', '')
            services = ', '.join(item.get('services', [])[:2])
            return f"{location} - الخدمات: {services}"
        else:
            return item.get('description', 'لا يوجد وصف')
    
    def _save_search_history(self, search_query: SearchQuery, total_results: int):
        """حفظ البحث في التاريخ"""
        if search_query.user_id not in self.search_history:
            self.search_history[search_query.user_id] = []
        
        history_entry = {
            'query_id': search_query.query_id,
            'query': search_query.query_text,
            'timestamp': search_query.timestamp,
            'total_results': total_results,
            'search_types': search_query.search_types,
            'filters': search_query.filters
        }
        
        self.search_history[search_query.user_id].append(history_entry)
        
        # الحفاظ على الحد الأقصى
        if len(self.search_history[search_query.user_id]) > self.search_settings['search_history_limit']:
            self.search_history[search_query.user_id] = \
                self.search_history[search_query.user_id][-self.search_settings['search_history_limit']:]
    
    def _update_search_analytics(self, search_query: SearchQuery, total_results: int):
        """تحديث إحصائيات البحث"""
        # تحديث البحثات الشائعة
        query_lower = search_query.query_text.lower()
        
        # البحث عن البحث في القائمة الحالية
        found = False
        for trending in self.trending_searches:
            if trending['query'].lower() == query_lower:
                trending['count'] += 1
                trending['last_searched'] = search_query.timestamp
                found = True
                break
        
        if not found:
            self.trending_searches.append({
                'query': search_query.query_text,
                'count': 1,
                'last_searched': search_query.timestamp
            })
        
        # ترتيب البحثات الشائعة
        self.trending_searches.sort(key=lambda x: x['count'], reverse=True)
        
        # الحفاظ على الحد الأقصى
        if len(self.trending_searches) > self.search_settings['trending_searches_limit']:
            self.trending_searches = self.trending_searches[:self.search_settings['trending_searches_limit']]
    
    def _generate_cache_key(self, search_query: SearchQuery) -> str:
        """إنشاء مفتاح ذاكرة التخزين المؤقت"""
        key_data = {
            'query': search_query.query_text,
            'types': sorted(search_query.search_types),
            'filters': search_query.filters,
            'sort_by': search_query.sort_by
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def _get_cached_results(self, cache_key: str) -> Optional[Dict]:
        """الحصول على النتائج المخزنة مؤقتاً"""
        if cache_key in self.search_cache:
            cached_data = self.search_cache[cache_key]
            # فحص انتهاء الصلاحية
            if datetime.now() - cached_data['timestamp'] < timedelta(
                minutes=self.search_settings['cache_duration_minutes']
            ):
                return cached_data['results']
            else:
                # إزالة البيانات المنتهية الصلاحية
                del self.search_cache[cache_key]
        return None
    
    def _cache_results(self, cache_key: str, results: Dict):
        """حفظ النتائج في ذاكرة التخزين المؤقت"""
        self.search_cache[cache_key] = {
            'results': results,
            'timestamp': datetime.now()
        }
    
    def _calculate_search_time(self) -> int:
        """حساب وقت البحث (محاكاة)"""
        return 150  # ميلي ثانية
    
    # دوال الإكمال التلقائي والاقتراحات
    def _get_keyword_suggestions(self, query_text: str, search_types: List[str]) -> List[Dict]:
        """اقتراحات من الكلمات المفتاحية"""
        suggestions = []
        query_lower = query_text.lower()
        
        for keyword, items in self.keyword_index.items():
            if query_lower in keyword:
                relevance = difflib.SequenceMatcher(None, query_lower, keyword).ratio()
                if relevance >= self.search_settings['fuzzy_match_threshold']:
                    suggestions.append({
                        'text': keyword,
                        'type': 'keyword',
                        'relevance_score': relevance,
                        'count': len(items)
                    })
        
        return suggestions
    
    def _get_history_suggestions(self, query_text: str) -> List[Dict]:
        """اقتراحات من تاريخ البحث"""
        suggestions = []
        query_lower = query_text.lower()
        
        # جمع جميع البحثات من تاريخ جميع المستخدمين
        all_searches = []
        for user_history in self.search_history.values():
            all_searches.extend(user_history)
        
        for search in all_searches:
            search_query = search['query'].lower()
            if query_lower in search_query:
                relevance = difflib.SequenceMatcher(None, query_lower, search_query).ratio()
                suggestions.append({
                    'text': search['query'],
                    'type': 'history',
                    'relevance_score': relevance,
                    'last_used': search['timestamp'].isoformat()
                })
        
        return suggestions
    
    def _get_trending_suggestions(self, query_text: str) -> List[Dict]:
        """اقتراحات من البحثات الشائعة"""
        suggestions = []
        query_lower = query_text.lower()
        
        for trending in self.trending_searches:
            trending_query = trending['query'].lower()
            if query_lower in trending_query:
                relevance = difflib.SequenceMatcher(None, query_lower, trending_query).ratio()
                suggestions.append({
                    'text': trending['query'],
                    'type': 'trending',
                    'relevance_score': relevance,
                    'popularity': trending['count']
                })
        
        return suggestions
    
    def _get_synonym_suggestions(self, query_text: str) -> List[Dict]:
        """اقتراحات من المرادفات"""
        suggestions = []
        words = query_text.split()
        
        for word in words:
            if word in self.synonyms:
                for synonym in self.synonyms[word]:
                    suggested_text = query_text.replace(word, synonym)
                    suggestions.append({
                        'text': suggested_text,
                        'type': 'synonym',
                        'relevance_score': 0.8,
                        'original_word': word,
                        'synonym': synonym
                    })
        
        return suggestions
    
    def _deduplicate_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """إزالة التكرارات من الاقتراحات"""
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            text = suggestion['text'].lower()
            if text not in seen:
                seen.add(text)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    # دوال البحثات الشائعة
    def _get_general_trending_searches(self) -> List[Dict]:
        """البحثات الشائعة العامة"""
        return self.trending_searches[:10]
    
    def _get_personal_trending_searches(self, user_id: str) -> List[Dict]:
        """البحثات الشائعة الشخصية"""
        user_history = self.search_history.get(user_id, [])
        
        # تحليل البحثات الشخصية
        query_counts = defaultdict(int)
        for search in user_history:
            query_counts[search['query']] += 1
        
        # ترتيب حسب التكرار
        personal_trending = []
        for query, count in sorted(query_counts.items(), key=lambda x: x[1], reverse=True):
            personal_trending.append({
                'query': query,
                'count': count,
                'type': 'personal'
            })
        
        return personal_trending[:5]
    
    def _get_location_trending_searches(self, user_id: str) -> List[Dict]:
        """البحثات الشائعة حسب الموقع"""
        # محاكاة البحثات الشائعة حسب الموقع
        return [
            {'query': 'أطباء قلب القاهرة', 'count': 45, 'location': 'القاهرة'},
            {'query': 'مستشفيات الإسكندرية', 'count': 32, 'location': 'الإسكندرية'},
            {'query': 'صيدليات الجيزة', 'count': 28, 'location': 'الجيزة'}
        ]
    
    def _get_specialty_trending_searches(self, user_id: str) -> List[Dict]:
        """البحثات الشائعة حسب التخصص"""
        # محاكاة البحثات الشائعة حسب التخصص
        return [
            {'query': 'أطباء قلب', 'count': 67, 'specialty': 'قلب'},
            {'query': 'أطباء أطفال', 'count': 54, 'specialty': 'أطفال'},
            {'query': 'أطباء عظام', 'count': 43, 'specialty': 'عظام'}
        ]
    
    def _analyze_search_history(self, user_history: List[Dict]) -> Dict:
        """تحليل تاريخ البحث"""
        if not user_history:
            return {}
        
        # تحليل أنواع البحث
        search_types = defaultdict(int)
        for search in user_history:
            for search_type in search.get('search_types', []):
                search_types[search_type] += 1
        
        # تحليل الكلمات الأكثر بحثاً
        all_words = []
        for search in user_history:
            words = search['query'].split()
            all_words.extend(words)
        
        word_counts = defaultdict(int)
        for word in all_words:
            word_counts[word.lower()] += 1
        
        most_searched_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_searches': len(user_history),
            'most_searched_types': dict(search_types),
            'most_searched_words': dict(most_searched_words),
            'average_searches_per_day': len(user_history) / 30,  # تقدير
            'last_search': user_history[-1]['timestamp'].isoformat() if user_history else None
        }
    
    # دوال البحث المتقدم
    def _advanced_search_doctors(self, criteria: Dict) -> List[SearchResult]:
        """البحث المتقدم في الأطباء"""
        doctors = self.search_index[SearchType.DOCTORS.value]
        results = []
        
        for doctor in doctors:
            # تطبيق معايير البحث المتقدم
            if self._doctor_matches_criteria(doctor, criteria):
                result = SearchResult(
                    result_id=doctor['id'],
                    result_type=SearchType.DOCTORS.value,
                    title=doctor['name'],
                    description=f"{doctor['specialty']} - {doctor['hospital']}",
                    relevance_score=self._calculate_advanced_relevance(doctor, criteria),
                    metadata=doctor,
                    thumbnail=doctor.get('photo'),
                    url=f"/doctors/{doctor['id']}"
                )
                results.append(result)
        
        return results
    
    def _advanced_search_hospitals(self, criteria: Dict) -> List[SearchResult]:
        """البحث المتقدم في المستشفيات"""
        hospitals = self.search_index[SearchType.HOSPITALS.value]
        results = []
        
        for hospital in hospitals:
            if self._hospital_matches_criteria(hospital, criteria):
                result = SearchResult(
                    result_id=hospital['id'],
                    result_type=SearchType.HOSPITALS.value,
                    title=hospital['name'],
                    description=f"{hospital['type']} - {hospital['location']}",
                    relevance_score=self._calculate_advanced_relevance(hospital, criteria),
                    metadata=hospital,
                    thumbnail=hospital.get('image'),
                    url=f"/hospitals/{hospital['id']}"
                )
                results.append(result)
        
        return results
    
    def _advanced_search_pharmacies(self, criteria: Dict) -> List[SearchResult]:
        """البحث المتقدم في الصيدليات"""
        pharmacies = self.search_index[SearchType.PHARMACIES.value]
        results = []
        
        for pharmacy in pharmacies:
            if self._pharmacy_matches_criteria(pharmacy, criteria):
                result = SearchResult(
                    result_id=pharmacy['id'],
                    result_type=SearchType.PHARMACIES.value,
                    title=pharmacy['name'],
                    description=f"{pharmacy['location']} - {pharmacy['hours']}",
                    relevance_score=self._calculate_advanced_relevance(pharmacy, criteria),
                    metadata=pharmacy,
                    thumbnail=pharmacy.get('logo'),
                    url=f"/pharmacies/{pharmacy['id']}"
                )
                results.append(result)
        
        return results
    
    def _doctor_matches_criteria(self, doctor: Dict, criteria: Dict) -> bool:
        """فحص مطابقة الطبيب للمعايير"""
        # فحص التخصص
        if criteria.get('specialty') and criteria['specialty'] not in doctor.get('specialty', ''):
            return False
        
        # فحص الموقع
        if criteria.get('location') and criteria['location'] not in doctor.get('location', ''):
            return False
        
        # فحص التقييم
        if criteria.get('rating_min') and doctor.get('rating', 0) < criteria['rating_min']:
            return False
        
        # فحص السعر
        price_range = criteria.get('price_range', {})
        if price_range:
            doctor_fee = doctor.get('consultation_fee', 0)
            if price_range.get('min') and doctor_fee < price_range['min']:
                return False
            if price_range.get('max') and doctor_fee > price_range['max']:
                return False
        
        # فحص الجنس
        if criteria.get('gender') and doctor.get('gender') != criteria['gender']:
            return False
        
        # فحص سنوات الخبرة
        if criteria.get('experience_years') and doctor.get('experience_years', 0) < criteria['experience_years']:
            return False
        
        # فحص اللغة
        if criteria.get('language'):
            doctor_languages = doctor.get('languages', [])
            if criteria['language'] not in doctor_languages:
                return False
        
        # فحص التأمين
        if criteria.get('insurance_accepted'):
            doctor_insurance = doctor.get('insurance_accepted', [])
            if criteria['insurance_accepted'] not in doctor_insurance:
                return False
        
        return True
    
    def _hospital_matches_criteria(self, hospital: Dict, criteria: Dict) -> bool:
        """فحص مطابقة المستشفى للمعايير"""
        # تطبيق معايير مشابهة للمستشفيات
        return True  # مبسط للمثال
    
    def _pharmacy_matches_criteria(self, pharmacy: Dict, criteria: Dict) -> bool:
        """فحص مطابقة الصيدلية للمعايير"""
        # تطبيق معايير مشابهة للصيدليات
        return True  # مبسط للمثال
    
    def _calculate_advanced_relevance(self, item: Dict, criteria: Dict) -> float:
        """حساب درجة الصلة المتقدمة"""
        score = 0.5  # نقطة بداية
        
        # زيادة النقاط حسب التطابق مع المعايير
        if criteria.get('specialty') and criteria['specialty'] in item.get('specialty', ''):
            score += 0.3
        
        if criteria.get('location') and criteria['location'] in item.get('location', ''):
            score += 0.2
        
        # تعديل حسب التقييم
        rating = item.get('rating', 0)
        if rating > 0:
            score *= (1 + rating / 10)
        
        return min(score, 1.0)
    
    def _advanced_sort_results(self, results: List[SearchResult], criteria: Dict) -> List[SearchResult]:
        """ترتيب النتائج المتقدم"""
        sort_by = criteria.get('sort_by', SortBy.RELEVANCE.value)
        
        if sort_by == SortBy.RELEVANCE.value:
            return sorted(results, key=lambda x: x.relevance_score, reverse=True)
        elif sort_by == SortBy.RATING.value:
            return sorted(results, key=lambda x: x.metadata.get('rating', 0), reverse=True)
        elif sort_by == SortBy.PRICE.value:
            return sorted(results, key=lambda x: x.metadata.get('consultation_fee', 0))
        elif sort_by == SortBy.EXPERIENCE.value:
            return sorted(results, key=lambda x: x.metadata.get('experience_years', 0), reverse=True)
        else:
            return results
    
    # دوال اقتراحات البحث المتخصصة
    def _get_symptom_suggestions(self, query_text: str) -> List[Dict]:
        """اقتراحات الأعراض"""
        symptoms = [
            'صداع', 'حمى', 'سعال', 'ألم في الصدر', 'ضيق تنفس',
            'غثيان', 'قيء', 'إسهال', 'إمساك', 'دوخة', 'تعب',
            'ألم في البطن', 'ألم في الظهر', 'ألم في المفاصل'
        ]
        
        suggestions = []
        query_lower = query_text.lower()
        
        for symptom in symptoms:
            if query_lower in symptom.lower():
                suggestions.append({
                    'text': symptom,
                    'type': 'symptom',
                    'relevance_score': 0.9,
                    'category': 'أعراض'
                })
        
        return suggestions
    
    def _get_condition_suggestions(self, query_text: str) -> List[Dict]:
        """اقتراحات الحالات الطبية"""
        conditions = [
            'ضغط الدم المرتفع', 'السكري', 'أمراض القلب', 'الربو',
            'التهاب المفاصل', 'الصداع النصفي', 'القولون العصبي',
            'حساسية الطعام', 'الاكتئاب', 'القلق'
        ]
        
        suggestions = []
        query_lower = query_text.lower()
        
        for condition in conditions:
            if query_lower in condition.lower():
                suggestions.append({
                    'text': condition,
                    'type': 'condition',
                    'relevance_score': 0.9,
                    'category': 'حالات طبية'
                })
        
        return suggestions
    
    def _get_medication_suggestions(self, query_text: str) -> List[Dict]:
        """اقتراحات الأدوية"""
        medications = [
            'باراسيتامول', 'إيبوبروفين', 'أسبرين', 'أموكسيسيلين',
            'أوميبرازول', 'ميتفورمين', 'أتورفاستاتين', 'ليسينوبريل'
        ]
        
        suggestions = []
        query_lower = query_text.lower()
        
        for medication in medications:
            if query_lower in medication.lower():
                suggestions.append({
                    'text': medication,
                    'type': 'medication',
                    'relevance_score': 0.9,
                    'category': 'أدوية'
                })
        
        return suggestions
    
    def _get_doctor_suggestions(self, query_text: str) -> List[Dict]:
        """اقتراحات الأطباء"""
        specialties = [
            'قلب وأوعية دموية', 'أطفال', 'عظام ومفاصل', 'جلدية',
            'عيون', 'أنف وأذن وحنجرة', 'نساء وتوليد', 'مخ وأعصاب',
            'باطنة', 'جراحة عامة', 'نفسية', 'أسنان'
        ]
        
        suggestions = []
        query_lower = query_text.lower()
        
        for specialty in specialties:
            if query_lower in specialty.lower():
                suggestions.append({
                    'text': f'أطباء {specialty}',
                    'type': 'doctor_specialty',
                    'relevance_score': 0.9,
                    'category': 'تخصصات طبية'
                })
        
        return suggestions
    
    def _get_general_suggestions(self, query_text: str) -> List[Dict]:
        """اقتراحات عامة"""
        general_terms = [
            'مستشفى', 'صيدلية', 'عيادة', 'مختبر', 'أشعة',
            'تحليل', 'فحص', 'استشارة', 'موعد', 'طوارئ'
        ]
        
        suggestions = []
        query_lower = query_text.lower()
        
        for term in general_terms:
            if query_lower in term.lower():
                suggestions.append({
                    'text': term,
                    'type': 'general',
                    'relevance_score': 0.7,
                    'category': 'عام'
                })
        
        return suggestions
    
    def _get_personal_suggestions(self, user_id: str, query_text: str) -> List[Dict]:
        """اقتراحات شخصية حسب تاريخ المستخدم"""
        user_history = self.search_history.get(user_id, [])
        suggestions = []
        
        # تحليل البحثات السابقة للمستخدم
        for search in user_history[-10:]:  # آخر 10 بحثات
            if query_text.lower() in search['query'].lower():
                suggestions.append({
                    'text': search['query'],
                    'type': 'personal_history',
                    'relevance_score': 0.8,
                    'last_searched': search['timestamp'].isoformat()
                })
        
        return suggestions

