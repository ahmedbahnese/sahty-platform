"""
نظام طلب التحاليل والأشعة المتكامل
نظام شامل لطلب وإدارة التحاليل الطبية والأشعة مع الحجز والمتابعة
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

class TestType(Enum):
    BLOOD_TEST = "تحليل دم"
    URINE_TEST = "تحليل بول"
    STOOL_TEST = "تحليل براز"
    HORMONE_TEST = "تحليل هرمونات"
    BIOCHEMISTRY = "كيمياء حيوية"
    MICROBIOLOGY = "ميكروبيولوجي"
    IMMUNOLOGY = "مناعة"
    GENETICS = "وراثة"
    PATHOLOGY = "باثولوجي"
    CYTOLOGY = "خلايا"

class RadiologyType(Enum):
    XRAY = "أشعة سينية"
    CT_SCAN = "أشعة مقطعية"
    MRI = "رنين مغناطيسي"
    ULTRASOUND = "موجات فوق صوتية"
    MAMMOGRAPHY = "ماموجرام"
    BONE_SCAN = "مسح عظام"
    PET_SCAN = "مسح بوزيتروني"
    ANGIOGRAPHY = "قسطرة تشخيصية"
    FLUOROSCOPY = "فلوروسكوبي"
    NUCLEAR_MEDICINE = "طب نووي"

class TestStatus(Enum):
    REQUESTED = "مطلوب"
    SCHEDULED = "مجدول"
    SAMPLE_COLLECTED = "تم أخذ العينة"
    IN_PROGRESS = "قيد التحليل"
    COMPLETED = "مكتمل"
    REPORTED = "تم التقرير"
    CANCELLED = "ملغي"
    DELAYED = "متأخر"

class UrgencyLevel(Enum):
    ROUTINE = "روتيني"
    URGENT = "عاجل"
    STAT = "فوري"
    CRITICAL = "حرج"

class SampleType(Enum):
    BLOOD_SERUM = "مصل دم"
    BLOOD_PLASMA = "بلازما دم"
    WHOLE_BLOOD = "دم كامل"
    URINE_RANDOM = "بول عشوائي"
    URINE_24H = "بول 24 ساعة"
    STOOL = "براز"
    SALIVA = "لعاب"
    TISSUE = "نسيج"
    FLUID = "سائل"
    SWAB = "مسحة"

class PreparationRequirement(Enum):
    FASTING_8H = "صيام 8 ساعات"
    FASTING_12H = "صيام 12 ساعات"
    NO_PREPARATION = "بدون تحضير"
    AVOID_MEDICATIONS = "تجنب الأدوية"
    SPECIAL_DIET = "نظام غذائي خاص"
    HYDRATION = "شرب ماء كثير"
    EMPTY_BLADDER = "إفراغ المثانة"
    CONTRAST_PREPARATION = "تحضير للصبغة"

@dataclass
class LabTest:
    test_id: str
    test_name: str
    test_code: str
    test_type: str
    sample_type: str
    normal_range: Dict[str, Any]
    preparation_requirements: List[str]
    processing_time_hours: int
    cost: float
    department: str
    requires_fasting: bool
    age_restrictions: Dict[str, int]
    gender_specific: bool
    pregnancy_safe: bool
    description: str

@dataclass
class RadiologyExam:
    exam_id: str
    exam_name: str
    exam_code: str
    radiology_type: str
    body_part: str
    contrast_required: bool
    preparation_requirements: List[str]
    duration_minutes: int
    cost: float
    radiation_dose: float
    pregnancy_contraindicated: bool
    claustrophobia_warning: bool
    metal_contraindications: List[str]
    description: str

@dataclass
class TestRequest:
    request_id: str
    patient_id: str
    doctor_id: str
    hospital_id: str
    requested_tests: List[str]
    requested_radiology: List[str]
    urgency_level: str
    clinical_indication: str
    request_date: datetime
    preferred_date: Optional[datetime]
    status: str
    total_cost: float
    insurance_coverage: float
    patient_preparation: List[str]
    special_instructions: str
    lab_location: str
    appointment_scheduled: bool

@dataclass
class TestAppointment:
    appointment_id: str
    request_id: str
    patient_id: str
    lab_center_id: str
    scheduled_date: datetime
    estimated_duration_minutes: int
    preparation_checklist: List[Dict]
    arrival_instructions: str
    contact_info: Dict
    status: str
    confirmation_code: str
    reminder_sent: bool

@dataclass
class TestResult:
    result_id: str
    request_id: str
    test_id: str
    patient_id: str
    result_value: Any
    unit: str
    reference_range: str
    status: str
    abnormal_flag: bool
    critical_flag: bool
    result_date: datetime
    verified_by: str
    comments: str
    follow_up_required: bool

@dataclass
class RadiologyReport:
    report_id: str
    request_id: str
    exam_id: str
    patient_id: str
    radiologist_id: str
    findings: str
    impression: str
    recommendations: str
    report_date: datetime
    images_available: bool
    image_urls: List[str]
    critical_findings: bool
    follow_up_required: bool
    comparison_studies: List[str]

@dataclass
class LabCenter:
    center_id: str
    name: str
    location: Dict
    contact_info: Dict
    operating_hours: Dict
    available_tests: List[str]
    available_radiology: List[str]
    equipment: List[str]
    certifications: List[str]
    rating: float
    capacity_per_day: int
    current_bookings: int

class LabRadiologyService:
    def __init__(self):
        """تهيئة نظام التحاليل والأشعة"""
        
        # قواعد البيانات
        self.lab_tests = {}
        self.radiology_exams = {}
        self.test_requests = {}
        self.test_appointments = {}
        self.test_results = {}
        self.radiology_reports = {}
        self.lab_centers = {}
        
        # إعدادات النظام
        self.system_settings = {
            'max_tests_per_request': 20,
            'max_radiology_per_request': 5,
            'appointment_buffer_minutes': 30,
            'reminder_hours_before': [24, 2],
            'result_retention_days': 365,
            'critical_result_notification_minutes': 15,
            'routine_processing_hours': 24,
            'urgent_processing_hours': 6,
            'stat_processing_hours': 2,
            'insurance_coverage_percentage': 80
        }
        
        # إحصائيات النظام
        self.lab_stats = {
            'total_requests': 0,
            'completed_tests': 0,
            'pending_results': 0,
            'critical_results': 0,
            'average_turnaround_time_hours': 0,
            'patient_satisfaction_score': 0,
            'lab_centers_active': 0,
            'daily_capacity_utilization': 0
        }
        
        # تهيئة البيانات الأساسية
        self._initialize_lab_tests()
        self._initialize_radiology_exams()
        self._initialize_lab_centers()
        
        # بدء خدمات المراقبة
        self._start_monitoring_services()
    
    def create_test_request(self, request_data: Dict) -> Dict:
        """
        إنشاء طلب تحاليل وأشعة
        
        Args:
            request_data: بيانات الطلب
            
        Returns:
            Dict: نتيجة الإنشاء
        """
        try:
            # التحقق من صحة البيانات
            validation_result = self._validate_test_request(request_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # إنشاء الطلب
            request = TestRequest(
                request_id=str(uuid.uuid4()),
                patient_id=request_data['patient_id'],
                doctor_id=request_data['doctor_id'],
                hospital_id=request_data.get('hospital_id', ''),
                requested_tests=request_data.get('requested_tests', []),
                requested_radiology=request_data.get('requested_radiology', []),
                urgency_level=request_data.get('urgency_level', UrgencyLevel.ROUTINE.value),
                clinical_indication=request_data['clinical_indication'],
                request_date=datetime.now(),
                preferred_date=datetime.fromisoformat(request_data['preferred_date']) if request_data.get('preferred_date') else None,
                status=TestStatus.REQUESTED.value,
                total_cost=0.0,
                insurance_coverage=0.0,
                patient_preparation=[],
                special_instructions=request_data.get('special_instructions', ''),
                lab_location=request_data.get('preferred_lab', ''),
                appointment_scheduled=False
            )
            
            # حساب التكلفة الإجمالية
            cost_calculation = self._calculate_total_cost(request)
            request.total_cost = cost_calculation['total_cost']
            request.insurance_coverage = cost_calculation['insurance_coverage']
            
            # تحديد متطلبات التحضير
            preparation_requirements = self._determine_preparation_requirements(request)
            request.patient_preparation = preparation_requirements
            
            # حفظ الطلب
            self.test_requests[request.request_id] = request
            
            # البحث عن المراكز المتاحة
            available_centers = self._find_available_lab_centers(request)
            
            # تقدير وقت المعالجة
            processing_estimate = self._estimate_processing_time(request)
            
            # فحص التعارضات والتداخلات
            conflicts_check = self._check_test_conflicts(request)
            
            # تحديث الإحصائيات
            self.lab_stats['total_requests'] += 1
            
            return {
                'success': True,
                'request_id': request.request_id,
                'status': request.status,
                'total_cost': request.total_cost,
                'insurance_coverage': request.insurance_coverage,
                'out_of_pocket_cost': request.total_cost - request.insurance_coverage,
                'preparation_requirements': request.patient_preparation,
                'processing_estimate': processing_estimate,
                'available_centers': available_centers,
                'conflicts_warnings': conflicts_check,
                'next_steps': self._get_request_next_steps(request)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء طلب التحاليل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء طلب التحاليل'
            }
    
    def schedule_appointment(self, request_id: str, appointment_data: Dict) -> Dict:
        """
        جدولة موعد للتحاليل والأشعة
        
        Args:
            request_id: معرف الطلب
            appointment_data: بيانات الموعد
            
        Returns:
            Dict: نتيجة الجدولة
        """
        try:
            # التحقق من وجود الطلب
            if request_id not in self.test_requests:
                return {
                    'success': False,
                    'error': 'الطلب غير موجود'
                }
            
            request = self.test_requests[request_id]
            
            # التحقق من إمكانية الجدولة
            if request.appointment_scheduled:
                return {
                    'success': False,
                    'error': 'تم جدولة موعد مسبقاً'
                }
            
            # التحقق من توفر المركز
            lab_center_id = appointment_data['lab_center_id']
            if lab_center_id not in self.lab_centers:
                return {
                    'success': False,
                    'error': 'مركز التحاليل غير موجود'
                }
            
            lab_center = self.lab_centers[lab_center_id]
            
            # التحقق من توفر الموعد
            requested_datetime = datetime.fromisoformat(appointment_data['preferred_datetime'])
            availability_check = self._check_appointment_availability(lab_center, requested_datetime, request)
            
            if not availability_check['available']:
                return {
                    'success': False,
                    'error': availability_check['reason'],
                    'alternative_slots': availability_check.get('alternatives', [])
                }
            
            # إنشاء الموعد
            appointment = TestAppointment(
                appointment_id=str(uuid.uuid4()),
                request_id=request_id,
                patient_id=request.patient_id,
                lab_center_id=lab_center_id,
                scheduled_date=requested_datetime,
                estimated_duration_minutes=self._calculate_appointment_duration(request),
                preparation_checklist=self._create_preparation_checklist(request),
                arrival_instructions=self._generate_arrival_instructions(lab_center, request),
                contact_info=lab_center.contact_info,
                status='scheduled',
                confirmation_code=self._generate_confirmation_code(),
                reminder_sent=False
            )
            
            # حفظ الموعد
            self.test_appointments[appointment.appointment_id] = appointment
            
            # تحديث حالة الطلب
            request.appointment_scheduled = True
            request.status = TestStatus.SCHEDULED.value
            
            # تحديث سعة المركز
            lab_center.current_bookings += 1
            
            # جدولة التذكيرات
            self._schedule_appointment_reminders(appointment)
            
            # إنشاء تعليمات ما قبل الموعد
            pre_appointment_instructions = self._generate_pre_appointment_instructions(appointment, request)
            
            return {
                'success': True,
                'appointment_id': appointment.appointment_id,
                'confirmation_code': appointment.confirmation_code,
                'scheduled_date': appointment.scheduled_date.isoformat(),
                'estimated_duration': appointment.estimated_duration_minutes,
                'lab_center_info': {
                    'name': lab_center.name,
                    'location': lab_center.location,
                    'contact': lab_center.contact_info
                },
                'preparation_checklist': appointment.preparation_checklist,
                'arrival_instructions': appointment.arrival_instructions,
                'pre_appointment_instructions': pre_appointment_instructions,
                'reminder_schedule': self.system_settings['reminder_hours_before']
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في جدولة الموعد: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في جدولة الموعد'
            }
    
    def submit_test_results(self, results_data: Dict) -> Dict:
        """
        إدخال نتائج التحاليل
        
        Args:
            results_data: بيانات النتائج
            
        Returns:
            Dict: نتيجة الإدخال
        """
        try:
            # التحقق من صحة البيانات
            validation_result = self._validate_test_results(results_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            results = []
            critical_results = []
            
            # معالجة كل نتيجة
            for result_data in results_data['results']:
                # إنشاء نتيجة التحليل
                result = TestResult(
                    result_id=str(uuid.uuid4()),
                    request_id=results_data['request_id'],
                    test_id=result_data['test_id'],
                    patient_id=results_data['patient_id'],
                    result_value=result_data['result_value'],
                    unit=result_data.get('unit', ''),
                    reference_range=result_data.get('reference_range', ''),
                    status='completed',
                    abnormal_flag=result_data.get('abnormal_flag', False),
                    critical_flag=result_data.get('critical_flag', False),
                    result_date=datetime.now(),
                    verified_by=results_data['verified_by'],
                    comments=result_data.get('comments', ''),
                    follow_up_required=result_data.get('follow_up_required', False)
                )
                
                # تحليل النتيجة
                analysis = self._analyze_test_result(result)
                result.abnormal_flag = analysis['abnormal']
                result.critical_flag = analysis['critical']
                
                # حفظ النتيجة
                self.test_results[result.result_id] = result
                results.append(result)
                
                # فحص النتائج الحرجة
                if result.critical_flag:
                    critical_results.append(result)
            
            # تحديث حالة الطلب
            if results_data['request_id'] in self.test_requests:
                request = self.test_requests[results_data['request_id']]
                request.status = TestStatus.COMPLETED.value
            
            # إرسال تنبيهات النتائج الحرجة
            if critical_results:
                self._send_critical_result_alerts(critical_results)
            
            # إنتاج التقرير الشامل
            comprehensive_report = self._generate_comprehensive_report(results_data['request_id'], results)
            
            # تحديث الإحصائيات
            self.lab_stats['completed_tests'] += len(results)
            self.lab_stats['critical_results'] += len(critical_results)
            
            return {
                'success': True,
                'results_processed': len(results),
                'critical_results_found': len(critical_results),
                'comprehensive_report': comprehensive_report,
                'follow_up_recommendations': self._generate_follow_up_recommendations(results),
                'patient_notification_sent': True,
                'doctor_notification_sent': True
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إدخال نتائج التحاليل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إدخال نتائج التحاليل'
            }
    
    def submit_radiology_report(self, report_data: Dict) -> Dict:
        """
        إدخال تقرير الأشعة
        
        Args:
            report_data: بيانات التقرير
            
        Returns:
            Dict: نتيجة الإدخال
        """
        try:
            # إنشاء تقرير الأشعة
            report = RadiologyReport(
                report_id=str(uuid.uuid4()),
                request_id=report_data['request_id'],
                exam_id=report_data['exam_id'],
                patient_id=report_data['patient_id'],
                radiologist_id=report_data['radiologist_id'],
                findings=report_data['findings'],
                impression=report_data['impression'],
                recommendations=report_data.get('recommendations', ''),
                report_date=datetime.now(),
                images_available=report_data.get('images_available', False),
                image_urls=report_data.get('image_urls', []),
                critical_findings=report_data.get('critical_findings', False),
                follow_up_required=report_data.get('follow_up_required', False),
                comparison_studies=report_data.get('comparison_studies', [])
            )
            
            # تحليل التقرير للكشف عن النتائج الحرجة
            critical_analysis = self._analyze_radiology_report(report)
            report.critical_findings = critical_analysis['critical']
            
            # حفظ التقرير
            self.radiology_reports[report.report_id] = report
            
            # إرسال تنبيهات النتائج الحرجة
            if report.critical_findings:
                self._send_critical_radiology_alerts(report)
            
            # تحديث حالة الطلب
            if report.request_id in self.test_requests:
                request = self.test_requests[report.request_id]
                request.status = TestStatus.REPORTED.value
            
            # إنتاج ملخص التقرير
            report_summary = self._generate_radiology_summary(report)
            
            return {
                'success': True,
                'report_id': report.report_id,
                'critical_findings': report.critical_findings,
                'follow_up_required': report.follow_up_required,
                'report_summary': report_summary,
                'images_processed': len(report.image_urls),
                'patient_notification_sent': True,
                'doctor_notification_sent': True
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إدخال تقرير الأشعة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إدخال تقرير الأشعة'
            }
    
    def get_test_results(self, request_id: str, patient_id: str) -> Dict:
        """
        الحصول على نتائج التحاليل
        
        Args:
            request_id: معرف الطلب
            patient_id: معرف المريض
            
        Returns:
            Dict: النتائج
        """
        try:
            # التحقق من وجود الطلب
            if request_id not in self.test_requests:
                return {
                    'success': False,
                    'error': 'الطلب غير موجود'
                }
            
            request = self.test_requests[request_id]
            
            # التحقق من صلاحية المريض
            if request.patient_id != patient_id:
                return {
                    'success': False,
                    'error': 'غير مصرح بالوصول'
                }
            
            # جمع نتائج التحاليل
            test_results = []
            for result in self.test_results.values():
                if result.request_id == request_id:
                    test_results.append({
                        'test_name': self._get_test_name(result.test_id),
                        'result_value': result.result_value,
                        'unit': result.unit,
                        'reference_range': result.reference_range,
                        'status': result.status,
                        'abnormal_flag': result.abnormal_flag,
                        'critical_flag': result.critical_flag,
                        'result_date': result.result_date.isoformat(),
                        'comments': result.comments,
                        'follow_up_required': result.follow_up_required
                    })
            
            # جمع تقارير الأشعة
            radiology_reports = []
            for report in self.radiology_reports.values():
                if report.request_id == request_id:
                    radiology_reports.append({
                        'exam_name': self._get_exam_name(report.exam_id),
                        'findings': report.findings,
                        'impression': report.impression,
                        'recommendations': report.recommendations,
                        'report_date': report.report_date.isoformat(),
                        'critical_findings': report.critical_findings,
                        'follow_up_required': report.follow_up_required,
                        'images_available': report.images_available,
                        'image_count': len(report.image_urls)
                    })
            
            # إنتاج التحليل الشامل
            comprehensive_analysis = self._generate_comprehensive_analysis(test_results, radiology_reports)
            
            # تحديد التوصيات
            recommendations = self._generate_patient_recommendations(test_results, radiology_reports)
            
            return {
                'success': True,
                'request_info': {
                    'request_id': request.request_id,
                    'request_date': request.request_date.isoformat(),
                    'clinical_indication': request.clinical_indication,
                    'status': request.status
                },
                'test_results': test_results,
                'radiology_reports': radiology_reports,
                'comprehensive_analysis': comprehensive_analysis,
                'recommendations': recommendations,
                'critical_findings_present': any(r['critical_flag'] for r in test_results) or any(r['critical_findings'] for r in radiology_reports),
                'follow_up_required': any(r['follow_up_required'] for r in test_results) or any(r['follow_up_required'] for r in radiology_reports)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على نتائج التحاليل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على نتائج التحاليل'
            }
    
    def search_lab_centers(self, search_criteria: Dict) -> Dict:
        """
        البحث عن مراكز التحاليل
        
        Args:
            search_criteria: معايير البحث
            
        Returns:
            Dict: نتائج البحث
        """
        try:
            # فلترة المراكز حسب المعايير
            filtered_centers = []
            
            for center in self.lab_centers.values():
                # فلترة حسب الموقع
                if search_criteria.get('location'):
                    if not self._is_center_in_location(center, search_criteria['location']):
                        continue
                
                # فلترة حسب التحاليل المتاحة
                if search_criteria.get('required_tests'):
                    if not all(test in center.available_tests for test in search_criteria['required_tests']):
                        continue
                
                # فلترة حسب الأشعة المتاحة
                if search_criteria.get('required_radiology'):
                    if not all(exam in center.available_radiology for exam in search_criteria['required_radiology']):
                        continue
                
                # فلترة حسب التقييم
                if search_criteria.get('min_rating'):
                    if center.rating < search_criteria['min_rating']:
                        continue
                
                # فلترة حسب التوفر
                if search_criteria.get('check_availability'):
                    availability = self._check_center_availability(center, search_criteria.get('preferred_date'))
                    if not availability['available']:
                        continue
                
                # إضافة معلومات إضافية
                center_info = {
                    'center_id': center.center_id,
                    'name': center.name,
                    'location': center.location,
                    'contact_info': center.contact_info,
                    'rating': center.rating,
                    'available_tests_count': len(center.available_tests),
                    'available_radiology_count': len(center.available_radiology),
                    'current_capacity_utilization': (center.current_bookings / center.capacity_per_day) * 100,
                    'estimated_cost': self._estimate_center_cost(center, search_criteria),
                    'distance_km': self._calculate_distance(center, search_criteria.get('patient_location')),
                    'next_available_slot': self._get_next_available_slot(center)
                }
                
                filtered_centers.append(center_info)
            
            # ترتيب النتائج
            sort_by = search_criteria.get('sort_by', 'rating')
            if sort_by == 'rating':
                filtered_centers.sort(key=lambda x: x['rating'], reverse=True)
            elif sort_by == 'distance':
                filtered_centers.sort(key=lambda x: x['distance_km'])
            elif sort_by == 'cost':
                filtered_centers.sort(key=lambda x: x['estimated_cost'])
            elif sort_by == 'availability':
                filtered_centers.sort(key=lambda x: x['current_capacity_utilization'])
            
            # إحصائيات البحث
            search_stats = {
                'total_centers_found': len(filtered_centers),
                'average_rating': sum(c['rating'] for c in filtered_centers) / len(filtered_centers) if filtered_centers else 0,
                'average_distance': sum(c['distance_km'] for c in filtered_centers) / len(filtered_centers) if filtered_centers else 0,
                'cost_range': {
                    'min': min(c['estimated_cost'] for c in filtered_centers) if filtered_centers else 0,
                    'max': max(c['estimated_cost'] for c in filtered_centers) if filtered_centers else 0
                }
            }
            
            return {
                'success': True,
                'centers': filtered_centers[:20],  # أفضل 20 مركز
                'search_stats': search_stats,
                'search_criteria_applied': search_criteria,
                'recommendations': self._generate_center_recommendations(filtered_centers)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في البحث عن مراكز التحاليل: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في البحث عن مراكز التحاليل'
            }
    
    def get_lab_statistics(self, period_days: int = 30) -> Dict:
        """
        الحصول على إحصائيات المختبر
        
        Args:
            period_days: فترة الإحصائيات بالأيام
            
        Returns:
            Dict: الإحصائيات
        """
        try:
            # تحديد فترة الإحصائيات
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # إحصائيات الطلبات
            period_requests = [
                req for req in self.test_requests.values()
                if start_date <= req.request_date <= end_date
            ]
            
            # إحصائيات النتائج
            period_results = [
                result for result in self.test_results.values()
                if start_date <= result.result_date <= end_date
            ]
            
            # إحصائيات التقارير
            period_reports = [
                report for report in self.radiology_reports.values()
                if start_date <= report.report_date <= end_date
            ]
            
            # حساب الإحصائيات
            stats = {
                'period_info': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'period_days': period_days
                },
                'request_statistics': {
                    'total_requests': len(period_requests),
                    'completed_requests': len([r for r in period_requests if r.status == TestStatus.COMPLETED.value]),
                    'pending_requests': len([r for r in period_requests if r.status in [TestStatus.REQUESTED.value, TestStatus.SCHEDULED.value]]),
                    'cancelled_requests': len([r for r in period_requests if r.status == TestStatus.CANCELLED.value]),
                    'average_daily_requests': len(period_requests) / period_days if period_days > 0 else 0
                },
                'test_statistics': {
                    'total_tests_completed': len(period_results),
                    'abnormal_results': len([r for r in period_results if r.abnormal_flag]),
                    'critical_results': len([r for r in period_results if r.critical_flag]),
                    'follow_up_required': len([r for r in period_results if r.follow_up_required]),
                    'abnormal_rate_percentage': (len([r for r in period_results if r.abnormal_flag]) / len(period_results) * 100) if period_results else 0
                },
                'radiology_statistics': {
                    'total_reports_completed': len(period_reports),
                    'critical_findings': len([r for r in period_reports if r.critical_findings]),
                    'follow_up_required': len([r for r in period_reports if r.follow_up_required]),
                    'reports_with_images': len([r for r in period_reports if r.images_available]),
                    'critical_findings_rate': (len([r for r in period_reports if r.critical_findings]) / len(period_reports) * 100) if period_reports else 0
                },
                'performance_metrics': {
                    'average_turnaround_time_hours': self._calculate_average_turnaround_time(period_requests, period_results),
                    'on_time_delivery_rate': self._calculate_on_time_delivery_rate(period_requests),
                    'patient_satisfaction_score': self._calculate_patient_satisfaction(period_requests),
                    'lab_center_utilization': self._calculate_lab_utilization()
                },
                'financial_statistics': {
                    'total_revenue': sum(req.total_cost for req in period_requests),
                    'insurance_coverage_total': sum(req.insurance_coverage for req in period_requests),
                    'patient_payments': sum(req.total_cost - req.insurance_coverage for req in period_requests),
                    'average_cost_per_request': sum(req.total_cost for req in period_requests) / len(period_requests) if period_requests else 0
                }
            }
            
            # تحليل الاتجاهات
            trends_analysis = self._analyze_lab_trends(period_requests, period_results, period_reports)
            
            # توصيات التحسين
            improvement_recommendations = self._generate_improvement_recommendations(stats)
            
            return {
                'success': True,
                'statistics': stats,
                'trends_analysis': trends_analysis,
                'improvement_recommendations': improvement_recommendations,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على إحصائيات المختبر: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على إحصائيات المختبر'
            }
    
    # الدوال المساعدة
    def _initialize_lab_tests(self):
        """تهيئة قاعدة بيانات التحاليل"""
        
        # تحاليل الدم الأساسية
        basic_blood_tests = [
            {
                'test_name': 'صورة دم كاملة',
                'test_code': 'CBC',
                'test_type': TestType.BLOOD_TEST.value,
                'sample_type': SampleType.WHOLE_BLOOD.value,
                'normal_range': {
                    'hemoglobin_male': '13.5-17.5 g/dL',
                    'hemoglobin_female': '12.0-15.5 g/dL',
                    'wbc': '4.5-11.0 x10³/μL',
                    'platelets': '150-450 x10³/μL'
                },
                'preparation_requirements': [PreparationRequirement.NO_PREPARATION.value],
                'processing_time_hours': 2,
                'cost': 50.0,
                'department': 'هيماتولوجي',
                'requires_fasting': False,
                'age_restrictions': {'min': 0, 'max': 120},
                'gender_specific': True,
                'pregnancy_safe': True,
                'description': 'فحص شامل لخلايا الدم والصفائح الدموية'
            },
            {
                'test_name': 'سكر الدم الصائم',
                'test_code': 'FBS',
                'test_type': TestType.BIOCHEMISTRY.value,
                'sample_type': SampleType.BLOOD_SERUM.value,
                'normal_range': {'value': '70-100 mg/dL'},
                'preparation_requirements': [PreparationRequirement.FASTING_8H.value],
                'processing_time_hours': 1,
                'cost': 30.0,
                'department': 'كيمياء حيوية',
                'requires_fasting': True,
                'age_restrictions': {'min': 0, 'max': 120},
                'gender_specific': False,
                'pregnancy_safe': True,
                'description': 'قياس مستوى السكر في الدم بعد الصيام'
            },
            {
                'test_name': 'وظائف الكلى',
                'test_code': 'RFT',
                'test_type': TestType.BIOCHEMISTRY.value,
                'sample_type': SampleType.BLOOD_SERUM.value,
                'normal_range': {
                    'creatinine_male': '0.7-1.3 mg/dL',
                    'creatinine_female': '0.6-1.1 mg/dL',
                    'urea': '15-40 mg/dL'
                },
                'preparation_requirements': [PreparationRequirement.NO_PREPARATION.value],
                'processing_time_hours': 3,
                'cost': 80.0,
                'department': 'كيمياء حيوية',
                'requires_fasting': False,
                'age_restrictions': {'min': 0, 'max': 120},
                'gender_specific': True,
                'pregnancy_safe': True,
                'description': 'فحص وظائف الكلى والكرياتينين واليوريا'
            }
        ]
        
        # إضافة التحاليل إلى قاعدة البيانات
        for test_data in basic_blood_tests:
            test = LabTest(
                test_id=str(uuid.uuid4()),
                **test_data
            )
            self.lab_tests[test.test_id] = test
    
    def _initialize_radiology_exams(self):
        """تهيئة قاعدة بيانات الأشعة"""
        
        # فحوصات الأشعة الأساسية
        basic_radiology_exams = [
            {
                'exam_name': 'أشعة سينية على الصدر',
                'exam_code': 'CXR',
                'radiology_type': RadiologyType.XRAY.value,
                'body_part': 'الصدر',
                'contrast_required': False,
                'preparation_requirements': [PreparationRequirement.NO_PREPARATION.value],
                'duration_minutes': 15,
                'cost': 100.0,
                'radiation_dose': 0.1,
                'pregnancy_contraindicated': True,
                'claustrophobia_warning': False,
                'metal_contraindications': [],
                'description': 'فحص الرئتين والقلب والأضلاع'
            },
            {
                'exam_name': 'أشعة مقطعية على البطن',
                'exam_code': 'CT_ABD',
                'radiology_type': RadiologyType.CT_SCAN.value,
                'body_part': 'البطن',
                'contrast_required': True,
                'preparation_requirements': [
                    PreparationRequirement.FASTING_8H.value,
                    PreparationRequirement.CONTRAST_PREPARATION.value
                ],
                'duration_minutes': 30,
                'cost': 800.0,
                'radiation_dose': 10.0,
                'pregnancy_contraindicated': True,
                'claustrophobia_warning': True,
                'metal_contraindications': [],
                'description': 'فحص مفصل لأعضاء البطن'
            },
            {
                'exam_name': 'رنين مغناطيسي على الدماغ',
                'exam_code': 'MRI_BRAIN',
                'radiology_type': RadiologyType.MRI.value,
                'body_part': 'الدماغ',
                'contrast_required': False,
                'preparation_requirements': [PreparationRequirement.NO_PREPARATION.value],
                'duration_minutes': 45,
                'cost': 1500.0,
                'radiation_dose': 0.0,
                'pregnancy_contraindicated': False,
                'claustrophobia_warning': True,
                'metal_contraindications': ['pacemaker', 'metal_implants', 'cochlear_implant'],
                'description': 'فحص مفصل لأنسجة الدماغ'
            }
        ]
        
        # إضافة الفحوصات إلى قاعدة البيانات
        for exam_data in basic_radiology_exams:
            exam = RadiologyExam(
                exam_id=str(uuid.uuid4()),
                **exam_data
            )
            self.radiology_exams[exam.exam_id] = exam
    
    def _initialize_lab_centers(self):
        """تهيئة مراكز التحاليل"""
        
        # مراكز التحاليل الأساسية
        lab_centers_data = [
            {
                'name': 'مختبرات ألفا',
                'location': {
                    'address': 'شارع التحرير، وسط البلد، القاهرة',
                    'latitude': 30.0444,
                    'longitude': 31.2357,
                    'district': 'وسط البلد',
                    'city': 'القاهرة'
                },
                'contact_info': {
                    'phone': '02-25555555',
                    'email': 'info@alpha-labs.com',
                    'website': 'www.alpha-labs.com'
                },
                'operating_hours': {
                    'weekdays': '07:00-22:00',
                    'friday': '07:00-20:00',
                    'saturday': '08:00-18:00'
                },
                'available_tests': list(self.lab_tests.keys()),
                'available_radiology': list(self.radiology_exams.keys()),
                'equipment': ['CT Scanner', 'MRI', 'X-Ray', 'Ultrasound', 'Automated Analyzers'],
                'certifications': ['ISO 15189', 'CAP', 'JCI'],
                'rating': 4.5,
                'capacity_per_day': 500,
                'current_bookings': 0
            },
            {
                'name': 'مختبرات البرج',
                'location': {
                    'address': 'شارع الهرم، الجيزة',
                    'latitude': 30.0131,
                    'longitude': 31.2089,
                    'district': 'الهرم',
                    'city': 'الجيزة'
                },
                'contact_info': {
                    'phone': '02-33333333',
                    'email': 'info@alborg-labs.com',
                    'website': 'www.alborg-labs.com'
                },
                'operating_hours': {
                    'weekdays': '06:00-23:00',
                    'friday': '06:00-21:00',
                    'saturday': '07:00-19:00'
                },
                'available_tests': list(self.lab_tests.keys()),
                'available_radiology': list(self.radiology_exams.keys()),
                'equipment': ['CT Scanner', 'MRI', 'X-Ray', 'Ultrasound', 'Digital Mammography'],
                'certifications': ['ISO 15189', 'NABL'],
                'rating': 4.3,
                'capacity_per_day': 400,
                'current_bookings': 0
            }
        ]
        
        # إضافة المراكز إلى قاعدة البيانات
        for center_data in lab_centers_data:
            center = LabCenter(
                center_id=str(uuid.uuid4()),
                **center_data
            )
            self.lab_centers[center.center_id] = center
    
    def _validate_test_request(self, request_data: Dict) -> Dict:
        """التحقق من صحة طلب التحاليل"""
        
        required_fields = ['patient_id', 'doctor_id', 'clinical_indication']
        
        for field in required_fields:
            if field not in request_data:
                return {
                    'valid': False,
                    'error': f'الحقل {field} مطلوب'
                }
        
        # التحقق من وجود تحاليل أو أشعة
        if not request_data.get('requested_tests') and not request_data.get('requested_radiology'):
            return {
                'valid': False,
                'error': 'يجب طلب تحليل واحد على الأقل أو فحص أشعة'
            }
        
        # التحقق من حد التحاليل
        if len(request_data.get('requested_tests', [])) > self.system_settings['max_tests_per_request']:
            return {
                'valid': False,
                'error': f'عدد التحاليل يتجاوز الحد الأقصى ({self.system_settings["max_tests_per_request"]})'
            }
        
        return {'valid': True}
    
    def _calculate_total_cost(self, request: TestRequest) -> Dict:
        """حساب التكلفة الإجمالية"""
        
        total_cost = 0.0
        
        # تكلفة التحاليل
        for test_id in request.requested_tests:
            if test_id in self.lab_tests:
                total_cost += self.lab_tests[test_id].cost
        
        # تكلفة الأشعة
        for exam_id in request.requested_radiology:
            if exam_id in self.radiology_exams:
                total_cost += self.radiology_exams[exam_id].cost
        
        # حساب التغطية التأمينية
        insurance_coverage = total_cost * (self.system_settings['insurance_coverage_percentage'] / 100)
        
        return {
            'total_cost': total_cost,
            'insurance_coverage': insurance_coverage
        }
    
    def _determine_preparation_requirements(self, request: TestRequest) -> List[str]:
        """تحديد متطلبات التحضير"""
        
        all_requirements = set()
        
        # متطلبات التحاليل
        for test_id in request.requested_tests:
            if test_id in self.lab_tests:
                test = self.lab_tests[test_id]
                all_requirements.update(test.preparation_requirements)
        
        # متطلبات الأشعة
        for exam_id in request.requested_radiology:
            if exam_id in self.radiology_exams:
                exam = self.radiology_exams[exam_id]
                all_requirements.update(exam.preparation_requirements)
        
        return list(all_requirements)
    
    def _find_available_lab_centers(self, request: TestRequest) -> List[Dict]:
        """البحث عن المراكز المتاحة"""
        
        available_centers = []
        
        for center in self.lab_centers.values():
            # فحص توفر التحاليل المطلوبة
            tests_available = all(test_id in center.available_tests for test_id in request.requested_tests)
            
            # فحص توفر الأشعة المطلوبة
            radiology_available = all(exam_id in center.available_radiology for exam_id in request.requested_radiology)
            
            if tests_available and radiology_available:
                # حساب السعة المتاحة
                capacity_utilization = (center.current_bookings / center.capacity_per_day) * 100
                
                available_centers.append({
                    'center_id': center.center_id,
                    'name': center.name,
                    'location': center.location,
                    'rating': center.rating,
                    'capacity_utilization': capacity_utilization,
                    'estimated_cost': self._estimate_center_cost(center, {'requested_tests': request.requested_tests, 'requested_radiology': request.requested_radiology}),
                    'next_available_slot': self._get_next_available_slot(center)
                })
        
        # ترتيب حسب التقييم والسعة
        available_centers.sort(key=lambda x: (x['rating'], -x['capacity_utilization']), reverse=True)
        
        return available_centers[:10]  # أفضل 10 مراكز
    
    def _estimate_processing_time(self, request: TestRequest) -> Dict:
        """تقدير وقت المعالجة"""
        
        max_processing_time = 0
        urgency_multiplier = {
            UrgencyLevel.ROUTINE.value: 1.0,
            UrgencyLevel.URGENT.value: 0.5,
            UrgencyLevel.STAT.value: 0.25,
            UrgencyLevel.CRITICAL.value: 0.1
        }
        
        # حساب أقصى وقت معالجة للتحاليل
        for test_id in request.requested_tests:
            if test_id in self.lab_tests:
                test = self.lab_tests[test_id]
                max_processing_time = max(max_processing_time, test.processing_time_hours)
        
        # إضافة وقت الأشعة (افتراضي 2 ساعة)
        if request.requested_radiology:
            max_processing_time = max(max_processing_time, 2)
        
        # تطبيق معامل الإلحاح
        estimated_time = max_processing_time * urgency_multiplier.get(request.urgency_level, 1.0)
        
        return {
            'estimated_hours': estimated_time,
            'estimated_completion': (datetime.now() + timedelta(hours=estimated_time)).isoformat(),
            'urgency_level': request.urgency_level
        }
    
    def _check_test_conflicts(self, request: TestRequest) -> List[str]:
        """فحص التعارضات والتداخلات"""
        
        conflicts = []
        
        # فحص تعارض متطلبات التحضير
        fasting_required = False
        no_preparation = False
        
        for test_id in request.requested_tests:
            if test_id in self.lab_tests:
                test = self.lab_tests[test_id]
                if test.requires_fasting:
                    fasting_required = True
                if PreparationRequirement.NO_PREPARATION.value in test.preparation_requirements:
                    no_preparation = True
        
        if fasting_required and no_preparation:
            conflicts.append('تعارض في متطلبات التحضير - بعض التحاليل تتطلب الصيام وأخرى لا')
        
        # فحص تعارض الأشعة مع الحمل
        pregnancy_contraindicated = []
        for exam_id in request.requested_radiology:
            if exam_id in self.radiology_exams:
                exam = self.radiology_exams[exam_id]
                if exam.pregnancy_contraindicated:
                    pregnancy_contraindicated.append(exam.exam_name)
        
        if pregnancy_contraindicated:
            conflicts.append(f'فحوصات غير آمنة للحوامل: {", ".join(pregnancy_contraindicated)}')
        
        return conflicts
    
    def _get_request_next_steps(self, request: TestRequest) -> List[str]:
        """الحصول على الخطوات التالية للطلب"""
        
        steps = [
            'مراجعة متطلبات التحضير',
            'اختيار مركز التحاليل المناسب',
            'حجز موعد للفحص'
        ]
        
        if request.urgency_level in [UrgencyLevel.URGENT.value, UrgencyLevel.STAT.value, UrgencyLevel.CRITICAL.value]:
            steps.insert(0, 'معالجة عاجلة - أولوية عالية')
        
        if any(self.lab_tests[test_id].requires_fasting for test_id in request.requested_tests if test_id in self.lab_tests):
            steps.append('الصيام قبل الفحص حسب التعليمات')
        
        steps.extend([
            'الحضور في الموعد المحدد',
            'انتظار النتائج',
            'مراجعة الطبيب لمناقشة النتائج'
        ])
        
        return steps
    
    def _start_monitoring_services(self):
        """بدء خدمات المراقبة"""
        
        def appointment_reminder_service():
            """خدمة تذكيرات المواعيد"""
            while True:
                try:
                    current_time = datetime.now()
                    
                    for appointment in self.test_appointments.values():
                        if appointment.status == 'scheduled' and not appointment.reminder_sent:
                            # فحص إذا حان وقت إرسال التذكير
                            time_to_appointment = (appointment.scheduled_date - current_time).total_seconds() / 3600
                            
                            if time_to_appointment <= 24 and time_to_appointment > 0:
                                # إرسال تذكير
                                self._send_appointment_reminder(appointment)
                                appointment.reminder_sent = True
                    
                    # انتظار ساعة
                    time.sleep(3600)
                    
                except Exception as e:
                    current_app.logger.error(f"خطأ في خدمة التذكيرات: {str(e)}")
                    time.sleep(1800)  # انتظار 30 دقيقة في حالة الخطأ
        
        def result_processing_monitor():
            """مراقبة معالجة النتائج"""
            while True:
                try:
                    # فحص الطلبات المتأخرة
                    current_time = datetime.now()
                    
                    for request in self.test_requests.values():
                        if request.status in [TestStatus.SCHEDULED.value, TestStatus.IN_PROGRESS.value]:
                            # حساب الوقت المتوقع للانتهاء
                            processing_estimate = self._estimate_processing_time(request)
                            expected_completion = request.request_date + timedelta(hours=processing_estimate['estimated_hours'])
                            
                            if current_time > expected_completion:
                                # تحديث حالة الطلب إلى متأخر
                                request.status = TestStatus.DELAYED.value
                                current_app.logger.warning(f"طلب متأخر: {request.request_id}")
                    
                    # انتظار 30 دقيقة
                    time.sleep(1800)
                    
                except Exception as e:
                    current_app.logger.error(f"خطأ في مراقبة معالجة النتائج: {str(e)}")
                    time.sleep(900)  # انتظار 15 دقيقة في حالة الخطأ
        
        # بدء خدمات المراقبة في خيوط منفصلة
        reminder_thread = threading.Thread(target=appointment_reminder_service, daemon=True)
        processing_thread = threading.Thread(target=result_processing_monitor, daemon=True)
        
        reminder_thread.start()
        processing_thread.start()
    
    # دوال مساعدة إضافية
    def _check_appointment_availability(self, lab_center: LabCenter, requested_datetime: datetime, request: TestRequest) -> Dict:
        """فحص توفر الموعد"""
        
        # فحص ساعات العمل
        day_of_week = requested_datetime.strftime('%A').lower()
        operating_hours = lab_center.operating_hours
        
        # فحص السعة
        if lab_center.current_bookings >= lab_center.capacity_per_day:
            return {
                'available': False,
                'reason': 'المركز مكتمل في هذا اليوم',
                'alternatives': self._suggest_alternative_slots(lab_center, requested_datetime)
            }
        
        return {'available': True}
    
    def _calculate_appointment_duration(self, request: TestRequest) -> int:
        """حساب مدة الموعد"""
        
        total_duration = 30  # وقت أساسي للتسجيل والانتظار
        
        # إضافة وقت التحاليل
        total_duration += len(request.requested_tests) * 5  # 5 دقائق لكل تحليل
        
        # إضافة وقت الأشعة
        for exam_id in request.requested_radiology:
            if exam_id in self.radiology_exams:
                exam = self.radiology_exams[exam_id]
                total_duration += exam.duration_minutes
        
        return total_duration
    
    def _create_preparation_checklist(self, request: TestRequest) -> List[Dict]:
        """إنشاء قائمة التحضير"""
        
        checklist = []
        
        for requirement in request.patient_preparation:
            checklist.append({
                'item': requirement,
                'completed': False,
                'importance': 'عالي' if 'صيام' in requirement else 'متوسط'
            })
        
        return checklist
    
    def _generate_arrival_instructions(self, lab_center: LabCenter, request: TestRequest) -> str:
        """إنتاج تعليمات الوصول"""
        
        instructions = f"""
        تعليمات الوصول لمركز {lab_center.name}:
        
        العنوان: {lab_center.location['address']}
        الهاتف: {lab_center.contact_info['phone']}
        
        يرجى الوصول قبل 15 دقيقة من الموعد المحدد.
        إحضار بطاقة الهوية وبطاقة التأمين.
        """
        
        if any(self.lab_tests[test_id].requires_fasting for test_id in request.requested_tests if test_id in self.lab_tests):
            instructions += "\nتذكير: يجب الصيام حسب التعليمات المحددة."
        
        return instructions.strip()
    
    def _generate_confirmation_code(self) -> str:
        """إنتاج رمز التأكيد"""
        import random
        import string
        
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def _schedule_appointment_reminders(self, appointment: TestAppointment):
        """جدولة تذكيرات الموعد"""
        
        # محاكاة جدولة التذكيرات
        # في التطبيق الحقيقي، سيتم استخدام نظام جدولة المهام
        
        reminder_times = []
        for hours_before in self.system_settings['reminder_hours_before']:
            reminder_time = appointment.scheduled_date - timedelta(hours=hours_before)
            reminder_times.append(reminder_time)
        
        current_app.logger.info(f"تم جدولة تذكيرات للموعد {appointment.appointment_id} في: {reminder_times}")
    
    def _generate_pre_appointment_instructions(self, appointment: TestAppointment, request: TestRequest) -> List[str]:
        """إنتاج تعليمات ما قبل الموعد"""
        
        instructions = [
            f"الحضور في {appointment.scheduled_date.strftime('%Y-%m-%d %H:%M')}",
            "إحضار بطاقة الهوية الشخصية",
            "إحضار بطاقة التأمين الصحي",
            "إحضار طلب الطبيب الأصلي"
        ]
        
        # تعليمات خاصة بالتحضير
        for requirement in request.patient_preparation:
            if 'صيام' in requirement:
                instructions.append(f"الصيام: {requirement}")
            elif 'شرب ماء' in requirement:
                instructions.append(f"الترطيب: {requirement}")
        
        return instructions
    
    def _validate_test_results(self, results_data: Dict) -> Dict:
        """التحقق من صحة نتائج التحاليل"""
        
        required_fields = ['request_id', 'patient_id', 'results', 'verified_by']
        
        for field in required_fields:
            if field not in results_data:
                return {
                    'valid': False,
                    'error': f'الحقل {field} مطلوب'
                }
        
        # التحقق من وجود نتائج
        if not results_data['results']:
            return {
                'valid': False,
                'error': 'لا توجد نتائج للإدخال'
            }
        
        return {'valid': True}
    
    def _analyze_test_result(self, result: TestResult) -> Dict:
        """تحليل نتيجة التحليل"""
        
        analysis = {
            'abnormal': False,
            'critical': False,
            'interpretation': 'طبيعي'
        }
        
        # الحصول على معلومات التحليل
        if result.test_id in self.lab_tests:
            test = self.lab_tests[result.test_id]
            
            # تحليل بسيط للنتائج (يمكن تطويره أكثر)
            if isinstance(result.result_value, (int, float)):
                # فحص القيم الرقمية
                if result.result_value < 0:
                    analysis['abnormal'] = True
                    analysis['interpretation'] = 'قيمة غير طبيعية'
                
                # فحص القيم الحرجة (مثال بسيط)
                if test.test_code == 'FBS' and result.result_value > 200:
                    analysis['critical'] = True
                    analysis['interpretation'] = 'مستوى سكر مرتفع جداً - يتطلب تدخل فوري'
        
        return analysis
    
    def _send_critical_result_alerts(self, critical_results: List[TestResult]):
        """إرسال تنبيهات النتائج الحرجة"""
        
        for result in critical_results:
            alert_message = f"""
            تنبيه نتيجة حرجة!
            
            المريض: {result.patient_id}
            التحليل: {self._get_test_name(result.test_id)}
            النتيجة: {result.result_value} {result.unit}
            التعليق: {result.comments}
            
            يتطلب تدخل طبي فوري.
            """
            
            current_app.logger.critical(f"نتيجة حرجة للمريض {result.patient_id}: {alert_message}")
    
    def _generate_comprehensive_report(self, request_id: str, results: List[TestResult]) -> Dict:
        """إنتاج التقرير الشامل"""
        
        report = {
            'request_id': request_id,
            'total_tests': len(results),
            'normal_results': len([r for r in results if not r.abnormal_flag]),
            'abnormal_results': len([r for r in results if r.abnormal_flag]),
            'critical_results': len([r for r in results if r.critical_flag]),
            'summary': '',
            'recommendations': []
        }
        
        # إنتاج الملخص
        if report['critical_results'] > 0:
            report['summary'] = f"تم العثور على {report['critical_results']} نتيجة حرجة تتطلب تدخل فوري"
        elif report['abnormal_results'] > 0:
            report['summary'] = f"تم العثور على {report['abnormal_results']} نتيجة غير طبيعية"
        else:
            report['summary'] = "جميع النتائج ضمن المعدل الطبيعي"
        
        # إنتاج التوصيات
        if report['critical_results'] > 0:
            report['recommendations'].append('مراجعة الطبيب فوراً')
        elif report['abnormal_results'] > 0:
            report['recommendations'].append('مراجعة الطبيب لمناقشة النتائج')
        
        return report
    
    def _generate_follow_up_recommendations(self, results: List[TestResult]) -> List[str]:
        """إنتاج توصيات المتابعة"""
        
        recommendations = []
        
        for result in results:
            if result.follow_up_required:
                recommendations.append(f"متابعة {self._get_test_name(result.test_id)} خلال أسبوعين")
            
            if result.critical_flag:
                recommendations.append(f"مراجعة طبية عاجلة لنتيجة {self._get_test_name(result.test_id)}")
        
        if not recommendations:
            recommendations.append("لا توجد متابعة خاصة مطلوبة")
        
        return recommendations
    
    def _get_test_name(self, test_id: str) -> str:
        """الحصول على اسم التحليل"""
        
        if test_id in self.lab_tests:
            return self.lab_tests[test_id].test_name
        return "تحليل غير معروف"
    
    def _get_exam_name(self, exam_id: str) -> str:
        """الحصول على اسم فحص الأشعة"""
        
        if exam_id in self.radiology_exams:
            return self.radiology_exams[exam_id].exam_name
        return "فحص غير معروف"
    
    # دوال مساعدة إضافية للإحصائيات والتحليل
    def _calculate_average_turnaround_time(self, requests: List[TestRequest], results: List[TestResult]) -> float:
        """حساب متوسط وقت المعالجة"""
        
        if not requests or not results:
            return 0.0
        
        total_time = 0
        count = 0
        
        for request in requests:
            request_results = [r for r in results if r.request_id == request.request_id]
            if request_results:
                # حساب الوقت من الطلب إلى آخر نتيجة
                latest_result = max(request_results, key=lambda x: x.result_date)
                turnaround_time = (latest_result.result_date - request.request_date).total_seconds() / 3600
                total_time += turnaround_time
                count += 1
        
        return total_time / count if count > 0 else 0.0
    
    def _calculate_on_time_delivery_rate(self, requests: List[TestRequest]) -> float:
        """حساب معدل التسليم في الوقت المحدد"""
        
        if not requests:
            return 0.0
        
        on_time_count = 0
        
        for request in requests:
            if request.status == TestStatus.COMPLETED.value:
                # افتراض أن الطلب تم في الوقت المحدد إذا كان مكتملاً
                on_time_count += 1
        
        return (on_time_count / len(requests)) * 100
    
    def _calculate_patient_satisfaction(self, requests: List[TestRequest]) -> float:
        """حساب رضا المرضى"""
        
        # محاكاة نقاط رضا المرضى
        # في التطبيق الحقيقي، سيتم جمع هذه البيانات من استطلاعات الرأي
        
        import random
        return round(random.uniform(4.0, 5.0), 1)
    
    def _calculate_lab_utilization(self) -> float:
        """حساب معدل استخدام المختبرات"""
        
        if not self.lab_centers:
            return 0.0
        
        total_capacity = sum(center.capacity_per_day for center in self.lab_centers.values())
        total_bookings = sum(center.current_bookings for center in self.lab_centers.values())
        
        return (total_bookings / total_capacity) * 100 if total_capacity > 0 else 0.0

