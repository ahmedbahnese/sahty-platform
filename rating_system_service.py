"""
نظام التقييم الشامل
نظام متكامل لتقييم الأطباء والخدمات والمرافق الطبية من قبل المرضى
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum
import statistics

class RatingType(Enum):
    DOCTOR = "طبيب"
    HOSPITAL = "مستشفى"
    CLINIC = "عيادة"
    PHARMACY = "صيدلية"
    LAB = "مختبر"
    SERVICE = "خدمة"
    TELEMEDICINE = "تطبيب عن بُعد"
    EMERGENCY = "طوارئ"

class RatingCategory(Enum):
    OVERALL = "التقييم العام"
    PROFESSIONALISM = "الاحترافية"
    COMMUNICATION = "التواصل"
    WAITING_TIME = "وقت الانتظار"
    CLEANLINESS = "النظافة"
    FACILITIES = "المرافق"
    STAFF_BEHAVIOR = "سلوك الطاقم"
    TREATMENT_QUALITY = "جودة العلاج"
    VALUE_FOR_MONEY = "القيمة مقابل المال"
    ACCESSIBILITY = "سهولة الوصول"

class ReviewStatus(Enum):
    PENDING = "في الانتظار"
    APPROVED = "معتمد"
    REJECTED = "مرفوض"
    FLAGGED = "مبلغ عنه"
    HIDDEN = "مخفي"

@dataclass
class Rating:
    rating_id: str
    user_id: str
    target_id: str  # معرف الطبيب/المستشفى/الخدمة
    target_type: str
    overall_rating: float  # من 1 إلى 5
    category_ratings: Dict[str, float]  # تقييمات فرعية
    review_text: str
    pros: List[str]  # النقاط الإيجابية
    cons: List[str]  # النقاط السلبية
    visit_date: datetime
    is_verified: bool  # تم التحقق من الزيارة
    is_anonymous: bool
    helpful_votes: int
    not_helpful_votes: int
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict  # معلومات إضافية

@dataclass
class RatingStatistics:
    target_id: str
    target_type: str
    total_ratings: int
    average_rating: float
    rating_distribution: Dict[int, int]  # توزيع النجوم
    category_averages: Dict[str, float]
    recent_trend: str  # تحسن، تراجع، مستقر
    verified_percentage: float
    response_rate: float  # معدل رد المقدم
    recommendation_percentage: float
    last_updated: datetime

@dataclass
class ReviewResponse:
    response_id: str
    rating_id: str
    responder_id: str  # معرف الطبيب/المؤسسة
    response_text: str
    is_official: bool
    created_at: datetime

@dataclass
class RatingFilter:
    rating_range: Tuple[float, float]
    date_range: Tuple[datetime, datetime]
    verified_only: bool
    categories: List[str]
    sort_by: str  # newest, oldest, highest, lowest, helpful
    limit: int

class RatingSystemService:
    def __init__(self):
        """تهيئة خدمة نظام التقييم"""
        
        # إعدادات النظام
        self.system_settings = {
            'min_rating': 1.0,
            'max_rating': 5.0,
            'min_review_length': 10,
            'max_review_length': 2000,
            'verification_required_days': 30,  # أيام للتحقق من الزيارة
            'auto_approve_threshold': 4.0,  # تقييمات أعلى من هذا تعتمد تلقائياً
            'flag_threshold': 5,  # عدد البلاغات للمراجعة
            'helpful_votes_weight': 0.1,
            'verified_rating_weight': 1.5,
            'recent_ratings_weight': 1.2  # وزن إضافي للتقييمات الحديثة
        }
        
        # معايير التقييم لكل نوع
        self.rating_criteria = {
            RatingType.DOCTOR.value: [
                RatingCategory.OVERALL.value,
                RatingCategory.PROFESSIONALISM.value,
                RatingCategory.COMMUNICATION.value,
                RatingCategory.TREATMENT_QUALITY.value,
                RatingCategory.WAITING_TIME.value
            ],
            RatingType.HOSPITAL.value: [
                RatingCategory.OVERALL.value,
                RatingCategory.FACILITIES.value,
                RatingCategory.CLEANLINESS.value,
                RatingCategory.STAFF_BEHAVIOR.value,
                RatingCategory.WAITING_TIME.value,
                RatingCategory.ACCESSIBILITY.value
            ],
            RatingType.CLINIC.value: [
                RatingCategory.OVERALL.value,
                RatingCategory.PROFESSIONALISM.value,
                RatingCategory.CLEANLINESS.value,
                RatingCategory.WAITING_TIME.value,
                RatingCategory.VALUE_FOR_MONEY.value
            ],
            RatingType.PHARMACY.value: [
                RatingCategory.OVERALL.value,
                RatingCategory.STAFF_BEHAVIOR.value,
                RatingCategory.WAITING_TIME.value,
                RatingCategory.VALUE_FOR_MONEY.value,
                RatingCategory.ACCESSIBILITY.value
            ],
            RatingType.TELEMEDICINE.value: [
                RatingCategory.OVERALL.value,
                RatingCategory.COMMUNICATION.value,
                RatingCategory.TREATMENT_QUALITY.value,
                RatingCategory.VALUE_FOR_MONEY.value
            ]
        }
        
        # قوالب الأسئلة للتقييم
        self.rating_questions = {
            RatingCategory.OVERALL.value: "كيف تقيم تجربتك الإجمالية؟",
            RatingCategory.PROFESSIONALISM.value: "ما مدى احترافية الطبيب؟",
            RatingCategory.COMMUNICATION.value: "كيف كان التواصل والشرح؟",
            RatingCategory.WAITING_TIME.value: "كيف تقيم وقت الانتظار؟",
            RatingCategory.CLEANLINESS.value: "ما مدى نظافة المكان؟",
            RatingCategory.FACILITIES.value: "كيف تقيم المرافق والتجهيزات؟",
            RatingCategory.STAFF_BEHAVIOR.value: "كيف كان تعامل الطاقم؟",
            RatingCategory.TREATMENT_QUALITY.value: "ما مدى جودة العلاج المقدم؟",
            RatingCategory.VALUE_FOR_MONEY.value: "هل التكلفة مناسبة للخدمة؟",
            RatingCategory.ACCESSIBILITY.value: "ما مدى سهولة الوصول والحركة؟"
        }
        
        # قوالب التعليقات الإيجابية والسلبية
        self.comment_templates = {
            'positive': [
                "طبيب ممتاز ومتفهم",
                "خدمة سريعة ومميزة",
                "طاقم متعاون ومهذب",
                "مكان نظيف ومرتب",
                "شرح واضح ومفصل",
                "وقت انتظار قصير",
                "أسعار معقولة",
                "سهولة في الحجز",
                "متابعة ممتازة",
                "نتائج مرضية"
            ],
            'negative': [
                "وقت انتظار طويل",
                "تعامل غير مهذب",
                "مكان غير نظيف",
                "أسعار مرتفعة",
                "شرح غير واضح",
                "صعوبة في الحجز",
                "عدم الالتزام بالمواعيد",
                "نقص في التجهيزات",
                "عدم المتابعة",
                "نتائج غير مرضية"
            ]
        }
        
        # قاعدة بيانات التقييمات (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.ratings = {}
        self.rating_statistics = {}
        self.review_responses = {}
        self.flagged_reviews = {}
        
        # إحصائيات النظام
        self.system_stats = {
            'total_ratings': 0,
            'verified_ratings': 0,
            'average_system_rating': 0.0,
            'most_rated_category': '',
            'response_rate': 0.0
        }
    
    def submit_rating(self, user_id: str, rating_data: Dict) -> Dict:
        """
        تقديم تقييم جديد
        
        Args:
            user_id: معرف المستخدم
            rating_data: بيانات التقييم
            
        Returns:
            Dict: نتيجة التقديم
        """
        try:
            # التحقق من صحة البيانات
            validation_result = self._validate_rating_data(rating_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # التحقق من عدم وجود تقييم مسبق
            existing_rating = self._check_existing_rating(user_id, rating_data['target_id'])
            if existing_rating:
                return {
                    'success': False,
                    'error': 'لقد قمت بتقييم هذا المقدم مسبقاً. يمكنك تعديل تقييمك الحالي.'
                }
            
            # إنشاء التقييم
            rating = Rating(
                rating_id=str(uuid.uuid4()),
                user_id=user_id,
                target_id=rating_data['target_id'],
                target_type=rating_data['target_type'],
                overall_rating=float(rating_data['overall_rating']),
                category_ratings=rating_data.get('category_ratings', {}),
                review_text=rating_data.get('review_text', ''),
                pros=rating_data.get('pros', []),
                cons=rating_data.get('cons', []),
                visit_date=datetime.fromisoformat(rating_data['visit_date']),
                is_verified=False,  # سيتم التحقق لاحقاً
                is_anonymous=rating_data.get('is_anonymous', False),
                helpful_votes=0,
                not_helpful_votes=0,
                status=ReviewStatus.PENDING.value,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata=rating_data.get('metadata', {})
            )
            
            # التحقق من الزيارة
            verification_result = self._verify_visit(user_id, rating_data['target_id'], rating.visit_date)
            rating.is_verified = verification_result['verified']
            
            # تحديد حالة التقييم
            if rating.overall_rating >= self.system_settings['auto_approve_threshold'] and rating.is_verified:
                rating.status = ReviewStatus.APPROVED.value
            
            # حفظ التقييم
            self.ratings[rating.rating_id] = rating
            
            # تحديث الإحصائيات
            self._update_rating_statistics(rating.target_id, rating.target_type)
            
            # إرسال إشعار للمقدم
            self._notify_provider_new_rating(rating)
            
            return {
                'success': True,
                'message': 'تم تقديم التقييم بنجاح',
                'rating_id': rating.rating_id,
                'status': rating.status,
                'is_verified': rating.is_verified,
                'points_earned': self._calculate_rating_points(rating)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تقديم التقييم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تقديم التقييم'
            }
    
    def get_ratings(self, target_id: str, filters: RatingFilter = None) -> Dict:
        """
        الحصول على تقييمات مقدم خدمة
        
        Args:
            target_id: معرف المقدم
            filters: فلاتر البحث
            
        Returns:
            Dict: التقييمات والإحصائيات
        """
        try:
            # الحصول على جميع التقييمات للمقدم
            target_ratings = [
                rating for rating in self.ratings.values()
                if rating.target_id == target_id and rating.status == ReviewStatus.APPROVED.value
            ]
            
            # تطبيق الفلاتر
            if filters:
                target_ratings = self._apply_filters(target_ratings, filters)
            
            # ترتيب التقييمات
            sort_by = filters.sort_by if filters else 'newest'
            target_ratings = self._sort_ratings(target_ratings, sort_by)
            
            # تحديد الحد الأقصى
            limit = filters.limit if filters and filters.limit else 20
            target_ratings = target_ratings[:limit]
            
            # تحويل إلى قاموس
            ratings_data = []
            for rating in target_ratings:
                rating_dict = self._rating_to_dict(rating)
                
                # إضافة الردود
                responses = self._get_rating_responses(rating.rating_id)
                rating_dict['responses'] = responses
                
                ratings_data.append(rating_dict)
            
            # الحصول على الإحصائيات
            statistics = self._get_rating_statistics(target_id)
            
            return {
                'success': True,
                'ratings': ratings_data,
                'statistics': statistics,
                'total_count': len([r for r in self.ratings.values() if r.target_id == target_id]),
                'filtered_count': len(target_ratings)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على التقييمات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على التقييمات'
            }
    
    def update_rating(self, user_id: str, rating_id: str, update_data: Dict) -> Dict:
        """
        تحديث تقييم موجود
        
        Args:
            user_id: معرف المستخدم
            rating_id: معرف التقييم
            update_data: بيانات التحديث
            
        Returns:
            Dict: نتيجة التحديث
        """
        try:
            if rating_id not in self.ratings:
                return {
                    'success': False,
                    'error': 'التقييم غير موجود'
                }
            
            rating = self.ratings[rating_id]
            
            # التحقق من الصلاحية
            if rating.user_id != user_id:
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية لتعديل هذا التقييم'
                }
            
            # التحقق من إمكانية التعديل (خلال 30 يوم)
            if (datetime.now() - rating.created_at).days > 30:
                return {
                    'success': False,
                    'error': 'لا يمكن تعديل التقييم بعد 30 يوم من تاريخ إنشائه'
                }
            
            # تحديث البيانات
            if 'overall_rating' in update_data:
                rating.overall_rating = float(update_data['overall_rating'])
            
            if 'category_ratings' in update_data:
                rating.category_ratings.update(update_data['category_ratings'])
            
            if 'review_text' in update_data:
                rating.review_text = update_data['review_text']
            
            if 'pros' in update_data:
                rating.pros = update_data['pros']
            
            if 'cons' in update_data:
                rating.cons = update_data['cons']
            
            rating.updated_at = datetime.now()
            rating.status = ReviewStatus.PENDING.value  # إعادة للمراجعة
            
            # تحديث الإحصائيات
            self._update_rating_statistics(rating.target_id, rating.target_type)
            
            return {
                'success': True,
                'message': 'تم تحديث التقييم بنجاح',
                'status': rating.status
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحديث التقييم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تحديث التقييم'
            }
    
    def respond_to_rating(self, responder_id: str, rating_id: str, response_text: str, is_official: bool = True) -> Dict:
        """
        الرد على تقييم
        
        Args:
            responder_id: معرف المجيب (طبيب/مؤسسة)
            rating_id: معرف التقييم
            response_text: نص الرد
            is_official: هل الرد رسمي
            
        Returns:
            Dict: نتيجة الرد
        """
        try:
            if rating_id not in self.ratings:
                return {
                    'success': False,
                    'error': 'التقييم غير موجود'
                }
            
            rating = self.ratings[rating_id]
            
            # التحقق من الصلاحية
            if not self._can_respond_to_rating(responder_id, rating.target_id):
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية للرد على هذا التقييم'
                }
            
            # إنشاء الرد
            response = ReviewResponse(
                response_id=str(uuid.uuid4()),
                rating_id=rating_id,
                responder_id=responder_id,
                response_text=response_text,
                is_official=is_official,
                created_at=datetime.now()
            )
            
            # حفظ الرد
            if rating_id not in self.review_responses:
                self.review_responses[rating_id] = []
            
            self.review_responses[rating_id].append(response)
            
            # إرسال إشعار للمقيم
            self._notify_user_response(rating.user_id, response)
            
            # تحديث معدل الرد
            self._update_response_rate(rating.target_id)
            
            return {
                'success': True,
                'message': 'تم إرسال الرد بنجاح',
                'response_id': response.response_id
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الرد على التقييم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الرد على التقييم'
            }
    
    def vote_helpful(self, user_id: str, rating_id: str, is_helpful: bool) -> Dict:
        """
        التصويت على مفيد/غير مفيد للتقييم
        
        Args:
            user_id: معرف المستخدم
            rating_id: معرف التقييم
            is_helpful: هل التقييم مفيد
            
        Returns:
            Dict: نتيجة التصويت
        """
        try:
            if rating_id not in self.ratings:
                return {
                    'success': False,
                    'error': 'التقييم غير موجود'
                }
            
            rating = self.ratings[rating_id]
            
            # التحقق من عدم التصويت المسبق
            vote_key = f"{user_id}_{rating_id}"
            if hasattr(self, 'user_votes') and vote_key in self.user_votes:
                return {
                    'success': False,
                    'error': 'لقد قمت بالتصويت على هذا التقييم مسبقاً'
                }
            
            # تسجيل التصويت
            if not hasattr(self, 'user_votes'):
                self.user_votes = {}
            
            self.user_votes[vote_key] = is_helpful
            
            # تحديث عدد الأصوات
            if is_helpful:
                rating.helpful_votes += 1
            else:
                rating.not_helpful_votes += 1
            
            return {
                'success': True,
                'message': 'تم تسجيل تصويتك بنجاح',
                'helpful_votes': rating.helpful_votes,
                'not_helpful_votes': rating.not_helpful_votes
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في التصويت: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في التصويت'
            }
    
    def flag_rating(self, user_id: str, rating_id: str, reason: str) -> Dict:
        """
        الإبلاغ عن تقييم
        
        Args:
            user_id: معرف المبلغ
            rating_id: معرف التقييم
            reason: سبب الإبلاغ
            
        Returns:
            Dict: نتيجة الإبلاغ
        """
        try:
            if rating_id not in self.ratings:
                return {
                    'success': False,
                    'error': 'التقييم غير موجود'
                }
            
            # إنشاء البلاغ
            flag_data = {
                'flag_id': str(uuid.uuid4()),
                'user_id': user_id,
                'rating_id': rating_id,
                'reason': reason,
                'created_at': datetime.now().isoformat()
            }
            
            # حفظ البلاغ
            if rating_id not in self.flagged_reviews:
                self.flagged_reviews[rating_id] = []
            
            self.flagged_reviews[rating_id].append(flag_data)
            
            # التحقق من عدد البلاغات
            if len(self.flagged_reviews[rating_id]) >= self.system_settings['flag_threshold']:
                rating = self.ratings[rating_id]
                rating.status = ReviewStatus.FLAGGED.value
                
                # إرسال تنبيه للمراجعة
                self._notify_admin_flagged_review(rating_id)
            
            return {
                'success': True,
                'message': 'تم تسجيل البلاغ بنجاح. سيتم مراجعته من قبل الفريق المختص.'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الإبلاغ عن التقييم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تسجيل البلاغ'
            }
    
    def get_rating_analytics(self, target_id: str, period_days: int = 30) -> Dict:
        """
        الحصول على تحليلات التقييمات
        
        Args:
            target_id: معرف المقدم
            period_days: فترة التحليل بالأيام
            
        Returns:
            Dict: تحليلات مفصلة
        """
        try:
            # تحديد فترة التحليل
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # الحصول على التقييمات في الفترة
            period_ratings = [
                rating for rating in self.ratings.values()
                if (rating.target_id == target_id and 
                    start_date <= rating.created_at <= end_date and
                    rating.status == ReviewStatus.APPROVED.value)
            ]
            
            if not period_ratings:
                return {
                    'success': True,
                    'analytics': {
                        'period_summary': {
                            'total_ratings': 0,
                            'average_rating': 0,
                            'trend': 'لا توجد بيانات كافية'
                        }
                    }
                }
            
            # حساب الإحصائيات
            analytics = {
                'period_summary': self._calculate_period_summary(period_ratings),
                'rating_trends': self._calculate_rating_trends(period_ratings),
                'category_analysis': self._analyze_categories(period_ratings),
                'sentiment_analysis': self._analyze_sentiment(period_ratings),
                'response_analytics': self._analyze_responses(target_id),
                'comparison_metrics': self._calculate_comparison_metrics(target_id, period_ratings),
                'improvement_suggestions': self._generate_improvement_suggestions(period_ratings)
            }
            
            return {
                'success': True,
                'analytics': analytics,
                'period': f'{period_days} يوم',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحليلات التقييمات: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنتاج التحليلات'
            }
    
    def get_top_rated_providers(self, provider_type: str, limit: int = 10) -> Dict:
        """
        الحصول على أفضل مقدمي الخدمة
        
        Args:
            provider_type: نوع المقدم
            limit: عدد النتائج
            
        Returns:
            Dict: قائمة أفضل المقدمين
        """
        try:
            # جمع إحصائيات جميع المقدمين من النوع المحدد
            provider_stats = {}
            
            for rating in self.ratings.values():
                if (rating.target_type == provider_type and 
                    rating.status == ReviewStatus.APPROVED.value):
                    
                    if rating.target_id not in provider_stats:
                        provider_stats[rating.target_id] = {
                            'ratings': [],
                            'verified_count': 0,
                            'total_helpful_votes': 0
                        }
                    
                    provider_stats[rating.target_id]['ratings'].append(rating.overall_rating)
                    
                    if rating.is_verified:
                        provider_stats[rating.target_id]['verified_count'] += 1
                    
                    provider_stats[rating.target_id]['total_helpful_votes'] += rating.helpful_votes
            
            # حساب النقاط لكل مقدم
            ranked_providers = []
            for provider_id, stats in provider_stats.items():
                if len(stats['ratings']) >= 3:  # الحد الأدنى 3 تقييمات
                    score = self._calculate_provider_score(stats)
                    
                    ranked_providers.append({
                        'provider_id': provider_id,
                        'average_rating': round(statistics.mean(stats['ratings']), 2),
                        'total_ratings': len(stats['ratings']),
                        'verified_percentage': round((stats['verified_count'] / len(stats['ratings'])) * 100, 1),
                        'helpful_votes': stats['total_helpful_votes'],
                        'score': score
                    })
            
            # ترتيب حسب النقاط
            ranked_providers.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'success': True,
                'top_providers': ranked_providers[:limit],
                'provider_type': provider_type,
                'total_evaluated': len(ranked_providers)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على أفضل المقدمين: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على أفضل المقدمين'
            }
    
    # الدوال المساعدة
    def _validate_rating_data(self, rating_data: Dict) -> Dict:
        """التحقق من صحة بيانات التقييم"""
        
        required_fields = ['target_id', 'target_type', 'overall_rating', 'visit_date']
        
        for field in required_fields:
            if field not in rating_data:
                return {
                    'valid': False,
                    'error': f'الحقل {field} مطلوب'
                }
        
        # التحقق من نطاق التقييم
        rating = float(rating_data['overall_rating'])
        if not (self.system_settings['min_rating'] <= rating <= self.system_settings['max_rating']):
            return {
                'valid': False,
                'error': f'التقييم يجب أن يكون بين {self.system_settings["min_rating"]} و {self.system_settings["max_rating"]}'
            }
        
        # التحقق من طول المراجعة
        review_text = rating_data.get('review_text', '')
        if len(review_text) > self.system_settings['max_review_length']:
            return {
                'valid': False,
                'error': f'المراجعة طويلة جداً (الحد الأقصى {self.system_settings["max_review_length"]} حرف)'
            }
        
        return {'valid': True}
    
    def _check_existing_rating(self, user_id: str, target_id: str) -> Optional[Rating]:
        """التحقق من وجود تقييم مسبق"""
        
        for rating in self.ratings.values():
            if rating.user_id == user_id and rating.target_id == target_id:
                return rating
        
        return None
    
    def _verify_visit(self, user_id: str, target_id: str, visit_date: datetime) -> Dict:
        """التحقق من صحة الزيارة"""
        
        # في التطبيق الحقيقي، سيتم التحقق من سجلات المواعيد
        # هنا نحاكي التحقق
        
        days_since_visit = (datetime.now() - visit_date).days
        
        if days_since_visit <= self.system_settings['verification_required_days']:
            # محاكاة التحقق من قاعدة البيانات
            verified = True  # افتراض وجود موعد
        else:
            verified = False
        
        return {
            'verified': verified,
            'verification_method': 'appointment_record' if verified else 'none'
        }
    
    def _update_rating_statistics(self, target_id: str, target_type: str):
        """تحديث إحصائيات التقييمات"""
        
        # الحصول على جميع التقييمات المعتمدة للمقدم
        target_ratings = [
            rating for rating in self.ratings.values()
            if (rating.target_id == target_id and 
                rating.status == ReviewStatus.APPROVED.value)
        ]
        
        if not target_ratings:
            return
        
        # حساب الإحصائيات
        total_ratings = len(target_ratings)
        average_rating = statistics.mean([r.overall_rating for r in target_ratings])
        
        # توزيع النجوم
        rating_distribution = {i: 0 for i in range(1, 6)}
        for rating in target_ratings:
            star_rating = int(round(rating.overall_rating))
            rating_distribution[star_rating] += 1
        
        # متوسط الفئات
        category_averages = {}
        for rating in target_ratings:
            for category, value in rating.category_ratings.items():
                if category not in category_averages:
                    category_averages[category] = []
                category_averages[category].append(value)
        
        for category in category_averages:
            category_averages[category] = statistics.mean(category_averages[category])
        
        # حساب الاتجاه
        recent_ratings = [r for r in target_ratings if (datetime.now() - r.created_at).days <= 30]
        older_ratings = [r for r in target_ratings if (datetime.now() - r.created_at).days > 30]
        
        if recent_ratings and older_ratings:
            recent_avg = statistics.mean([r.overall_rating for r in recent_ratings])
            older_avg = statistics.mean([r.overall_rating for r in older_ratings])
            
            if recent_avg > older_avg + 0.2:
                trend = 'تحسن'
            elif recent_avg < older_avg - 0.2:
                trend = 'تراجع'
            else:
                trend = 'مستقر'
        else:
            trend = 'غير محدد'
        
        # نسبة التحقق
        verified_count = len([r for r in target_ratings if r.is_verified])
        verified_percentage = (verified_count / total_ratings) * 100
        
        # معدل الرد
        ratings_with_responses = len([r for r in target_ratings if r.rating_id in self.review_responses])
        response_rate = (ratings_with_responses / total_ratings) * 100
        
        # نسبة التوصية (تقييمات 4 نجوم فأكثر)
        high_ratings = len([r for r in target_ratings if r.overall_rating >= 4.0])
        recommendation_percentage = (high_ratings / total_ratings) * 100
        
        # حفظ الإحصائيات
        self.rating_statistics[target_id] = RatingStatistics(
            target_id=target_id,
            target_type=target_type,
            total_ratings=total_ratings,
            average_rating=round(average_rating, 2),
            rating_distribution=rating_distribution,
            category_averages={k: round(v, 2) for k, v in category_averages.items()},
            recent_trend=trend,
            verified_percentage=round(verified_percentage, 1),
            response_rate=round(response_rate, 1),
            recommendation_percentage=round(recommendation_percentage, 1),
            last_updated=datetime.now()
        )
    
    def _apply_filters(self, ratings: List[Rating], filters: RatingFilter) -> List[Rating]:
        """تطبيق فلاتر البحث"""
        
        filtered_ratings = ratings
        
        # فلتر نطاق التقييم
        if filters.rating_range:
            min_rating, max_rating = filters.rating_range
            filtered_ratings = [
                r for r in filtered_ratings
                if min_rating <= r.overall_rating <= max_rating
            ]
        
        # فلتر نطاق التاريخ
        if filters.date_range:
            start_date, end_date = filters.date_range
            filtered_ratings = [
                r for r in filtered_ratings
                if start_date <= r.created_at <= end_date
            ]
        
        # فلتر التحقق
        if filters.verified_only:
            filtered_ratings = [
                r for r in filtered_ratings
                if r.is_verified
            ]
        
        # فلتر الفئات
        if filters.categories:
            filtered_ratings = [
                r for r in filtered_ratings
                if any(category in r.category_ratings for category in filters.categories)
            ]
        
        return filtered_ratings
    
    def _sort_ratings(self, ratings: List[Rating], sort_by: str) -> List[Rating]:
        """ترتيب التقييمات"""
        
        if sort_by == 'newest':
            return sorted(ratings, key=lambda x: x.created_at, reverse=True)
        elif sort_by == 'oldest':
            return sorted(ratings, key=lambda x: x.created_at)
        elif sort_by == 'highest':
            return sorted(ratings, key=lambda x: x.overall_rating, reverse=True)
        elif sort_by == 'lowest':
            return sorted(ratings, key=lambda x: x.overall_rating)
        elif sort_by == 'helpful':
            return sorted(ratings, key=lambda x: x.helpful_votes, reverse=True)
        else:
            return ratings
    
    def _rating_to_dict(self, rating: Rating) -> Dict:
        """تحويل التقييم إلى قاموس"""
        
        return {
            'rating_id': rating.rating_id,
            'user_id': rating.user_id if not rating.is_anonymous else None,
            'overall_rating': rating.overall_rating,
            'category_ratings': rating.category_ratings,
            'review_text': rating.review_text,
            'pros': rating.pros,
            'cons': rating.cons,
            'visit_date': rating.visit_date.isoformat(),
            'is_verified': rating.is_verified,
            'is_anonymous': rating.is_anonymous,
            'helpful_votes': rating.helpful_votes,
            'not_helpful_votes': rating.not_helpful_votes,
            'created_at': rating.created_at.isoformat(),
            'time_ago': self._calculate_time_ago(rating.created_at)
        }
    
    def _get_rating_responses(self, rating_id: str) -> List[Dict]:
        """الحصول على ردود التقييم"""
        
        if rating_id not in self.review_responses:
            return []
        
        responses = []
        for response in self.review_responses[rating_id]:
            responses.append({
                'response_id': response.response_id,
                'responder_id': response.responder_id,
                'response_text': response.response_text,
                'is_official': response.is_official,
                'created_at': response.created_at.isoformat(),
                'time_ago': self._calculate_time_ago(response.created_at)
            })
        
        return responses
    
    def _get_rating_statistics(self, target_id: str) -> Dict:
        """الحصول على إحصائيات التقييمات"""
        
        if target_id not in self.rating_statistics:
            return {}
        
        stats = self.rating_statistics[target_id]
        
        return {
            'total_ratings': stats.total_ratings,
            'average_rating': stats.average_rating,
            'rating_distribution': stats.rating_distribution,
            'category_averages': stats.category_averages,
            'recent_trend': stats.recent_trend,
            'verified_percentage': stats.verified_percentage,
            'response_rate': stats.response_rate,
            'recommendation_percentage': stats.recommendation_percentage,
            'last_updated': stats.last_updated.isoformat()
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
    
    # باقي الدوال المساعدة للتحليلات والإحصائيات...
    def _calculate_period_summary(self, ratings: List[Rating]) -> Dict:
        """حساب ملخص الفترة"""
        
        if not ratings:
            return {
                'total_ratings': 0,
                'average_rating': 0,
                'trend': 'لا توجد بيانات'
            }
        
        total_ratings = len(ratings)
        average_rating = statistics.mean([r.overall_rating for r in ratings])
        
        # حساب الاتجاه
        mid_point = len(ratings) // 2
        first_half = ratings[:mid_point]
        second_half = ratings[mid_point:]
        
        if first_half and second_half:
            first_avg = statistics.mean([r.overall_rating for r in first_half])
            second_avg = statistics.mean([r.overall_rating for r in second_half])
            
            if second_avg > first_avg + 0.2:
                trend = 'تحسن'
            elif second_avg < first_avg - 0.2:
                trend = 'تراجع'
            else:
                trend = 'مستقر'
        else:
            trend = 'غير محدد'
        
        return {
            'total_ratings': total_ratings,
            'average_rating': round(average_rating, 2),
            'trend': trend
        }
    
    def _calculate_rating_trends(self, ratings: List[Rating]) -> Dict:
        """حساب اتجاهات التقييمات"""
        
        # تجميع التقييمات حسب الأسبوع
        weekly_data = {}
        for rating in ratings:
            week_start = rating.created_at - timedelta(days=rating.created_at.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in weekly_data:
                weekly_data[week_key] = []
            
            weekly_data[week_key].append(rating.overall_rating)
        
        # حساب متوسط كل أسبوع
        weekly_averages = {}
        for week, ratings_list in weekly_data.items():
            weekly_averages[week] = round(statistics.mean(ratings_list), 2)
        
        return {
            'weekly_averages': weekly_averages,
            'trend_direction': self._determine_trend_direction(list(weekly_averages.values()))
        }
    
    def _analyze_categories(self, ratings: List[Rating]) -> Dict:
        """تحليل فئات التقييم"""
        
        category_data = {}
        
        for rating in ratings:
            for category, value in rating.category_ratings.items():
                if category not in category_data:
                    category_data[category] = []
                category_data[category].append(value)
        
        category_analysis = {}
        for category, values in category_data.items():
            if values:
                category_analysis[category] = {
                    'average': round(statistics.mean(values), 2),
                    'count': len(values),
                    'trend': self._determine_trend_direction(values[-10:])  # آخر 10 تقييمات
                }
        
        return category_analysis
    
    def _analyze_sentiment(self, ratings: List[Rating]) -> Dict:
        """تحليل المشاعر"""
        
        positive_keywords = ['ممتاز', 'رائع', 'جيد', 'مميز', 'سريع', 'نظيف', 'مهذب']
        negative_keywords = ['سيء', 'بطيء', 'غير نظيف', 'غير مهذب', 'مكلف', 'صعب']
        
        sentiment_scores = []
        
        for rating in ratings:
            review_text = rating.review_text.lower()
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in review_text)
            negative_count = sum(1 for keyword in negative_keywords if keyword in review_text)
            
            # حساب نقاط المشاعر
            sentiment_score = positive_count - negative_count
            sentiment_scores.append(sentiment_score)
        
        if sentiment_scores:
            avg_sentiment = statistics.mean(sentiment_scores)
            
            if avg_sentiment > 0.5:
                overall_sentiment = 'إيجابي'
            elif avg_sentiment < -0.5:
                overall_sentiment = 'سلبي'
            else:
                overall_sentiment = 'محايد'
        else:
            overall_sentiment = 'غير محدد'
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': round(avg_sentiment, 2) if sentiment_scores else 0,
            'positive_mentions': sum(1 for score in sentiment_scores if score > 0),
            'negative_mentions': sum(1 for score in sentiment_scores if score < 0)
        }
    
    def _analyze_responses(self, target_id: str) -> Dict:
        """تحليل الردود"""
        
        target_ratings = [r for r in self.ratings.values() if r.target_id == target_id]
        total_ratings = len(target_ratings)
        
        ratings_with_responses = 0
        avg_response_time = 0
        response_times = []
        
        for rating in target_ratings:
            if rating.rating_id in self.review_responses:
                ratings_with_responses += 1
                
                # حساب وقت الرد
                responses = self.review_responses[rating.rating_id]
                if responses:
                    first_response = min(responses, key=lambda x: x.created_at)
                    response_time = (first_response.created_at - rating.created_at).total_seconds() / 3600  # بالساعات
                    response_times.append(response_time)
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
        
        return {
            'response_rate': round((ratings_with_responses / total_ratings) * 100, 1) if total_ratings > 0 else 0,
            'average_response_time_hours': round(avg_response_time, 1),
            'total_responses': ratings_with_responses
        }
    
    def _calculate_comparison_metrics(self, target_id: str, period_ratings: List[Rating]) -> Dict:
        """حساب مقاييس المقارنة"""
        
        # مقارنة مع المتوسط العام للنظام
        all_ratings = [r for r in self.ratings.values() if r.status == ReviewStatus.APPROVED.value]
        
        if all_ratings:
            system_average = statistics.mean([r.overall_rating for r in all_ratings])
        else:
            system_average = 0
        
        if period_ratings:
            target_average = statistics.mean([r.overall_rating for r in period_ratings])
            
            if target_average > system_average + 0.2:
                performance = 'أعلى من المتوسط'
            elif target_average < system_average - 0.2:
                performance = 'أقل من المتوسط'
            else:
                performance = 'في المتوسط'
        else:
            target_average = 0
            performance = 'غير محدد'
        
        return {
            'target_average': round(target_average, 2),
            'system_average': round(system_average, 2),
            'performance_vs_average': performance,
            'difference': round(target_average - system_average, 2)
        }
    
    def _generate_improvement_suggestions(self, ratings: List[Rating]) -> List[str]:
        """إنتاج اقتراحات التحسين"""
        
        suggestions = []
        
        if not ratings:
            return ['لا توجد بيانات كافية لتقديم اقتراحات']
        
        # تحليل النقاط السلبية الشائعة
        all_cons = []
        for rating in ratings:
            all_cons.extend(rating.cons)
        
        # حساب تكرار المشاكل
        problem_counts = {}
        for con in all_cons:
            problem_counts[con] = problem_counts.get(con, 0) + 1
        
        # ترتيب المشاكل حسب التكرار
        sorted_problems = sorted(problem_counts.items(), key=lambda x: x[1], reverse=True)
        
        # إنتاج اقتراحات بناءً على المشاكل الأكثر تكراراً
        for problem, count in sorted_problems[:3]:
            if 'انتظار' in problem.lower():
                suggestions.append('تحسين إدارة المواعيد لتقليل أوقات الانتظار')
            elif 'نظافة' in problem.lower():
                suggestions.append('تعزيز معايير النظافة والتعقيم')
            elif 'تعامل' in problem.lower() or 'سلوك' in problem.lower():
                suggestions.append('تدريب الطاقم على خدمة العملاء والتعامل المهذب')
            elif 'سعر' in problem.lower() or 'تكلفة' in problem.lower():
                suggestions.append('مراجعة هيكل الأسعار وتوضيح قيمة الخدمات')
        
        # اقتراحات عامة بناءً على متوسط التقييم
        avg_rating = statistics.mean([r.overall_rating for r in ratings])
        
        if avg_rating < 3.0:
            suggestions.append('مراجعة شاملة لجودة الخدمات المقدمة')
        elif avg_rating < 4.0:
            suggestions.append('تحسين تجربة المريض والاهتمام بالتفاصيل')
        
        return suggestions[:5]  # أقصى 5 اقتراحات
    
    def _determine_trend_direction(self, values: List[float]) -> str:
        """تحديد اتجاه الاتجاه"""
        
        if len(values) < 2:
            return 'غير محدد'
        
        # حساب الاتجاه باستخدام الانحدار البسيط
        n = len(values)
        x_values = list(range(n))
        
        # حساب معامل الارتباط
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'مستقر'
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return 'تحسن'
        elif slope < -0.1:
            return 'تراجع'
        else:
            return 'مستقر'
    
    def _calculate_provider_score(self, stats: Dict) -> float:
        """حساب نقاط المقدم"""
        
        ratings = stats['ratings']
        verified_count = stats['verified_count']
        helpful_votes = stats['total_helpful_votes']
        
        # النقاط الأساسية من متوسط التقييم
        base_score = statistics.mean(ratings) * 20  # من 100
        
        # مكافأة للتقييمات المتحققة
        verified_bonus = (verified_count / len(ratings)) * 10
        
        # مكافأة للأصوات المفيدة
        helpful_bonus = min(helpful_votes * 0.1, 10)
        
        # مكافأة لعدد التقييمات (الثقة)
        volume_bonus = min(len(ratings) * 0.5, 10)
        
        total_score = base_score + verified_bonus + helpful_bonus + volume_bonus
        
        return round(min(total_score, 100), 2)
    
    # دوال الإشعارات
    def _notify_provider_new_rating(self, rating: Rating):
        """إرسال إشعار للمقدم بتقييم جديد"""
        # في التطبيق الحقيقي، سيتم إرسال إشعار فعلي
        pass
    
    def _notify_user_response(self, user_id: str, response: ReviewResponse):
        """إرسال إشعار للمستخدم برد جديد"""
        # في التطبيق الحقيقي، سيتم إرسال إشعار فعلي
        pass
    
    def _notify_admin_flagged_review(self, rating_id: str):
        """إرسال تنبيه للإدارة بمراجعة مبلغ عنها"""
        # في التطبيق الحقيقي، سيتم إرسال تنبيه للإدارة
        pass
    
    def _can_respond_to_rating(self, responder_id: str, target_id: str) -> bool:
        """التحقق من صلاحية الرد على التقييم"""
        # في التطبيق الحقيقي، سيتم التحقق من الصلاحيات
        return True
    
    def _update_response_rate(self, target_id: str):
        """تحديث معدل الرد"""
        # تحديث إحصائيات الرد في قاعدة البيانات
        pass
    
    def _calculate_rating_points(self, rating: Rating) -> int:
        """حساب النقاط المكتسبة من التقييم"""
        
        base_points = 5
        
        # نقاط إضافية للتقييمات المتحققة
        if rating.is_verified:
            base_points += 3
        
        # نقاط إضافية للمراجعات المفصلة
        if len(rating.review_text) > 100:
            base_points += 2
        
        # نقاط إضافية للنقاط الإيجابية والسلبية
        if rating.pros or rating.cons:
            base_points += 2
        
        return base_points

