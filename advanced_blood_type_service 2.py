"""
نظام فصائل الدم المتقدم والطوارئ
نظام شامل لإدارة فصائل الدم، التبرع، والطوارئ الطبية
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass, asdict
from enum import Enum
import math
import threading
import time

class BloodType(Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class RhFactor(Enum):
    POSITIVE = "موجب"
    NEGATIVE = "سالب"

class DonationStatus(Enum):
    ELIGIBLE = "مؤهل للتبرع"
    TEMPORARILY_INELIGIBLE = "غير مؤهل مؤقتاً"
    PERMANENTLY_INELIGIBLE = "غير مؤهل نهائياً"
    UNDER_REVIEW = "قيد المراجعة"

class BloodComponentType(Enum):
    WHOLE_BLOOD = "دم كامل"
    RED_BLOOD_CELLS = "كريات دم حمراء"
    PLATELETS = "صفائح دموية"
    PLASMA = "بلازما"
    WHITE_BLOOD_CELLS = "كريات دم بيضاء"
    CRYOPRECIPITATE = "راسب بارد"

class UrgencyLevel(Enum):
    CRITICAL = "حرج"
    URGENT = "عاجل"
    ROUTINE = "روتيني"
    ELECTIVE = "اختياري"

class BloodRequestStatus(Enum):
    PENDING = "في الانتظار"
    APPROVED = "موافق عليه"
    FULFILLED = "تم التوفير"
    CANCELLED = "ملغي"
    EXPIRED = "منتهي الصلاحية"

@dataclass
class BloodTypeProfile:
    profile_id: str
    patient_id: str
    blood_type: str
    rh_factor: str
    antibodies: List[str]
    antigens: List[str]
    compatibility_matrix: Dict[str, bool]
    last_tested: datetime
    test_location: str
    verified_by: str
    genetic_markers: Dict[str, str]
    rare_blood_indicators: List[str]
    medical_notes: str

@dataclass
class DonorProfile:
    donor_id: str
    patient_id: str
    blood_type: str
    donation_status: str
    last_donation_date: Optional[datetime]
    total_donations: int
    donation_history: List[Dict]
    health_screening: Dict
    eligibility_criteria: Dict
    next_eligible_date: Optional[datetime]
    preferred_donation_center: str
    emergency_contact: Dict
    special_notes: str
    rewards_points: int

@dataclass
class BloodRequest:
    request_id: str
    patient_id: str
    hospital_id: str
    blood_type_needed: str
    component_type: str
    units_needed: int
    urgency_level: str
    medical_reason: str
    doctor_id: str
    request_date: datetime
    needed_by_date: datetime
    status: str
    approval_notes: str
    fulfilled_units: int
    donor_matches: List[str]
    cost_estimate: float

@dataclass
class BloodInventory:
    inventory_id: str
    blood_bank_id: str
    blood_type: str
    component_type: str
    units_available: int
    expiry_date: datetime
    collection_date: datetime
    donor_id: str
    quality_status: str
    storage_location: str
    temperature_log: List[Dict]
    testing_results: Dict
    reserved_units: int

@dataclass
class EmergencyBloodAlert:
    alert_id: str
    blood_type: str
    component_type: str
    units_needed: int
    hospital_location: str
    urgency_level: str
    contact_info: Dict
    alert_radius_km: float
    created_at: datetime
    expires_at: datetime
    responded_donors: List[str]
    status: str

@dataclass
class BloodCompatibilityResult:
    compatibility_id: str
    donor_blood_type: str
    recipient_blood_type: str
    is_compatible: bool
    compatibility_percentage: float
    risk_factors: List[str]
    special_considerations: List[str]
    crossmatch_required: bool
    recommended_components: List[str]

class AdvancedBloodTypeService:
    def __init__(self):
        """تهيئة نظام فصائل الدم المتقدم"""
        
        # إعدادات النظام
        self.system_settings = {
            'donation_interval_days': 56,        # فترة بين التبرعات (8 أسابيع)
            'platelet_donation_interval_days': 7, # فترة بين تبرع الصفائح
            'plasma_donation_interval_days': 28,  # فترة بين تبرع البلازما
            'emergency_alert_radius_km': 50,     # نطاق تنبيه الطوارئ
            'blood_expiry_days': 42,             # صلاحية الدم الكامل
            'platelet_expiry_days': 5,           # صلاحية الصفائح
            'plasma_expiry_days': 365,           # صلاحية البلازما
            'minimum_donor_age': 18,             # أقل عمر للتبرع
            'maximum_donor_age': 65,             # أقصى عمر للتبرع
            'minimum_weight_kg': 50,             # أقل وزن للتبرع
            'minimum_hemoglobin_male': 13.5,     # أقل هيموجلوبين للذكور
            'minimum_hemoglobin_female': 12.5,   # أقل هيموجلوبين للإناث
            'reward_points_per_donation': 100    # نقاط المكافآت لكل تبرع
        }
        
        # قواعد البيانات
        self.blood_type_profiles = {}
        self.donor_profiles = {}
        self.blood_requests = {}
        self.blood_inventory = {}
        self.emergency_alerts = {}
        self.compatibility_cache = {}
        
        # مصفوفة التوافق
        self.compatibility_matrix = self._initialize_compatibility_matrix()
        
        # إحصائيات النظام
        self.blood_stats = {
            'total_donors': 0,
            'total_donations': 0,
            'total_requests_fulfilled': 0,
            'emergency_responses': 0,
            'lives_saved_estimate': 0,
            'blood_units_collected': 0,
            'blood_units_distributed': 0,
            'average_response_time_minutes': 0
        }
        
        # خدمات المراقبة
        self._start_monitoring_services()
    
    def register_blood_type(self, patient_id: str, blood_type_data: Dict) -> Dict:
        """
        تسجيل فصيلة دم مريض
        
        Args:
            patient_id: معرف المريض
            blood_type_data: بيانات فصيلة الدم
            
        Returns:
            Dict: نتيجة التسجيل
        """
        try:
            # التحقق من صحة فصيلة الدم
            validation_result = self._validate_blood_type_data(blood_type_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # إنشاء ملف فصيلة الدم
            profile = BloodTypeProfile(
                profile_id=str(uuid.uuid4()),
                patient_id=patient_id,
                blood_type=blood_type_data['blood_type'],
                rh_factor=blood_type_data.get('rh_factor', 'موجب'),
                antibodies=blood_type_data.get('antibodies', []),
                antigens=blood_type_data.get('antigens', []),
                compatibility_matrix=self._generate_compatibility_matrix(blood_type_data['blood_type']),
                last_tested=datetime.fromisoformat(blood_type_data['last_tested']),
                test_location=blood_type_data.get('test_location', ''),
                verified_by=blood_type_data.get('verified_by', ''),
                genetic_markers=blood_type_data.get('genetic_markers', {}),
                rare_blood_indicators=blood_type_data.get('rare_blood_indicators', []),
                medical_notes=blood_type_data.get('medical_notes', '')
            )
            
            # حفظ الملف
            self.blood_type_profiles[profile.profile_id] = profile
            
            # تحليل التوافق
            compatibility_analysis = self._analyze_blood_compatibility(profile)
            
            # فحص الفصائل النادرة
            rarity_analysis = self._analyze_blood_rarity(profile)
            
            return {
                'success': True,
                'profile_id': profile.profile_id,
                'blood_type': profile.blood_type,
                'rh_factor': profile.rh_factor,
                'compatibility_analysis': compatibility_analysis,
                'rarity_analysis': rarity_analysis,
                'donation_eligibility': self._check_donation_eligibility_basic(profile),
                'emergency_donor_potential': self._assess_emergency_donor_potential(profile)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تسجيل فصيلة الدم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تسجيل فصيلة الدم'
            }
    
    def register_donor(self, patient_id: str, donor_data: Dict) -> Dict:
        """
        تسجيل متبرع جديد
        
        Args:
            patient_id: معرف المريض
            donor_data: بيانات المتبرع
            
        Returns:
            Dict: نتيجة التسجيل
        """
        try:
            # التحقق من وجود ملف فصيلة الدم
            blood_profile = None
            for profile in self.blood_type_profiles.values():
                if profile.patient_id == patient_id:
                    blood_profile = profile
                    break
            
            if not blood_profile:
                return {
                    'success': False,
                    'error': 'يجب تسجيل فصيلة الدم أولاً'
                }
            
            # فحص الأهلية للتبرع
            eligibility_check = self._comprehensive_donation_eligibility_check(donor_data)
            if not eligibility_check['eligible']:
                return {
                    'success': False,
                    'error': f"غير مؤهل للتبرع: {eligibility_check['reason']}"
                }
            
            # إنشاء ملف المتبرع
            donor = DonorProfile(
                donor_id=str(uuid.uuid4()),
                patient_id=patient_id,
                blood_type=blood_profile.blood_type,
                donation_status=DonationStatus.ELIGIBLE.value,
                last_donation_date=None,
                total_donations=0,
                donation_history=[],
                health_screening=donor_data.get('health_screening', {}),
                eligibility_criteria=eligibility_check['criteria'],
                next_eligible_date=datetime.now(),
                preferred_donation_center=donor_data.get('preferred_center', ''),
                emergency_contact=donor_data.get('emergency_contact', {}),
                special_notes=donor_data.get('special_notes', ''),
                rewards_points=0
            )
            
            # حفظ ملف المتبرع
            self.donor_profiles[donor.donor_id] = donor
            
            # تحديث الإحصائيات
            self.blood_stats['total_donors'] += 1
            
            # إنشاء خطة التبرع المقترحة
            donation_plan = self._create_donation_plan(donor, blood_profile)
            
            return {
                'success': True,
                'donor_id': donor.donor_id,
                'donation_status': donor.donation_status,
                'blood_type': donor.blood_type,
                'eligibility_details': eligibility_check,
                'donation_plan': donation_plan,
                'potential_impact': self._calculate_donation_impact(donor, blood_profile),
                'next_steps': self._get_donor_next_steps(donor)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تسجيل المتبرع: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تسجيل المتبرع'
            }
    
    def create_blood_request(self, request_data: Dict) -> Dict:
        """
        إنشاء طلب دم
        
        Args:
            request_data: بيانات الطلب
            
        Returns:
            Dict: نتيجة الإنشاء
        """
        try:
            # التحقق من صحة البيانات
            validation_result = self._validate_blood_request(request_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # إنشاء الطلب
            request = BloodRequest(
                request_id=str(uuid.uuid4()),
                patient_id=request_data['patient_id'],
                hospital_id=request_data['hospital_id'],
                blood_type_needed=request_data['blood_type_needed'],
                component_type=request_data.get('component_type', BloodComponentType.WHOLE_BLOOD.value),
                units_needed=request_data['units_needed'],
                urgency_level=request_data.get('urgency_level', UrgencyLevel.ROUTINE.value),
                medical_reason=request_data['medical_reason'],
                doctor_id=request_data['doctor_id'],
                request_date=datetime.now(),
                needed_by_date=datetime.fromisoformat(request_data['needed_by_date']),
                status=BloodRequestStatus.PENDING.value,
                approval_notes='',
                fulfilled_units=0,
                donor_matches=[],
                cost_estimate=0.0
            )
            
            # حفظ الطلب
            self.blood_requests[request.request_id] = request
            
            # البحث عن المتبرعين المتوافقين
            compatible_donors = self._find_compatible_donors(request)
            request.donor_matches = [donor['donor_id'] for donor in compatible_donors]
            
            # فحص المخزون المتاح
            available_inventory = self._check_available_inventory(request)
            
            # حساب تقدير التكلفة
            request.cost_estimate = self._calculate_blood_cost(request)
            
            # تحديد الأولوية
            priority_score = self._calculate_request_priority(request)
            
            # إرسال تنبيهات إذا كان الطلب عاجل
            if request.urgency_level in [UrgencyLevel.CRITICAL.value, UrgencyLevel.URGENT.value]:
                self._send_urgent_blood_alerts(request, compatible_donors)
            
            return {
                'success': True,
                'request_id': request.request_id,
                'status': request.status,
                'compatible_donors_found': len(compatible_donors),
                'available_inventory_units': available_inventory['total_units'],
                'estimated_cost': request.cost_estimate,
                'priority_score': priority_score,
                'estimated_fulfillment_time': self._estimate_fulfillment_time(request),
                'next_steps': self._get_request_next_steps(request)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء طلب الدم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء طلب الدم'
            }
    
    def create_emergency_alert(self, alert_data: Dict) -> Dict:
        """
        إنشاء تنبيه طوارئ للدم
        
        Args:
            alert_data: بيانات التنبيه
            
        Returns:
            Dict: نتيجة الإنشاء
        """
        try:
            # إنشاء التنبيه
            alert = EmergencyBloodAlert(
                alert_id=str(uuid.uuid4()),
                blood_type=alert_data['blood_type'],
                component_type=alert_data.get('component_type', BloodComponentType.WHOLE_BLOOD.value),
                units_needed=alert_data['units_needed'],
                hospital_location=alert_data['hospital_location'],
                urgency_level=UrgencyLevel.CRITICAL.value,
                contact_info=alert_data['contact_info'],
                alert_radius_km=alert_data.get('radius_km', self.system_settings['emergency_alert_radius_km']),
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=alert_data.get('expires_in_hours', 24)),
                responded_donors=[],
                status='active'
            )
            
            # حفظ التنبيه
            self.emergency_alerts[alert.alert_id] = alert
            
            # البحث عن المتبرعين في النطاق
            nearby_donors = self._find_nearby_emergency_donors(alert)
            
            # إرسال التنبيهات
            notification_results = self._send_emergency_notifications(alert, nearby_donors)
            
            # تحديث الإحصائيات
            self.blood_stats['emergency_responses'] += 1
            
            return {
                'success': True,
                'alert_id': alert.alert_id,
                'donors_notified': len(nearby_donors),
                'notification_results': notification_results,
                'estimated_response_time': self._estimate_emergency_response_time(alert),
                'alternative_sources': self._find_alternative_blood_sources(alert),
                'alert_expires_at': alert.expires_at.isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء تنبيه الطوارئ: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء تنبيه الطوارئ'
            }
    
    def check_blood_compatibility(self, donor_blood_type: str, recipient_blood_type: str) -> Dict:
        """
        فحص توافق فصائل الدم
        
        Args:
            donor_blood_type: فصيلة دم المتبرع
            recipient_blood_type: فصيلة دم المستقبل
            
        Returns:
            Dict: نتيجة فحص التوافق
        """
        try:
            # فحص التوافق الأساسي
            basic_compatibility = self._check_basic_compatibility(donor_blood_type, recipient_blood_type)
            
            # فحص التوافق المتقدم
            advanced_compatibility = self._check_advanced_compatibility(donor_blood_type, recipient_blood_type)
            
            # حساب نسبة التوافق
            compatibility_percentage = self._calculate_compatibility_percentage(
                donor_blood_type, recipient_blood_type, advanced_compatibility
            )
            
            # تحديد عوامل الخطر
            risk_factors = self._identify_compatibility_risks(donor_blood_type, recipient_blood_type)
            
            # اقتراح مكونات الدم المناسبة
            recommended_components = self._recommend_blood_components(
                donor_blood_type, recipient_blood_type, compatibility_percentage
            )
            
            # إنشاء نتيجة التوافق
            result = BloodCompatibilityResult(
                compatibility_id=str(uuid.uuid4()),
                donor_blood_type=donor_blood_type,
                recipient_blood_type=recipient_blood_type,
                is_compatible=basic_compatibility['compatible'],
                compatibility_percentage=compatibility_percentage,
                risk_factors=risk_factors,
                special_considerations=advanced_compatibility.get('special_considerations', []),
                crossmatch_required=advanced_compatibility.get('crossmatch_required', False),
                recommended_components=recommended_components
            )
            
            # حفظ في التخزين المؤقت
            cache_key = f"{donor_blood_type}_{recipient_blood_type}"
            self.compatibility_cache[cache_key] = result
            
            return {
                'success': True,
                'compatibility_result': {
                    'is_compatible': result.is_compatible,
                    'compatibility_percentage': result.compatibility_percentage,
                    'risk_level': self._categorize_risk_level(result.compatibility_percentage),
                    'risk_factors': result.risk_factors,
                    'special_considerations': result.special_considerations,
                    'crossmatch_required': result.crossmatch_required,
                    'recommended_components': result.recommended_components,
                    'safety_recommendations': self._generate_safety_recommendations(result)
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في فحص توافق الدم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في فحص توافق الدم'
            }
    
    def get_blood_inventory_status(self, blood_bank_id: str = None) -> Dict:
        """
        الحصول على حالة مخزون الدم
        
        Args:
            blood_bank_id: معرف بنك الدم (اختياري)
            
        Returns:
            Dict: حالة المخزون
        """
        try:
            # فلترة المخزون
            if blood_bank_id:
                inventory_items = [
                    item for item in self.blood_inventory.values()
                    if item.blood_bank_id == blood_bank_id
                ]
            else:
                inventory_items = list(self.blood_inventory.values())
            
            # تجميع البيانات حسب فصيلة الدم
            blood_type_summary = {}
            for item in inventory_items:
                if item.blood_type not in blood_type_summary:
                    blood_type_summary[item.blood_type] = {
                        'total_units': 0,
                        'components': {},
                        'expiring_soon': 0,
                        'quality_issues': 0
                    }
                
                blood_type_summary[item.blood_type]['total_units'] += item.units_available
                
                # تجميع المكونات
                component = item.component_type
                if component not in blood_type_summary[item.blood_type]['components']:
                    blood_type_summary[item.blood_type]['components'][component] = 0
                blood_type_summary[item.blood_type]['components'][component] += item.units_available
                
                # فحص انتهاء الصلاحية
                days_to_expiry = (item.expiry_date - datetime.now()).days
                if days_to_expiry <= 7:
                    blood_type_summary[item.blood_type]['expiring_soon'] += item.units_available
                
                # فحص جودة الدم
                if item.quality_status != 'excellent':
                    blood_type_summary[item.blood_type]['quality_issues'] += item.units_available
            
            # تحليل النقص والفائض
            shortage_analysis = self._analyze_blood_shortage(blood_type_summary)
            
            # تحديد الأولويات
            collection_priorities = self._determine_collection_priorities(blood_type_summary)
            
            # إحصائيات عامة
            total_units = sum(item.units_available for item in inventory_items)
            total_expiring = sum(
                summary['expiring_soon'] for summary in blood_type_summary.values()
            )
            
            return {
                'success': True,
                'inventory_summary': {
                    'total_units_available': total_units,
                    'blood_types_available': len(blood_type_summary),
                    'units_expiring_soon': total_expiring,
                    'blood_banks_covered': len(set(item.blood_bank_id for item in inventory_items))
                },
                'blood_type_breakdown': blood_type_summary,
                'shortage_analysis': shortage_analysis,
                'collection_priorities': collection_priorities,
                'recommendations': self._generate_inventory_recommendations(
                    blood_type_summary, shortage_analysis
                )
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على حالة المخزون: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على حالة المخزون'
            }
    
    def get_donor_statistics(self, donor_id: str) -> Dict:
        """
        الحصول على إحصائيات المتبرع
        
        Args:
            donor_id: معرف المتبرع
            
        Returns:
            Dict: إحصائيات المتبرع
        """
        try:
            # البحث عن المتبرع
            if donor_id not in self.donor_profiles:
                return {
                    'success': False,
                    'error': 'المتبرع غير موجود'
                }
            
            donor = self.donor_profiles[donor_id]
            
            # حساب الإحصائيات
            donation_stats = self._calculate_donor_statistics(donor)
            
            # تحليل تأثير التبرعات
            impact_analysis = self._analyze_donation_impact(donor)
            
            # تحديد الإنجازات
            achievements = self._calculate_donor_achievements(donor)
            
            # اقتراح التبرع التالي
            next_donation_suggestion = self._suggest_next_donation(donor)
            
            return {
                'success': True,
                'donor_info': {
                    'donor_id': donor.donor_id,
                    'blood_type': donor.blood_type,
                    'donation_status': donor.donation_status,
                    'total_donations': donor.total_donations,
                    'rewards_points': donor.rewards_points
                },
                'donation_statistics': donation_stats,
                'impact_analysis': impact_analysis,
                'achievements': achievements,
                'next_donation_suggestion': next_donation_suggestion,
                'donor_ranking': self._calculate_donor_ranking(donor)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على إحصائيات المتبرع: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على إحصائيات المتبرع'
            }
    
    # الدوال المساعدة
    def _initialize_compatibility_matrix(self) -> Dict:
        """تهيئة مصفوفة التوافق"""
        
        # مصفوفة التوافق الأساسية
        matrix = {
            'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # متبرع عام
            'O+': ['O+', 'A+', 'B+', 'AB+'],
            'A-': ['A-', 'A+', 'AB-', 'AB+'],
            'A+': ['A+', 'AB+'],
            'B-': ['B-', 'B+', 'AB-', 'AB+'],
            'B+': ['B+', 'AB+'],
            'AB-': ['AB-', 'AB+'],
            'AB+': ['AB+']  # مستقبل عام
        }
        
        return matrix
    
    def _validate_blood_type_data(self, data: Dict) -> Dict:
        """التحقق من صحة بيانات فصيلة الدم"""
        
        required_fields = ['blood_type', 'last_tested']
        
        for field in required_fields:
            if field not in data:
                return {
                    'valid': False,
                    'error': f'الحقل {field} مطلوب'
                }
        
        # التحقق من صحة فصيلة الدم
        valid_blood_types = [bt.value for bt in BloodType]
        if data['blood_type'] not in valid_blood_types:
            return {
                'valid': False,
                'error': 'فصيلة دم غير صالحة'
            }
        
        return {'valid': True}
    
    def _generate_compatibility_matrix(self, blood_type: str) -> Dict[str, bool]:
        """إنتاج مصفوفة التوافق لفصيلة دم محددة"""
        
        compatible_types = self.compatibility_matrix.get(blood_type, [])
        
        matrix = {}
        for bt in BloodType:
            matrix[bt.value] = bt.value in compatible_types
        
        return matrix
    
    def _analyze_blood_compatibility(self, profile: BloodTypeProfile) -> Dict:
        """تحليل توافق فصيلة الدم"""
        
        compatible_donors = self.compatibility_matrix.get(profile.blood_type, [])
        can_donate_to = []
        
        # تحديد من يمكن أن يتبرع له
        for blood_type, recipients in self.compatibility_matrix.items():
            if profile.blood_type in recipients:
                can_donate_to.append(blood_type)
        
        return {
            'can_receive_from': compatible_donors,
            'can_donate_to': can_donate_to,
            'universal_donor': profile.blood_type == 'O-',
            'universal_recipient': profile.blood_type == 'AB+',
            'compatibility_score': len(can_donate_to) / len(BloodType) * 100
        }
    
    def _analyze_blood_rarity(self, profile: BloodTypeProfile) -> Dict:
        """تحليل ندرة فصيلة الدم"""
        
        # نسب انتشار فصائل الدم في مصر (تقديرية)
        blood_type_frequencies = {
            'O+': 35.0, 'A+': 30.0, 'B+': 20.0, 'AB+': 5.0,
            'O-': 4.0, 'A-': 3.0, 'B-': 2.0, 'AB-': 1.0
        }
        
        frequency = blood_type_frequencies.get(profile.blood_type, 1.0)
        
        if frequency <= 2.0:
            rarity_level = 'نادر جداً'
        elif frequency <= 5.0:
            rarity_level = 'نادر'
        elif frequency <= 15.0:
            rarity_level = 'غير شائع'
        else:
            rarity_level = 'شائع'
        
        return {
            'rarity_level': rarity_level,
            'frequency_percentage': frequency,
            'special_value': frequency <= 5.0,
            'emergency_priority': frequency <= 2.0
        }
    
    def _check_donation_eligibility_basic(self, profile: BloodTypeProfile) -> Dict:
        """فحص الأهلية الأساسية للتبرع"""
        
        # فحص أساسي بناءً على فصيلة الدم
        eligibility = {
            'eligible': True,
            'restrictions': [],
            'recommendations': []
        }
        
        # فحص الأجسام المضادة
        if profile.antibodies:
            eligibility['restrictions'].append('وجود أجسام مضادة - يتطلب فحص إضافي')
        
        # فحص المؤشرات النادرة
        if profile.rare_blood_indicators:
            eligibility['recommendations'].append('فصيلة دم نادرة - تبرع ذو قيمة عالية')
        
        return eligibility
    
    def _assess_emergency_donor_potential(self, profile: BloodTypeProfile) -> Dict:
        """تقييم إمكانية التبرع في الطوارئ"""
        
        compatibility_analysis = self._analyze_blood_compatibility(profile)
        rarity_analysis = self._analyze_blood_rarity(profile)
        
        # حساب نقاط الأولوية
        priority_score = 0
        
        if compatibility_analysis['universal_donor']:
            priority_score += 50
        
        if rarity_analysis['special_value']:
            priority_score += 30
        
        priority_score += len(compatibility_analysis['can_donate_to']) * 5
        
        return {
            'emergency_priority_score': priority_score,
            'universal_donor': compatibility_analysis['universal_donor'],
            'rare_blood': rarity_analysis['special_value'],
            'potential_recipients': len(compatibility_analysis['can_donate_to']),
            'emergency_value': 'عالي' if priority_score >= 70 else 'متوسط' if priority_score >= 40 else 'منخفض'
        }
    
    def _comprehensive_donation_eligibility_check(self, donor_data: Dict) -> Dict:
        """فحص شامل لأهلية التبرع"""
        
        eligibility = {
            'eligible': True,
            'reason': '',
            'criteria': {}
        }
        
        # فحص العمر
        age = donor_data.get('age', 0)
        if age < self.system_settings['minimum_donor_age']:
            eligibility['eligible'] = False
            eligibility['reason'] = f"العمر أقل من {self.system_settings['minimum_donor_age']} سنة"
            return eligibility
        
        if age > self.system_settings['maximum_donor_age']:
            eligibility['eligible'] = False
            eligibility['reason'] = f"العمر أكبر من {self.system_settings['maximum_donor_age']} سنة"
            return eligibility
        
        # فحص الوزن
        weight = donor_data.get('weight_kg', 0)
        if weight < self.system_settings['minimum_weight_kg']:
            eligibility['eligible'] = False
            eligibility['reason'] = f"الوزن أقل من {self.system_settings['minimum_weight_kg']} كيلو"
            return eligibility
        
        # فحص الهيموجلوبين
        hemoglobin = donor_data.get('hemoglobin', 0)
        gender = donor_data.get('gender', 'male')
        min_hemoglobin = (self.system_settings['minimum_hemoglobin_male'] 
                         if gender == 'male' 
                         else self.system_settings['minimum_hemoglobin_female'])
        
        if hemoglobin < min_hemoglobin:
            eligibility['eligible'] = False
            eligibility['reason'] = f"مستوى الهيموجلوبين منخفض ({hemoglobin} < {min_hemoglobin})"
            return eligibility
        
        # فحص الحالة الصحية
        health_conditions = donor_data.get('health_conditions', [])
        disqualifying_conditions = [
            'hepatitis', 'hiv', 'heart_disease', 'diabetes_insulin',
            'cancer_active', 'blood_disorders'
        ]
        
        for condition in health_conditions:
            if condition in disqualifying_conditions:
                eligibility['eligible'] = False
                eligibility['reason'] = f"حالة صحية مانعة: {condition}"
                return eligibility
        
        # حفظ المعايير المستوفاة
        eligibility['criteria'] = {
            'age_check': True,
            'weight_check': True,
            'hemoglobin_check': True,
            'health_check': True,
            'age': age,
            'weight_kg': weight,
            'hemoglobin': hemoglobin
        }
        
        return eligibility
    
    def _create_donation_plan(self, donor: DonorProfile, blood_profile: BloodTypeProfile) -> Dict:
        """إنشاء خطة تبرع مقترحة"""
        
        rarity_analysis = self._analyze_blood_rarity(blood_profile)
        compatibility_analysis = self._analyze_blood_compatibility(blood_profile)
        
        plan = {
            'recommended_frequency': 'كل 8 أسابيع',
            'preferred_components': [],
            'annual_goal': 6,  # 6 تبرعات سنوياً
            'special_programs': []
        }
        
        # تحديد المكونات المفضلة
        if compatibility_analysis['universal_donor']:
            plan['preferred_components'].append('دم كامل')
            plan['preferred_components'].append('كريات دم حمراء')
        
        if rarity_analysis['special_value']:
            plan['special_programs'].append('برنامج الفصائل النادرة')
        
        if blood_profile.blood_type in ['AB+', 'AB-']:
            plan['preferred_components'].append('بلازما')
            plan['recommended_frequency'] = 'كل 4 أسابيع (بلازما)'
        
        return plan
    
    def _calculate_donation_impact(self, donor: DonorProfile, blood_profile: BloodTypeProfile) -> Dict:
        """حساب تأثير التبرع المحتمل"""
        
        compatibility_analysis = self._analyze_blood_compatibility(blood_profile)
        rarity_analysis = self._analyze_blood_rarity(blood_profile)
        
        # تقدير عدد الأرواح التي يمكن إنقاذها
        lives_per_donation = 3  # متوسط عام
        
        if compatibility_analysis['universal_donor']:
            lives_per_donation = 4
        elif rarity_analysis['special_value']:
            lives_per_donation = 5
        
        annual_donations = 6  # هدف سنوي
        annual_lives_impact = annual_donations * lives_per_donation
        
        return {
            'lives_per_donation': lives_per_donation,
            'annual_donations_goal': annual_donations,
            'annual_lives_impact': annual_lives_impact,
            'lifetime_impact_estimate': annual_lives_impact * 20,  # 20 سنة تبرع
            'community_value': 'عالي' if rarity_analysis['special_value'] else 'متوسط'
        }
    
    def _get_donor_next_steps(self, donor: DonorProfile) -> List[str]:
        """الحصول على الخطوات التالية للمتبرع"""
        
        steps = [
            'حجز موعد للتبرع الأول',
            'إجراء فحص طبي شامل',
            'تحديد مركز التبرع المفضل'
        ]
        
        if donor.blood_type in ['O-', 'AB-', 'B-', 'A-']:
            steps.append('التسجيل في برنامج المتبرعين النادرين')
        
        steps.extend([
            'تحميل تطبيق تذكيرات التبرع',
            'الانضمام لمجتمع المتبرعين'
        ])
        
        return steps
    
    def _validate_blood_request(self, request_data: Dict) -> Dict:
        """التحقق من صحة طلب الدم"""
        
        required_fields = [
            'patient_id', 'hospital_id', 'blood_type_needed',
            'units_needed', 'medical_reason', 'doctor_id', 'needed_by_date'
        ]
        
        for field in required_fields:
            if field not in request_data:
                return {
                    'valid': False,
                    'error': f'الحقل {field} مطلوب'
                }
        
        # التحقق من صحة فصيلة الدم
        valid_blood_types = [bt.value for bt in BloodType]
        if request_data['blood_type_needed'] not in valid_blood_types:
            return {
                'valid': False,
                'error': 'فصيلة دم غير صالحة'
            }
        
        # التحقق من عدد الوحدات
        if request_data['units_needed'] <= 0 or request_data['units_needed'] > 10:
            return {
                'valid': False,
                'error': 'عدد الوحدات يجب أن يكون بين 1 و 10'
            }
        
        return {'valid': True}
    
    def _find_compatible_donors(self, request: BloodRequest) -> List[Dict]:
        """البحث عن المتبرعين المتوافقين"""
        
        compatible_donors = []
        
        # الحصول على فصائل الدم المتوافقة
        compatible_blood_types = []
        for blood_type, recipients in self.compatibility_matrix.items():
            if request.blood_type_needed in recipients:
                compatible_blood_types.append(blood_type)
        
        # البحث في المتبرعين
        for donor in self.donor_profiles.values():
            if (donor.blood_type in compatible_blood_types and 
                donor.donation_status == DonationStatus.ELIGIBLE.value):
                
                # فحص إمكانية التبرع (آخر تبرع)
                if donor.last_donation_date:
                    days_since_last = (datetime.now() - donor.last_donation_date).days
                    if days_since_last < self.system_settings['donation_interval_days']:
                        continue
                
                compatible_donors.append({
                    'donor_id': donor.donor_id,
                    'blood_type': donor.blood_type,
                    'total_donations': donor.total_donations,
                    'last_donation_date': donor.last_donation_date.isoformat() if donor.last_donation_date else None,
                    'compatibility_score': self._calculate_donor_compatibility_score(donor, request)
                })
        
        # ترتيب حسب نقاط التوافق
        compatible_donors.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return compatible_donors[:20]  # أفضل 20 متبرع
    
    def _check_available_inventory(self, request: BloodRequest) -> Dict:
        """فحص المخزون المتاح"""
        
        available_units = 0
        matching_inventory = []
        
        for item in self.blood_inventory.values():
            if (item.blood_type == request.blood_type_needed and
                item.component_type == request.component_type and
                item.units_available > 0 and
                item.expiry_date > datetime.now() and
                item.quality_status == 'excellent'):
                
                available_units += item.units_available
                matching_inventory.append({
                    'inventory_id': item.inventory_id,
                    'blood_bank_id': item.blood_bank_id,
                    'units_available': item.units_available,
                    'expiry_date': item.expiry_date.isoformat(),
                    'collection_date': item.collection_date.isoformat()
                })
        
        return {
            'total_units': available_units,
            'can_fulfill_request': available_units >= request.units_needed,
            'matching_inventory': matching_inventory,
            'shortage': max(0, request.units_needed - available_units)
        }
    
    def _calculate_blood_cost(self, request: BloodRequest) -> float:
        """حساب تقدير تكلفة الدم"""
        
        # أسعار تقديرية بالجنيه المصري
        component_prices = {
            BloodComponentType.WHOLE_BLOOD.value: 200.0,
            BloodComponentType.RED_BLOOD_CELLS.value: 250.0,
            BloodComponentType.PLATELETS.value: 800.0,
            BloodComponentType.PLASMA.value: 150.0,
            BloodComponentType.WHITE_BLOOD_CELLS.value: 1000.0,
            BloodComponentType.CRYOPRECIPITATE.value: 300.0
        }
        
        base_cost = component_prices.get(request.component_type, 200.0)
        total_cost = base_cost * request.units_needed
        
        # إضافة رسوم الطوارئ
        if request.urgency_level == UrgencyLevel.CRITICAL.value:
            total_cost *= 1.5
        elif request.urgency_level == UrgencyLevel.URGENT.value:
            total_cost *= 1.2
        
        return round(total_cost, 2)
    
    def _calculate_request_priority(self, request: BloodRequest) -> int:
        """حساب أولوية الطلب"""
        
        priority_score = 0
        
        # نقاط الإلحاح
        urgency_scores = {
            UrgencyLevel.CRITICAL.value: 100,
            UrgencyLevel.URGENT.value: 75,
            UrgencyLevel.ROUTINE.value: 50,
            UrgencyLevel.ELECTIVE.value: 25
        }
        priority_score += urgency_scores.get(request.urgency_level, 50)
        
        # نقاط ندرة فصيلة الدم
        blood_type_frequencies = {
            'AB-': 50, 'B-': 40, 'A-': 30, 'O-': 20,
            'AB+': 15, 'B+': 10, 'A+': 5, 'O+': 0
        }
        priority_score += blood_type_frequencies.get(request.blood_type_needed, 0)
        
        # نقاط الوقت المتبقي
        time_remaining = (request.needed_by_date - datetime.now()).total_seconds() / 3600
        if time_remaining <= 6:  # أقل من 6 ساعات
            priority_score += 30
        elif time_remaining <= 24:  # أقل من 24 ساعة
            priority_score += 20
        elif time_remaining <= 72:  # أقل من 3 أيام
            priority_score += 10
        
        return min(priority_score, 200)  # حد أقصى 200
    
    def _send_urgent_blood_alerts(self, request: BloodRequest, compatible_donors: List[Dict]):
        """إرسال تنبيهات الدم العاجلة"""
        
        # محاكاة إرسال التنبيهات
        # في التطبيق الحقيقي، سيتم إرسال SMS، push notifications، إلخ
        
        alert_message = f"""
        تنبيه دم عاجل!
        
        فصيلة الدم المطلوبة: {request.blood_type_needed}
        عدد الوحدات: {request.units_needed}
        مستوى الإلحاح: {request.urgency_level}
        المطلوب قبل: {request.needed_by_date.strftime('%Y-%m-%d %H:%M')}
        
        للاستجابة، اتصل بـ: 123-456-7890
        """
        
        for donor in compatible_donors[:10]:  # أفضل 10 متبرعين
            current_app.logger.info(f"تنبيه مرسل للمتبرع {donor['donor_id']}: {alert_message}")
    
    def _estimate_fulfillment_time(self, request: BloodRequest) -> str:
        """تقدير وقت تلبية الطلب"""
        
        if request.urgency_level == UrgencyLevel.CRITICAL.value:
            return "2-6 ساعات"
        elif request.urgency_level == UrgencyLevel.URGENT.value:
            return "6-24 ساعة"
        elif request.urgency_level == UrgencyLevel.ROUTINE.value:
            return "1-3 أيام"
        else:
            return "3-7 أيام"
    
    def _get_request_next_steps(self, request: BloodRequest) -> List[str]:
        """الحصول على الخطوات التالية للطلب"""
        
        steps = [
            'مراجعة الطلب من قبل فريق بنك الدم',
            'البحث عن المتبرعين المتوافقين',
            'فحص المخزون المتاح'
        ]
        
        if request.urgency_level in [UrgencyLevel.CRITICAL.value, UrgencyLevel.URGENT.value]:
            steps.insert(0, 'تفعيل بروتوكول الطوارئ')
            steps.append('إرسال تنبيهات عاجلة للمتبرعين')
        
        steps.extend([
            'تحديد موعد التبرع أو التوزيع',
            'إجراء فحوصات التوافق النهائية',
            'تسليم الدم للمستشفى'
        ])
        
        return steps
    
    def _find_nearby_emergency_donors(self, alert: EmergencyBloodAlert) -> List[Dict]:
        """البحث عن المتبرعين القريبين للطوارئ"""
        
        # محاكاة البحث الجغرافي
        # في التطبيق الحقيقي، سيتم استخدام GPS والخرائط
        
        nearby_donors = []
        
        # البحث عن المتبرعين المتوافقين
        compatible_blood_types = []
        for blood_type, recipients in self.compatibility_matrix.items():
            if alert.blood_type in recipients:
                compatible_blood_types.append(blood_type)
        
        for donor in self.donor_profiles.values():
            if (donor.blood_type in compatible_blood_types and 
                donor.donation_status == DonationStatus.ELIGIBLE.value):
                
                # محاكاة المسافة (عشوائية)
                import random
                distance_km = random.uniform(1, alert.alert_radius_km)
                
                if distance_km <= alert.alert_radius_km:
                    nearby_donors.append({
                        'donor_id': donor.donor_id,
                        'blood_type': donor.blood_type,
                        'distance_km': round(distance_km, 1),
                        'estimated_arrival_minutes': int(distance_km * 2),  # تقدير 2 دقيقة/كم
                        'total_donations': donor.total_donations,
                        'emergency_response_history': random.randint(0, 5)
                    })
        
        # ترتيب حسب المسافة وتاريخ الاستجابة
        nearby_donors.sort(key=lambda x: (x['distance_km'], -x['emergency_response_history']))
        
        return nearby_donors[:15]  # أقرب 15 متبرع
    
    def _send_emergency_notifications(self, alert: EmergencyBloodAlert, donors: List[Dict]) -> Dict:
        """إرسال إشعارات الطوارئ"""
        
        # محاكاة إرسال الإشعارات
        notification_results = {
            'sms_sent': 0,
            'push_notifications_sent': 0,
            'calls_made': 0,
            'estimated_responses': 0
        }
        
        emergency_message = f"""
        🚨 طوارئ دم عاجلة! 🚨
        
        فصيلة الدم: {alert.blood_type}
        الوحدات المطلوبة: {alert.units_needed}
        الموقع: {alert.hospital_location}
        
        أنت على بُعد {'{distance_km}'} كم
        وقت الوصول المقدر: {'{estimated_arrival_minutes}'} دقيقة
        
        للاستجابة فوراً: {alert.contact_info.get('phone', '123-456-7890')}
        """
        
        for donor in donors:
            # محاكاة إرسال SMS
            notification_results['sms_sent'] += 1
            
            # محاكاة إرسال push notification
            notification_results['push_notifications_sent'] += 1
            
            # للحالات الحرجة، محاكاة اتصال هاتفي
            if alert.urgency_level == UrgencyLevel.CRITICAL.value and donor['distance_km'] <= 10:
                notification_results['calls_made'] += 1
        
        # تقدير معدل الاستجابة (30% للطوارئ)
        notification_results['estimated_responses'] = int(len(donors) * 0.3)
        
        return notification_results
    
    def _estimate_emergency_response_time(self, alert: EmergencyBloodAlert) -> str:
        """تقدير وقت الاستجابة للطوارئ"""
        
        if alert.urgency_level == UrgencyLevel.CRITICAL.value:
            return "30-90 دقيقة"
        else:
            return "1-3 ساعات"
    
    def _find_alternative_blood_sources(self, alert: EmergencyBloodAlert) -> List[Dict]:
        """البحث عن مصادر بديلة للدم"""
        
        # محاكاة مصادر بديلة
        alternative_sources = [
            {
                'source_type': 'بنك دم مركزي',
                'name': 'بنك الدم المركزي - القاهرة',
                'distance_km': 25,
                'estimated_units_available': 15,
                'contact': '02-12345678',
                'transport_time_minutes': 45
            },
            {
                'source_type': 'مستشفى شريك',
                'name': 'مستشفى 57357',
                'distance_km': 18,
                'estimated_units_available': 8,
                'contact': '02-87654321',
                'transport_time_minutes': 35
            },
            {
                'source_type': 'بنك دم خاص',
                'name': 'بنك دم فاب لاب',
                'distance_km': 12,
                'estimated_units_available': 5,
                'contact': '02-11223344',
                'transport_time_minutes': 25
            }
        ]
        
        return alternative_sources
    
    def _check_basic_compatibility(self, donor_type: str, recipient_type: str) -> Dict:
        """فحص التوافق الأساسي"""
        
        compatible_recipients = self.compatibility_matrix.get(donor_type, [])
        
        return {
            'compatible': recipient_type in compatible_recipients,
            'compatibility_type': 'أساسي',
            'confidence_level': 'عالي' if recipient_type in compatible_recipients else 'منخفض'
        }
    
    def _check_advanced_compatibility(self, donor_type: str, recipient_type: str) -> Dict:
        """فحص التوافق المتقدم"""
        
        # فحص متقدم يأخذ في الاعتبار عوامل إضافية
        advanced_result = {
            'special_considerations': [],
            'crossmatch_required': False,
            'additional_tests_needed': []
        }
        
        # فحص الفصائل النادرة
        rare_types = ['AB-', 'B-', 'A-', 'O-']
        if donor_type in rare_types or recipient_type in rare_types:
            advanced_result['special_considerations'].append('فصيلة دم نادرة')
            advanced_result['crossmatch_required'] = True
        
        # فحص التوافق المتقاطع
        if donor_type != recipient_type:
            advanced_result['crossmatch_required'] = True
            advanced_result['additional_tests_needed'].append('فحص التوافق المتقاطع')
        
        # فحص الأجسام المضادة
        if recipient_type in ['AB-', 'A-', 'B-']:
            advanced_result['additional_tests_needed'].append('فحص الأجسام المضادة')
        
        return advanced_result
    
    def _calculate_compatibility_percentage(self, donor_type: str, recipient_type: str, advanced_result: Dict) -> float:
        """حساب نسبة التوافق"""
        
        basic_compatibility = self._check_basic_compatibility(donor_type, recipient_type)
        
        if not basic_compatibility['compatible']:
            return 0.0
        
        # البدء بـ 100% للتوافق الأساسي
        percentage = 100.0
        
        # تقليل النسبة بناءً على العوامل المتقدمة
        if advanced_result['crossmatch_required']:
            percentage -= 10.0
        
        if len(advanced_result['additional_tests_needed']) > 0:
            percentage -= len(advanced_result['additional_tests_needed']) * 5.0
        
        # تقليل إضافي للفصائل المختلفة
        if donor_type != recipient_type:
            percentage -= 5.0
        
        return max(percentage, 70.0)  # حد أدنى 70% للتوافق الأساسي
    
    def _identify_compatibility_risks(self, donor_type: str, recipient_type: str) -> List[str]:
        """تحديد مخاطر التوافق"""
        
        risks = []
        
        # مخاطر عدم التوافق الأساسي
        basic_compatibility = self._check_basic_compatibility(donor_type, recipient_type)
        if not basic_compatibility['compatible']:
            risks.append('عدم توافق فصائل الدم - خطر تفاعل انحلالي')
        
        # مخاطر الفصائل النادرة
        if donor_type in ['AB-', 'B-'] and recipient_type != donor_type:
            risks.append('فصيلة دم نادرة - يتطلب فحص دقيق')
        
        # مخاطر العامل الريزوسي
        if donor_type.endswith('+') and recipient_type.endswith('-'):
            risks.append('عدم توافق العامل الريزوسي - خطر تحسس')
        
        # مخاطر الأجسام المضادة
        if recipient_type in ['A-', 'B-', 'AB-']:
            risks.append('احتمالية وجود أجسام مضادة نادرة')
        
        return risks
    
    def _recommend_blood_components(self, donor_type: str, recipient_type: str, compatibility_percentage: float) -> List[str]:
        """اقتراح مكونات الدم المناسبة"""
        
        recommendations = []
        
        if compatibility_percentage >= 95:
            recommendations.extend([
                BloodComponentType.WHOLE_BLOOD.value,
                BloodComponentType.RED_BLOOD_CELLS.value,
                BloodComponentType.PLASMA.value
            ])
        elif compatibility_percentage >= 85:
            recommendations.extend([
                BloodComponentType.RED_BLOOD_CELLS.value,
                BloodComponentType.PLASMA.value
            ])
        elif compatibility_percentage >= 75:
            recommendations.append(BloodComponentType.RED_BLOOD_CELLS.value)
        else:
            recommendations.append('يتطلب فحص توافق متقدم')
        
        # توصيات خاصة بالفصائل
        if donor_type == 'AB+' or donor_type == 'AB-':
            recommendations.append(BloodComponentType.PLASMA.value)
        
        if donor_type == 'O-':
            recommendations.append(BloodComponentType.RED_BLOOD_CELLS.value)
        
        return list(set(recommendations))  # إزالة التكرار
    
    def _categorize_risk_level(self, compatibility_percentage: float) -> str:
        """تصنيف مستوى الخطر"""
        
        if compatibility_percentage >= 95:
            return 'منخفض'
        elif compatibility_percentage >= 85:
            return 'متوسط'
        elif compatibility_percentage >= 75:
            return 'عالي'
        else:
            return 'عالي جداً'
    
    def _generate_safety_recommendations(self, result: BloodCompatibilityResult) -> List[str]:
        """إنتاج توصيات السلامة"""
        
        recommendations = []
        
        if not result.is_compatible:
            recommendations.append('⚠️ عدم إجراء نقل الدم - عدم توافق كامل')
            return recommendations
        
        if result.crossmatch_required:
            recommendations.append('إجراء فحص التوافق المتقاطع قبل النقل')
        
        if result.compatibility_percentage < 90:
            recommendations.append('مراقبة دقيقة للمريض أثناء وبعد النقل')
        
        if len(result.risk_factors) > 0:
            recommendations.append('توفير أدوية الطوارئ لعلاج التفاعلات المحتملة')
        
        recommendations.extend([
            'فحص العلامات الحيوية كل 15 دقيقة في أول ساعة',
            'مراقبة أعراض التفاعل الانحلالي',
            'توثيق جميع المعلومات في سجل المريض'
        ])
        
        return recommendations
    
    def _analyze_blood_shortage(self, blood_type_summary: Dict) -> Dict:
        """تحليل نقص الدم"""
        
        # أهداف المخزون المثالية (وحدات)
        ideal_inventory = {
            'O+': 100, 'A+': 80, 'B+': 60, 'AB+': 20,
            'O-': 40, 'A-': 30, 'B-': 25, 'AB-': 15
        }
        
        shortage_analysis = {
            'critical_shortages': [],
            'moderate_shortages': [],
            'adequate_levels': [],
            'surplus': []
        }
        
        for blood_type, ideal_units in ideal_inventory.items():
            current_units = blood_type_summary.get(blood_type, {}).get('total_units', 0)
            shortage_percentage = (ideal_units - current_units) / ideal_units * 100
            
            if shortage_percentage >= 75:
                shortage_analysis['critical_shortages'].append({
                    'blood_type': blood_type,
                    'current_units': current_units,
                    'needed_units': ideal_units,
                    'shortage_percentage': round(shortage_percentage, 1)
                })
            elif shortage_percentage >= 50:
                shortage_analysis['moderate_shortages'].append({
                    'blood_type': blood_type,
                    'current_units': current_units,
                    'needed_units': ideal_units,
                    'shortage_percentage': round(shortage_percentage, 1)
                })
            elif shortage_percentage <= -20:  # فائض 20% أو أكثر
                shortage_analysis['surplus'].append({
                    'blood_type': blood_type,
                    'current_units': current_units,
                    'ideal_units': ideal_units,
                    'surplus_percentage': round(-shortage_percentage, 1)
                })
            else:
                shortage_analysis['adequate_levels'].append({
                    'blood_type': blood_type,
                    'current_units': current_units,
                    'ideal_units': ideal_units
                })
        
        return shortage_analysis
    
    def _determine_collection_priorities(self, blood_type_summary: Dict) -> List[Dict]:
        """تحديد أولويات التجميع"""
        
        priorities = []
        
        # حساب الأولوية لكل فصيلة دم
        for blood_type in BloodType:
            current_units = blood_type_summary.get(blood_type.value, {}).get('total_units', 0)
            expiring_units = blood_type_summary.get(blood_type.value, {}).get('expiring_soon', 0)
            
            # حساب نقاط الأولوية
            priority_score = 0
            
            # نقاط النقص
            if current_units < 20:
                priority_score += 50
            elif current_units < 50:
                priority_score += 30
            elif current_units < 80:
                priority_score += 10
            
            # نقاط انتهاء الصلاحية
            if expiring_units > current_units * 0.3:
                priority_score += 20
            
            # نقاط ندرة الفصيلة
            if blood_type.value in ['AB-', 'B-', 'A-', 'O-']:
                priority_score += 25
            
            # نقاط الطلب العالي
            if blood_type.value in ['O+', 'A+']:
                priority_score += 15
            
            priorities.append({
                'blood_type': blood_type.value,
                'priority_score': priority_score,
                'current_units': current_units,
                'expiring_units': expiring_units,
                'priority_level': self._categorize_priority_level(priority_score)
            })
        
        # ترتيب حسب الأولوية
        priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priorities
    
    def _categorize_priority_level(self, score: int) -> str:
        """تصنيف مستوى الأولوية"""
        
        if score >= 80:
            return 'حرج'
        elif score >= 60:
            return 'عالي'
        elif score >= 40:
            return 'متوسط'
        else:
            return 'منخفض'
    
    def _generate_inventory_recommendations(self, blood_type_summary: Dict, shortage_analysis: Dict) -> List[str]:
        """إنتاج توصيات المخزون"""
        
        recommendations = []
        
        # توصيات النقص الحرج
        if shortage_analysis['critical_shortages']:
            critical_types = [item['blood_type'] for item in shortage_analysis['critical_shortages']]
            recommendations.append(f"🚨 نقص حرج في فصائل: {', '.join(critical_types)}")
            recommendations.append("تفعيل بروتوكول الطوارئ لجمع الدم")
        
        # توصيات النقص المتوسط
        if shortage_analysis['moderate_shortages']:
            moderate_types = [item['blood_type'] for item in shortage_analysis['moderate_shortages']]
            recommendations.append(f"⚠️ نقص متوسط في فصائل: {', '.join(moderate_types)}")
            recommendations.append("زيادة حملات التبرع المستهدفة")
        
        # توصيات الفائض
        if shortage_analysis['surplus']:
            surplus_types = [item['blood_type'] for item in shortage_analysis['surplus']]
            recommendations.append(f"📈 فائض في فصائل: {', '.join(surplus_types)}")
            recommendations.append("إعادة توزيع الفائض على المراكز الأخرى")
        
        # توصيات عامة
        recommendations.extend([
            "مراجعة تواريخ انتهاء الصلاحية يومياً",
            "تحديث قوائم المتبرعين النشطين",
            "تنسيق مع المستشفيات لتوقع الاحتياجات"
        ])
        
        return recommendations
    
    def _calculate_donor_statistics(self, donor: DonorProfile) -> Dict:
        """حساب إحصائيات المتبرع"""
        
        # حساب الإحصائيات الأساسية
        stats = {
            'total_donations': donor.total_donations,
            'donation_frequency_days': 0,
            'last_donation_days_ago': 0,
            'next_eligible_days': 0,
            'annual_donations': 0,
            'lifetime_impact_estimate': 0
        }
        
        # حساب تكرار التبرع
        if donor.total_donations > 1 and donor.donation_history:
            total_days = 0
            for i in range(1, len(donor.donation_history)):
                prev_date = datetime.fromisoformat(donor.donation_history[i-1]['date'])
                curr_date = datetime.fromisoformat(donor.donation_history[i]['date'])
                total_days += (curr_date - prev_date).days
            
            stats['donation_frequency_days'] = total_days / (len(donor.donation_history) - 1)
        
        # حساب آخر تبرع
        if donor.last_donation_date:
            stats['last_donation_days_ago'] = (datetime.now() - donor.last_donation_date).days
        
        # حساب الأهلية التالية
        if donor.next_eligible_date:
            days_to_next = (donor.next_eligible_date - datetime.now()).days
            stats['next_eligible_days'] = max(0, days_to_next)
        
        # تقدير التبرعات السنوية
        if donor.donation_history:
            first_donation = datetime.fromisoformat(donor.donation_history[0]['date'])
            years_active = max(1, (datetime.now() - first_donation).days / 365)
            stats['annual_donations'] = round(donor.total_donations / years_active, 1)
        
        # تقدير التأثير مدى الحياة
        stats['lifetime_impact_estimate'] = donor.total_donations * 3  # 3 أرواح لكل تبرع
        
        return stats
    
    def _analyze_donation_impact(self, donor: DonorProfile) -> Dict:
        """تحليل تأثير التبرعات"""
        
        impact = {
            'lives_saved_estimate': donor.total_donations * 3,
            'blood_units_contributed': donor.total_donations,
            'community_ranking': 'متوسط',
            'special_contributions': [],
            'emergency_responses': 0
        }
        
        # تحديد الترتيب في المجتمع
        if donor.total_donations >= 50:
            impact['community_ranking'] = 'بطل'
        elif donor.total_donations >= 25:
            impact['community_ranking'] = 'متقدم'
        elif donor.total_donations >= 10:
            impact['community_ranking'] = 'نشط'
        
        # المساهمات الخاصة
        if donor.blood_type == 'O-':
            impact['special_contributions'].append('متبرع عام - يمكن التبرع لجميع الفصائل')
        
        if donor.blood_type in ['AB-', 'B-', 'A-']:
            impact['special_contributions'].append('فصيلة نادرة - تبرع عالي القيمة')
        
        # حساب الاستجابات الطارئة
        for donation in donor.donation_history:
            if donation.get('emergency_response', False):
                impact['emergency_responses'] += 1
        
        return impact
    
    def _calculate_donor_achievements(self, donor: DonorProfile) -> List[Dict]:
        """حساب إنجازات المتبرع"""
        
        achievements = []
        
        # إنجازات عدد التبرعات
        donation_milestones = [
            (1, 'المتبرع الأول', '🩸'),
            (5, 'متبرع نشط', '⭐'),
            (10, 'متبرع ملتزم', '🏆'),
            (25, 'متبرع متقدم', '🥇'),
            (50, 'بطل التبرع', '👑'),
            (100, 'أسطورة التبرع', '🌟')
        ]
        
        for milestone, title, icon in donation_milestones:
            if donor.total_donations >= milestone:
                achievements.append({
                    'title': title,
                    'icon': icon,
                    'description': f'تبرع {milestone} مرة أو أكثر',
                    'achieved_date': 'محقق',
                    'type': 'donation_count'
                })
        
        # إنجازات خاصة
        if donor.blood_type == 'O-':
            achievements.append({
                'title': 'المتبرع العام',
                'icon': '🌍',
                'description': 'فصيلة دم يمكن نقلها لجميع المرضى',
                'achieved_date': 'محقق',
                'type': 'special_blood_type'
            })
        
        if donor.blood_type in ['AB-', 'B-', 'A-']:
            achievements.append({
                'title': 'المتبرع النادر',
                'icon': '💎',
                'description': 'فصيلة دم نادرة وقيمة',
                'achieved_date': 'محقق',
                'type': 'rare_blood_type'
            })
        
        # إنجازات الاستمرارية
        if donor.donation_history and len(donor.donation_history) >= 3:
            # فحص الانتظام
            dates = [datetime.fromisoformat(d['date']) for d in donor.donation_history[-3:]]
            intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            
            if all(50 <= interval <= 70 for interval in intervals):
                achievements.append({
                    'title': 'المتبرع المنتظم',
                    'icon': '📅',
                    'description': 'تبرع منتظم كل 8 أسابيع',
                    'achieved_date': 'محقق',
                    'type': 'regularity'
                })
        
        return achievements
    
    def _suggest_next_donation(self, donor: DonorProfile) -> Dict:
        """اقتراح التبرع التالي"""
        
        suggestion = {
            'can_donate_now': False,
            'next_eligible_date': None,
            'recommended_component': BloodComponentType.WHOLE_BLOOD.value,
            'estimated_impact': 'متوسط',
            'special_opportunities': []
        }
        
        # فحص الأهلية الحالية
        if donor.next_eligible_date and donor.next_eligible_date <= datetime.now():
            suggestion['can_donate_now'] = True
        else:
            suggestion['next_eligible_date'] = donor.next_eligible_date.isoformat() if donor.next_eligible_date else None
        
        # اقتراح المكون المناسب
        if donor.blood_type in ['AB+', 'AB-']:
            suggestion['recommended_component'] = BloodComponentType.PLASMA.value
            suggestion['estimated_impact'] = 'عالي'
        elif donor.blood_type == 'O-':
            suggestion['recommended_component'] = BloodComponentType.RED_BLOOD_CELLS.value
            suggestion['estimated_impact'] = 'عالي جداً'
        
        # الفرص الخاصة
        if donor.blood_type in ['AB-', 'B-', 'A-', 'O-']:
            suggestion['special_opportunities'].append('برنامج الفصائل النادرة')
        
        if donor.total_donations >= 10:
            suggestion['special_opportunities'].append('برنامج المتبرعين المتقدمين')
        
        return suggestion
    
    def _calculate_donor_ranking(self, donor: DonorProfile) -> Dict:
        """حساب ترتيب المتبرع"""
        
        # حساب النقاط الإجمالية
        total_score = 0
        
        # نقاط التبرعات
        total_score += donor.total_donations * 10
        
        # نقاط فصيلة الدم
        if donor.blood_type == 'O-':
            total_score += 50  # متبرع عام
        elif donor.blood_type in ['AB-', 'B-', 'A-']:
            total_score += 30  # فصيلة نادرة
        
        # نقاط الانتظام
        if donor.donation_history and len(donor.donation_history) >= 5:
            total_score += 25
        
        # نقاط المكافآت
        total_score += donor.rewards_points // 10
        
        # تحديد المستوى
        if total_score >= 1000:
            level = 'أسطوري'
            percentile = 99
        elif total_score >= 500:
            level = 'بطل'
            percentile = 95
        elif total_score >= 250:
            level = 'متقدم'
            percentile = 85
        elif total_score >= 100:
            level = 'نشط'
            percentile = 70
        else:
            level = 'مبتدئ'
            percentile = 50
        
        return {
            'total_score': total_score,
            'level': level,
            'percentile': percentile,
            'next_level_points_needed': self._calculate_points_to_next_level(total_score),
            'achievements_unlocked': len(self._calculate_donor_achievements(donor))
        }
    
    def _calculate_points_to_next_level(self, current_score: int) -> int:
        """حساب النقاط المطلوبة للمستوى التالي"""
        
        level_thresholds = [100, 250, 500, 1000]
        
        for threshold in level_thresholds:
            if current_score < threshold:
                return threshold - current_score
        
        return 0  # وصل للمستوى الأقصى
    
    def _calculate_donor_compatibility_score(self, donor: DonorProfile, request: BloodRequest) -> float:
        """حساب نقاط توافق المتبرع مع الطلب"""
        
        score = 0.0
        
        # نقاط التوافق الأساسي
        if donor.blood_type == request.blood_type_needed:
            score += 50.0  # توافق مثالي
        else:
            # فحص التوافق من المصفوفة
            compatible_recipients = self.compatibility_matrix.get(donor.blood_type, [])
            if request.blood_type_needed in compatible_recipients:
                score += 40.0  # توافق جيد
        
        # نقاط الخبرة
        score += min(donor.total_donations * 2, 20.0)
        
        # نقاط الموثوقية
        if donor.donation_status == DonationStatus.ELIGIBLE.value:
            score += 15.0
        
        # نقاط الاستجابة السريعة
        if donor.last_donation_date:
            days_since_last = (datetime.now() - donor.last_donation_date).days
            if days_since_last >= self.system_settings['donation_interval_days']:
                score += 10.0
        else:
            score += 5.0  # متبرع جديد
        
        # نقاط الطوارئ
        if request.urgency_level == UrgencyLevel.CRITICAL.value:
            # إضافة نقاط للمتبرعين ذوي الاستجابة السريعة
            emergency_responses = sum(1 for d in donor.donation_history if d.get('emergency_response', False))
            score += emergency_responses * 3
        
        return min(score, 100.0)  # حد أقصى 100
    
    def _start_monitoring_services(self):
        """بدء خدمات المراقبة"""
        
        def inventory_monitor():
            """مراقبة المخزون وانتهاء الصلاحية"""
            while True:
                try:
                    # فحص انتهاء الصلاحية
                    expiring_items = []
                    for item in self.blood_inventory.values():
                        days_to_expiry = (item.expiry_date - datetime.now()).days
                        if days_to_expiry <= 7:
                            expiring_items.append(item)
                    
                    if expiring_items:
                        current_app.logger.warning(f"تحذير: {len(expiring_items)} وحدة دم ستنتهي صلاحيتها قريباً")
                    
                    # انتظار 6 ساعات
                    time.sleep(6 * 3600)
                    
                except Exception as e:
                    current_app.logger.error(f"خطأ في مراقبة المخزون: {str(e)}")
                    time.sleep(3600)  # انتظار ساعة في حالة الخطأ
        
        def emergency_alert_monitor():
            """مراقبة تنبيهات الطوارئ"""
            while True:
                try:
                    # فحص التنبيهات المنتهية الصلاحية
                    expired_alerts = []
                    for alert in self.emergency_alerts.values():
                        if alert.expires_at <= datetime.now() and alert.status == 'active':
                            alert.status = 'expired'
                            expired_alerts.append(alert)
                    
                    if expired_alerts:
                        current_app.logger.info(f"انتهت صلاحية {len(expired_alerts)} تنبيه طوارئ")
                    
                    # انتظار 30 دقيقة
                    time.sleep(30 * 60)
                    
                except Exception as e:
                    current_app.logger.error(f"خطأ في مراقبة تنبيهات الطوارئ: {str(e)}")
                    time.sleep(600)  # انتظار 10 دقائق في حالة الخطأ
        
        # بدء خدمات المراقبة في خيوط منفصلة
        inventory_thread = threading.Thread(target=inventory_monitor, daemon=True)
        emergency_thread = threading.Thread(target=emergency_alert_monitor, daemon=True)
        
        inventory_thread.start()
        emergency_thread.start()

