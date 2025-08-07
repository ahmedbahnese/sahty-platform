"""
خدمة الامتثال للمعايير الطبية والقانونية
نظام شامل لضمان الامتثال للمعايير الطبية والقانونية المحلية والدولية
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class ComplianceStandard(Enum):
    HIPAA = "HIPAA"  # قانون نقل التأمين الصحي والمساءلة الأمريكي
    GDPR = "GDPR"   # اللائحة العامة لحماية البيانات الأوروبية
    EGYPTIAN_HEALTH_LAW = "قانون الصحة المصري"
    ISO_27001 = "ISO 27001"  # معيار أمن المعلومات
    ISO_13485 = "ISO 13485"  # معيار الأجهزة الطبية
    HL7_FHIR = "HL7 FHIR"   # معيار تبادل البيانات الصحية
    EGYPTIAN_DATA_PROTECTION = "قانون حماية البيانات المصري"
    MEDICAL_DEVICE_REGULATION = "لائحة الأجهزة الطبية"

class ComplianceCategory(Enum):
    DATA_PRIVACY = "خصوصية البيانات"
    MEDICAL_RECORDS = "السجلات الطبية"
    PATIENT_CONSENT = "موافقة المريض"
    DATA_SECURITY = "أمان البيانات"
    AUDIT_TRAIL = "سجل المراجعة"
    ACCESS_CONTROL = "التحكم في الوصول"
    DATA_RETENTION = "الاحتفاظ بالبيانات"
    CROSS_BORDER_TRANSFER = "النقل عبر الحدود"
    MEDICAL_PRACTICE = "الممارسة الطبية"
    PHARMACEUTICAL = "الصيدلة"

class ComplianceStatus(Enum):
    COMPLIANT = "متوافق"
    NON_COMPLIANT = "غير متوافق"
    PARTIALLY_COMPLIANT = "متوافق جزئياً"
    UNDER_REVIEW = "قيد المراجعة"
    PENDING_ACTION = "في انتظار إجراء"

@dataclass
class ComplianceRule:
    rule_id: str
    standard: str
    category: str
    title: str
    description: str
    requirements: List[str]
    implementation_guide: str
    severity: str  # critical, high, medium, low
    applicable_entities: List[str]  # patient, doctor, hospital, etc.
    verification_method: str
    documentation_required: List[str]
    penalties: Dict
    last_updated: datetime

@dataclass
class ComplianceAssessment:
    assessment_id: str
    entity_id: str
    entity_type: str
    standard: str
    assessed_rules: List[str]
    results: Dict[str, str]  # rule_id: status
    overall_score: float
    compliance_percentage: float
    critical_issues: List[str]
    recommendations: List[str]
    assessor_id: str
    assessment_date: datetime
    next_assessment_date: datetime
    evidence_files: List[str]

@dataclass
class ComplianceIncident:
    incident_id: str
    entity_id: str
    rule_id: str
    incident_type: str
    severity: str
    description: str
    detected_date: datetime
    reported_date: datetime
    status: str
    assigned_to: str
    resolution_steps: List[str]
    resolution_date: Optional[datetime]
    impact_assessment: Dict
    lessons_learned: str

@dataclass
class ConsentRecord:
    consent_id: str
    patient_id: str
    consent_type: str
    purpose: str
    data_categories: List[str]
    granted_date: datetime
    expiry_date: Optional[datetime]
    withdrawal_date: Optional[datetime]
    consent_method: str  # digital, written, verbal
    witness_id: Optional[str]
    legal_basis: str
    is_active: bool

class ComplianceService:
    def __init__(self):
        """تهيئة خدمة الامتثال"""
        
        # إعدادات النظام
        self.system_settings = {
            'assessment_frequency_days': 90,  # تقييم كل 3 أشهر
            'incident_response_hours': 24,   # الاستجابة خلال 24 ساعة
            'data_retention_years': 7,       # الاحتفاظ بالبيانات 7 سنوات
            'consent_renewal_days': 365,     # تجديد الموافقة سنوياً
            'audit_log_retention_years': 10, # الاحتفاظ بسجلات المراجعة 10 سنوات
            'encryption_standard': 'AES-256',
            'backup_frequency_hours': 6,     # نسخ احتياطية كل 6 ساعات
            'access_review_frequency_days': 30  # مراجعة الصلاحيات شهرياً
        }
        
        # قواعد الامتثال
        self.compliance_rules = {}
        self.assessments = {}
        self.incidents = {}
        self.consent_records = {}
        self.audit_logs = {}
        
        # إحصائيات الامتثال
        self.compliance_stats = {
            'overall_compliance_score': 0.0,
            'total_assessments': 0,
            'active_incidents': 0,
            'resolved_incidents': 0,
            'consent_compliance_rate': 0.0,
            'last_full_assessment': None
        }
        
        # تهيئة القواعد الافتراضية
        self._initialize_compliance_rules()
    
    def conduct_compliance_assessment(self, entity_id: str, entity_type: str, standards: List[str] = None) -> Dict:
        """
        إجراء تقييم امتثال شامل
        
        Args:
            entity_id: معرف الكيان
            entity_type: نوع الكيان
            standards: المعايير المطلوب تقييمها
            
        Returns:
            Dict: نتائج التقييم
        """
        try:
            # تحديد المعايير إذا لم تُحدد
            if not standards:
                standards = self._get_applicable_standards(entity_type)
            
            # جمع القواعد المطبقة
            applicable_rules = []
            for standard in standards:
                rules = self._get_rules_by_standard(standard, entity_type)
                applicable_rules.extend(rules)
            
            # إجراء التقييم
            assessment_results = {}
            critical_issues = []
            recommendations = []
            
            for rule in applicable_rules:
                result = self._assess_rule_compliance(entity_id, rule)
                assessment_results[rule.rule_id] = result['status']
                
                if result['status'] == ComplianceStatus.NON_COMPLIANT.value and rule.severity == 'critical':
                    critical_issues.append({
                        'rule_id': rule.rule_id,
                        'title': rule.title,
                        'description': rule.description,
                        'requirements': rule.requirements
                    })
                
                if result.get('recommendations'):
                    recommendations.extend(result['recommendations'])
            
            # حساب النقاط
            total_rules = len(applicable_rules)
            compliant_rules = len([r for r in assessment_results.values() if r == ComplianceStatus.COMPLIANT.value])
            partially_compliant = len([r for r in assessment_results.values() if r == ComplianceStatus.PARTIALLY_COMPLIANT.value])
            
            overall_score = (compliant_rules + (partially_compliant * 0.5)) / total_rules if total_rules > 0 else 0
            compliance_percentage = overall_score * 100
            
            # إنشاء التقييم
            assessment = ComplianceAssessment(
                assessment_id=str(uuid.uuid4()),
                entity_id=entity_id,
                entity_type=entity_type,
                standard=', '.join(standards),
                assessed_rules=[rule.rule_id for rule in applicable_rules],
                results=assessment_results,
                overall_score=round(overall_score, 3),
                compliance_percentage=round(compliance_percentage, 2),
                critical_issues=[issue['rule_id'] for issue in critical_issues],
                recommendations=list(set(recommendations)),
                assessor_id='system',
                assessment_date=datetime.now(),
                next_assessment_date=datetime.now() + timedelta(days=self.system_settings['assessment_frequency_days']),
                evidence_files=[]
            )
            
            # حفظ التقييم
            self.assessments[assessment.assessment_id] = assessment
            
            # إنشاء حوادث للمشاكل الحرجة
            for issue in critical_issues:
                self._create_compliance_incident(entity_id, issue['rule_id'], 'non_compliance', 'critical')
            
            # تحديث الإحصائيات
            self._update_compliance_statistics()
            
            return {
                'success': True,
                'assessment': self._assessment_to_dict(assessment),
                'critical_issues': critical_issues,
                'recommendations': recommendations,
                'next_steps': self._generate_next_steps(assessment)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تقييم الامتثال: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تقييم الامتثال'
            }
    
    def record_patient_consent(self, patient_id: str, consent_data: Dict) -> Dict:
        """
        تسجيل موافقة المريض
        
        Args:
            patient_id: معرف المريض
            consent_data: بيانات الموافقة
            
        Returns:
            Dict: نتيجة التسجيل
        """
        try:
            # التحقق من صحة البيانات
            validation_result = self._validate_consent_data(consent_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # إنشاء سجل الموافقة
            consent = ConsentRecord(
                consent_id=str(uuid.uuid4()),
                patient_id=patient_id,
                consent_type=consent_data['consent_type'],
                purpose=consent_data['purpose'],
                data_categories=consent_data['data_categories'],
                granted_date=datetime.now(),
                expiry_date=datetime.now() + timedelta(days=self.system_settings['consent_renewal_days']) if consent_data.get('has_expiry', True) else None,
                withdrawal_date=None,
                consent_method=consent_data.get('consent_method', 'digital'),
                witness_id=consent_data.get('witness_id'),
                legal_basis=consent_data.get('legal_basis', 'explicit_consent'),
                is_active=True
            )
            
            # حفظ الموافقة
            self.consent_records[consent.consent_id] = consent
            
            # تسجيل في سجل المراجعة
            self._log_audit_event('consent_granted', {
                'patient_id': patient_id,
                'consent_id': consent.consent_id,
                'consent_type': consent.consent_type,
                'granted_by': consent_data.get('granted_by', 'patient')
            })
            
            return {
                'success': True,
                'consent_id': consent.consent_id,
                'message': 'تم تسجيل الموافقة بنجاح',
                'expiry_date': consent.expiry_date.isoformat() if consent.expiry_date else None
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تسجيل الموافقة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تسجيل الموافقة'
            }
    
    def withdraw_consent(self, patient_id: str, consent_id: str, reason: str = None) -> Dict:
        """
        سحب موافقة المريض
        
        Args:
            patient_id: معرف المريض
            consent_id: معرف الموافقة
            reason: سبب السحب
            
        Returns:
            Dict: نتيجة السحب
        """
        try:
            if consent_id not in self.consent_records:
                return {
                    'success': False,
                    'error': 'الموافقة غير موجودة'
                }
            
            consent = self.consent_records[consent_id]
            
            # التحقق من الصلاحية
            if consent.patient_id != patient_id:
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية لسحب هذه الموافقة'
                }
            
            if not consent.is_active:
                return {
                    'success': False,
                    'error': 'الموافقة مسحوبة مسبقاً'
                }
            
            # سحب الموافقة
            consent.is_active = False
            consent.withdrawal_date = datetime.now()
            
            # تسجيل في سجل المراجعة
            self._log_audit_event('consent_withdrawn', {
                'patient_id': patient_id,
                'consent_id': consent_id,
                'reason': reason,
                'withdrawal_date': consent.withdrawal_date.isoformat()
            })
            
            # تنفيذ إجراءات السحب
            self._execute_consent_withdrawal_actions(consent)
            
            return {
                'success': True,
                'message': 'تم سحب الموافقة بنجاح',
                'withdrawal_date': consent.withdrawal_date.isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في سحب الموافقة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في سحب الموافقة'
            }
    
    def check_data_access_permission(self, user_id: str, patient_id: str, data_type: str, purpose: str) -> Dict:
        """
        التحقق من صلاحية الوصول للبيانات
        
        Args:
            user_id: معرف المستخدم
            patient_id: معرف المريض
            data_type: نوع البيانات
            purpose: الغرض من الوصول
            
        Returns:
            Dict: نتيجة التحقق
        """
        try:
            # البحث عن موافقات نشطة
            active_consents = [
                consent for consent in self.consent_records.values()
                if (consent.patient_id == patient_id and 
                    consent.is_active and
                    data_type in consent.data_categories and
                    (not consent.expiry_date or consent.expiry_date > datetime.now()))
            ]
            
            # التحقق من وجود موافقة مناسبة
            valid_consent = None
            for consent in active_consents:
                if self._is_purpose_compatible(consent.purpose, purpose):
                    valid_consent = consent
                    break
            
            if not valid_consent:
                # تسجيل محاولة وصول غير مصرح بها
                self._log_audit_event('unauthorized_access_attempt', {
                    'user_id': user_id,
                    'patient_id': patient_id,
                    'data_type': data_type,
                    'purpose': purpose,
                    'reason': 'no_valid_consent'
                })
                
                return {
                    'success': False,
                    'access_granted': False,
                    'reason': 'لا توجد موافقة صالحة للوصول لهذه البيانات',
                    'required_consent_type': self._get_required_consent_type(data_type, purpose)
                }
            
            # تسجيل الوصول المصرح به
            self._log_audit_event('data_access_granted', {
                'user_id': user_id,
                'patient_id': patient_id,
                'data_type': data_type,
                'purpose': purpose,
                'consent_id': valid_consent.consent_id
            })
            
            return {
                'success': True,
                'access_granted': True,
                'consent_id': valid_consent.consent_id,
                'access_conditions': self._get_access_conditions(valid_consent),
                'expiry_date': valid_consent.expiry_date.isoformat() if valid_consent.expiry_date else None
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في التحقق من صلاحية الوصول: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في التحقق من صلاحية الوصول'
            }
    
    def generate_compliance_report(self, entity_id: str = None, standards: List[str] = None, period_days: int = 30) -> Dict:
        """
        إنتاج تقرير امتثال شامل
        
        Args:
            entity_id: معرف الكيان (اختياري)
            standards: المعايير المطلوبة (اختياري)
            period_days: فترة التقرير بالأيام
            
        Returns:
            Dict: التقرير الشامل
        """
        try:
            # تحديد فترة التقرير
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # جمع البيانات
            assessments = self._get_assessments_in_period(entity_id, start_date, end_date)
            incidents = self._get_incidents_in_period(entity_id, start_date, end_date)
            consent_records = self._get_consent_records_in_period(entity_id, start_date, end_date)
            
            # تحليل الامتثال
            compliance_analysis = self._analyze_compliance_trends(assessments)
            incident_analysis = self._analyze_incident_trends(incidents)
            consent_analysis = self._analyze_consent_compliance(consent_records)
            
            # إنتاج التوصيات
            recommendations = self._generate_compliance_recommendations(
                compliance_analysis, incident_analysis, consent_analysis
            )
            
            # إنشاء التقرير
            report = {
                'report_id': str(uuid.uuid4()),
                'generated_date': datetime.now().isoformat(),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': period_days
                },
                'scope': {
                    'entity_id': entity_id,
                    'standards': standards,
                    'assessments_count': len(assessments),
                    'incidents_count': len(incidents),
                    'consent_records_count': len(consent_records)
                },
                'executive_summary': {
                    'overall_compliance_score': compliance_analysis.get('overall_score', 0),
                    'compliance_trend': compliance_analysis.get('trend', 'stable'),
                    'critical_incidents': len([i for i in incidents if i.severity == 'critical']),
                    'consent_compliance_rate': consent_analysis.get('compliance_rate', 0),
                    'key_achievements': self._identify_key_achievements(assessments, incidents),
                    'major_concerns': self._identify_major_concerns(assessments, incidents)
                },
                'detailed_analysis': {
                    'compliance_by_standard': self._analyze_compliance_by_standard(assessments),
                    'incident_breakdown': incident_analysis,
                    'consent_management': consent_analysis,
                    'audit_trail_summary': self._summarize_audit_trail(start_date, end_date)
                },
                'recommendations': recommendations,
                'action_plan': self._create_action_plan(recommendations),
                'next_review_date': (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            return {
                'success': True,
                'report': report,
                'export_formats': ['pdf', 'excel', 'json'],
                'sharing_options': ['email', 'download', 'dashboard']
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنتاج تقرير الامتثال: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنتاج تقرير الامتثال'
            }
    
    def monitor_compliance_violations(self) -> Dict:
        """
        مراقبة انتهاكات الامتثال في الوقت الفعلي
        
        Returns:
            Dict: نتائج المراقبة
        """
        try:
            violations = []
            
            # فحص انتهاء صلاحية الموافقات
            expired_consents = self._check_expired_consents()
            for consent in expired_consents:
                violations.append({
                    'type': 'expired_consent',
                    'severity': 'high',
                    'entity_id': consent.patient_id,
                    'description': f'انتهت صلاحية الموافقة {consent.consent_id}',
                    'action_required': 'تجديد الموافقة أو إيقاف معالجة البيانات'
                })
            
            # فحص الوصول غير المصرح به
            unauthorized_access = self._check_unauthorized_access()
            for access in unauthorized_access:
                violations.append({
                    'type': 'unauthorized_access',
                    'severity': 'critical',
                    'entity_id': access['user_id'],
                    'description': f'محاولة وصول غير مصرح بها للبيانات',
                    'action_required': 'مراجعة فورية وإجراءات تأديبية'
                })
            
            # فحص انتهاكات الاحتفاظ بالبيانات
            retention_violations = self._check_data_retention_violations()
            for violation in retention_violations:
                violations.append({
                    'type': 'data_retention_violation',
                    'severity': 'medium',
                    'entity_id': violation['entity_id'],
                    'description': f'بيانات محتفظ بها أطول من المدة المسموحة',
                    'action_required': 'حذف أو أرشفة البيانات'
                })
            
            # فحص انتهاكات التشفير
            encryption_violations = self._check_encryption_violations()
            for violation in encryption_violations:
                violations.append({
                    'type': 'encryption_violation',
                    'severity': 'critical',
                    'entity_id': violation['entity_id'],
                    'description': f'بيانات حساسة غير مشفرة',
                    'action_required': 'تشفير فوري للبيانات'
                })
            
            # ترتيب حسب الخطورة
            violations.sort(key=lambda x: {'critical': 3, 'high': 2, 'medium': 1, 'low': 0}[x['severity']], reverse=True)
            
            # إنشاء حوادث للانتهاكات الحرجة
            for violation in violations:
                if violation['severity'] in ['critical', 'high']:
                    self._create_compliance_incident(
                        violation['entity_id'],
                        'monitoring_rule',
                        violation['type'],
                        violation['severity']
                    )
            
            return {
                'success': True,
                'violations': violations,
                'total_violations': len(violations),
                'critical_violations': len([v for v in violations if v['severity'] == 'critical']),
                'monitoring_timestamp': datetime.now().isoformat(),
                'next_monitoring': (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في مراقبة الامتثال: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في مراقبة الامتثال'
            }
    
    # الدوال المساعدة
    def _initialize_compliance_rules(self):
        """تهيئة قواعد الامتثال الافتراضية"""
        
        # قواعد GDPR
        gdpr_rules = [
            {
                'standard': ComplianceStandard.GDPR.value,
                'category': ComplianceCategory.DATA_PRIVACY.value,
                'title': 'الحصول على موافقة صريحة',
                'description': 'يجب الحصول على موافقة صريحة من المريض قبل معالجة بياناته الشخصية',
                'requirements': [
                    'الموافقة يجب أن تكون محددة وواضحة',
                    'يجب إعلام المريض بالغرض من معالجة البيانات',
                    'يجب أن تكون الموافقة قابلة للسحب في أي وقت'
                ],
                'severity': 'critical'
            },
            {
                'standard': ComplianceStandard.GDPR.value,
                'category': ComplianceCategory.DATA_SECURITY.value,
                'title': 'تشفير البيانات الحساسة',
                'description': 'يجب تشفير جميع البيانات الصحية الحساسة',
                'requirements': [
                    'استخدام تشفير AES-256 أو أقوى',
                    'تشفير البيانات أثناء النقل والتخزين',
                    'إدارة آمنة لمفاتيح التشفير'
                ],
                'severity': 'critical'
            }
        ]
        
        # قواعد القانون المصري
        egyptian_rules = [
            {
                'standard': ComplianceStandard.EGYPTIAN_HEALTH_LAW.value,
                'category': ComplianceCategory.MEDICAL_RECORDS.value,
                'title': 'الاحتفاظ بالسجلات الطبية',
                'description': 'يجب الاحتفاظ بالسجلات الطبية لمدة لا تقل عن 7 سنوات',
                'requirements': [
                    'حفظ السجلات في مكان آمن',
                    'ضمان سهولة الوصول للسجلات عند الحاجة',
                    'حماية السجلات من التلف أو الفقدان'
                ],
                'severity': 'high'
            }
        ]
        
        # إنشاء قواعد الامتثال
        all_rules = gdpr_rules + egyptian_rules
        
        for rule_data in all_rules:
            rule = ComplianceRule(
                rule_id=str(uuid.uuid4()),
                standard=rule_data['standard'],
                category=rule_data['category'],
                title=rule_data['title'],
                description=rule_data['description'],
                requirements=rule_data['requirements'],
                implementation_guide=f"دليل تطبيق {rule_data['title']}",
                severity=rule_data['severity'],
                applicable_entities=['patient', 'doctor', 'hospital'],
                verification_method='automated_check',
                documentation_required=['policy_document', 'implementation_evidence'],
                penalties={'fine': '10000-50000 EUR', 'suspension': 'possible'},
                last_updated=datetime.now()
            )
            
            self.compliance_rules[rule.rule_id] = rule
    
    def _get_applicable_standards(self, entity_type: str) -> List[str]:
        """الحصول على المعايير المطبقة على نوع الكيان"""
        
        base_standards = [
            ComplianceStandard.GDPR.value,
            ComplianceStandard.EGYPTIAN_HEALTH_LAW.value,
            ComplianceStandard.EGYPTIAN_DATA_PROTECTION.value
        ]
        
        if entity_type in ['doctor', 'hospital']:
            base_standards.extend([
                ComplianceStandard.ISO_27001.value,
                ComplianceStandard.HL7_FHIR.value
            ])
        
        if entity_type == 'hospital':
            base_standards.append(ComplianceStandard.ISO_13485.value)
        
        return base_standards
    
    def _get_rules_by_standard(self, standard: str, entity_type: str) -> List[ComplianceRule]:
        """الحصول على القواعد حسب المعيار ونوع الكيان"""
        
        return [
            rule for rule in self.compliance_rules.values()
            if rule.standard == standard and entity_type in rule.applicable_entities
        ]
    
    def _assess_rule_compliance(self, entity_id: str, rule: ComplianceRule) -> Dict:
        """تقييم امتثال قاعدة محددة"""
        
        # محاكاة تقييم القاعدة
        # في التطبيق الحقيقي، سيتم فحص البيانات الفعلية
        
        if rule.category == ComplianceCategory.DATA_PRIVACY.value:
            # فحص وجود موافقات نشطة
            active_consents = [c for c in self.consent_records.values() if c.patient_id == entity_id and c.is_active]
            if active_consents:
                status = ComplianceStatus.COMPLIANT.value
                recommendations = []
            else:
                status = ComplianceStatus.NON_COMPLIANT.value
                recommendations = ['الحصول على موافقة صريحة من المريض']
        
        elif rule.category == ComplianceCategory.DATA_SECURITY.value:
            # فحص التشفير (محاكاة)
            status = ComplianceStatus.COMPLIANT.value  # افتراض وجود تشفير
            recommendations = []
        
        else:
            # تقييم افتراضي
            status = ComplianceStatus.PARTIALLY_COMPLIANT.value
            recommendations = ['مراجعة تطبيق القاعدة']
        
        return {
            'status': status,
            'recommendations': recommendations,
            'evidence': [],
            'assessment_date': datetime.now().isoformat()
        }
    
    def _validate_consent_data(self, consent_data: Dict) -> Dict:
        """التحقق من صحة بيانات الموافقة"""
        
        required_fields = ['consent_type', 'purpose', 'data_categories']
        
        for field in required_fields:
            if field not in consent_data:
                return {
                    'valid': False,
                    'error': f'الحقل {field} مطلوب'
                }
        
        # التحقق من صحة فئات البيانات
        valid_categories = ['medical_records', 'personal_info', 'contact_info', 'payment_info']
        for category in consent_data['data_categories']:
            if category not in valid_categories:
                return {
                    'valid': False,
                    'error': f'فئة البيانات {category} غير صالحة'
                }
        
        return {'valid': True}
    
    def _log_audit_event(self, event_type: str, event_data: Dict):
        """تسجيل حدث في سجل المراجعة"""
        
        audit_entry = {
            'event_id': str(uuid.uuid4()),
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': event_data,
            'ip_address': event_data.get('ip_address', 'unknown'),
            'user_agent': event_data.get('user_agent', 'unknown')
        }
        
        # حفظ في سجل المراجعة
        date_key = datetime.now().strftime('%Y-%m-%d')
        if date_key not in self.audit_logs:
            self.audit_logs[date_key] = []
        
        self.audit_logs[date_key].append(audit_entry)
    
    def _execute_consent_withdrawal_actions(self, consent: ConsentRecord):
        """تنفيذ إجراءات سحب الموافقة"""
        
        # في التطبيق الحقيقي، سيتم تنفيذ إجراءات فعلية
        # مثل إيقاف معالجة البيانات، حذف البيانات، إلخ
        
        actions = [
            'إيقاف معالجة البيانات المرتبطة بالموافقة',
            'إشعار جميع الأطراف المعنية',
            'تحديث أنظمة إدارة البيانات',
            'توثيق عملية السحب'
        ]
        
        for action in actions:
            self._log_audit_event('consent_withdrawal_action', {
                'consent_id': consent.consent_id,
                'action': action,
                'executed_at': datetime.now().isoformat()
            })
    
    def _is_purpose_compatible(self, consent_purpose: str, requested_purpose: str) -> bool:
        """التحقق من توافق الغرض مع الموافقة"""
        
        # قواعد توافق الأغراض
        purpose_compatibility = {
            'medical_treatment': ['diagnosis', 'treatment', 'follow_up'],
            'research': ['clinical_research', 'medical_research'],
            'administrative': ['billing', 'scheduling', 'communication']
        }
        
        for main_purpose, compatible_purposes in purpose_compatibility.items():
            if consent_purpose == main_purpose and requested_purpose in compatible_purposes:
                return True
        
        return consent_purpose == requested_purpose
    
    def _get_required_consent_type(self, data_type: str, purpose: str) -> str:
        """تحديد نوع الموافقة المطلوبة"""
        
        if data_type in ['medical_records', 'genetic_data']:
            return 'explicit_consent'
        elif purpose == 'research':
            return 'research_consent'
        else:
            return 'general_consent'
    
    def _get_access_conditions(self, consent: ConsentRecord) -> List[str]:
        """الحصول على شروط الوصول"""
        
        conditions = [
            'الوصول للغرض المحدد فقط',
            'عدم مشاركة البيانات مع أطراف ثالثة',
            'الالتزام بمعايير الأمان'
        ]
        
        if consent.expiry_date:
            conditions.append(f'الوصول صالح حتى {consent.expiry_date.strftime("%Y-%m-%d")}')
        
        return conditions
    
    def _create_compliance_incident(self, entity_id: str, rule_id: str, incident_type: str, severity: str):
        """إنشاء حادث امتثال"""
        
        incident = ComplianceIncident(
            incident_id=str(uuid.uuid4()),
            entity_id=entity_id,
            rule_id=rule_id,
            incident_type=incident_type,
            severity=severity,
            description=f'انتهاك امتثال من نوع {incident_type}',
            detected_date=datetime.now(),
            reported_date=datetime.now(),
            status='open',
            assigned_to='compliance_team',
            resolution_steps=[],
            resolution_date=None,
            impact_assessment={},
            lessons_learned=''
        )
        
        self.incidents[incident.incident_id] = incident
    
    def _update_compliance_statistics(self):
        """تحديث إحصائيات الامتثال"""
        
        # حساب النقاط الإجمالية
        if self.assessments:
            total_score = sum(assessment.overall_score for assessment in self.assessments.values())
            self.compliance_stats['overall_compliance_score'] = total_score / len(self.assessments)
        
        # عدد التقييمات
        self.compliance_stats['total_assessments'] = len(self.assessments)
        
        # الحوادث النشطة والمحلولة
        active_incidents = [i for i in self.incidents.values() if i.status == 'open']
        resolved_incidents = [i for i in self.incidents.values() if i.status == 'resolved']
        
        self.compliance_stats['active_incidents'] = len(active_incidents)
        self.compliance_stats['resolved_incidents'] = len(resolved_incidents)
        
        # معدل امتثال الموافقات
        total_consents = len(self.consent_records)
        active_consents = len([c for c in self.consent_records.values() if c.is_active])
        
        if total_consents > 0:
            self.compliance_stats['consent_compliance_rate'] = (active_consents / total_consents) * 100
    
    def _assessment_to_dict(self, assessment: ComplianceAssessment) -> Dict:
        """تحويل التقييم إلى قاموس"""
        
        return {
            'assessment_id': assessment.assessment_id,
            'entity_id': assessment.entity_id,
            'entity_type': assessment.entity_type,
            'standard': assessment.standard,
            'overall_score': assessment.overall_score,
            'compliance_percentage': assessment.compliance_percentage,
            'critical_issues_count': len(assessment.critical_issues),
            'recommendations_count': len(assessment.recommendations),
            'assessment_date': assessment.assessment_date.isoformat(),
            'next_assessment_date': assessment.next_assessment_date.isoformat(),
            'status': 'completed'
        }
    
    def _generate_next_steps(self, assessment: ComplianceAssessment) -> List[str]:
        """إنتاج الخطوات التالية"""
        
        next_steps = []
        
        if assessment.critical_issues:
            next_steps.append('معالجة المشاكل الحرجة فوراً')
        
        if assessment.compliance_percentage < 80:
            next_steps.append('وضع خطة تحسين شاملة')
        
        next_steps.extend([
            'مراجعة التوصيات وتطبيقها',
            'جدولة التقييم التالي',
            'تدريب الفريق على المتطلبات'
        ])
        
        return next_steps
    
    # دوال التحليل والمراقبة
    def _check_expired_consents(self) -> List[ConsentRecord]:
        """فحص الموافقات منتهية الصلاحية"""
        
        now = datetime.now()
        return [
            consent for consent in self.consent_records.values()
            if (consent.is_active and 
                consent.expiry_date and 
                consent.expiry_date <= now)
        ]
    
    def _check_unauthorized_access(self) -> List[Dict]:
        """فحص محاولات الوصول غير المصرح بها"""
        
        # فحص سجل المراجعة للعثور على محاولات وصول مشبوهة
        unauthorized_attempts = []
        
        for date_logs in self.audit_logs.values():
            for log_entry in date_logs:
                if log_entry['event_type'] == 'unauthorized_access_attempt':
                    unauthorized_attempts.append(log_entry['data'])
        
        return unauthorized_attempts
    
    def _check_data_retention_violations(self) -> List[Dict]:
        """فحص انتهاكات الاحتفاظ بالبيانات"""
        
        # في التطبيق الحقيقي، سيتم فحص قاعدة البيانات
        # للعثور على بيانات محتفظ بها أطول من المدة المسموحة
        
        violations = []
        retention_limit = datetime.now() - timedelta(days=self.system_settings['data_retention_years'] * 365)
        
        # محاكاة فحص البيانات القديمة
        for consent in self.consent_records.values():
            if consent.granted_date < retention_limit and consent.is_active:
                violations.append({
                    'entity_id': consent.patient_id,
                    'data_type': 'consent_record',
                    'retention_date': consent.granted_date.isoformat(),
                    'violation_type': 'exceeded_retention_period'
                })
        
        return violations
    
    def _check_encryption_violations(self) -> List[Dict]:
        """فحص انتهاكات التشفير"""
        
        # في التطبيق الحقيقي، سيتم فحص قاعدة البيانات
        # للعثور على بيانات حساسة غير مشفرة
        
        violations = []
        
        # محاكاة فحص التشفير
        # هنا نفترض أن جميع البيانات مشفرة
        
        return violations
    
    # دوال التحليل للتقارير
    def _get_assessments_in_period(self, entity_id: str, start_date: datetime, end_date: datetime) -> List[ComplianceAssessment]:
        """الحصول على التقييمات في فترة محددة"""
        
        assessments = []
        for assessment in self.assessments.values():
            if (start_date <= assessment.assessment_date <= end_date and
                (not entity_id or assessment.entity_id == entity_id)):
                assessments.append(assessment)
        
        return assessments
    
    def _get_incidents_in_period(self, entity_id: str, start_date: datetime, end_date: datetime) -> List[ComplianceIncident]:
        """الحصول على الحوادث في فترة محددة"""
        
        incidents = []
        for incident in self.incidents.values():
            if (start_date <= incident.detected_date <= end_date and
                (not entity_id or incident.entity_id == entity_id)):
                incidents.append(incident)
        
        return incidents
    
    def _get_consent_records_in_period(self, entity_id: str, start_date: datetime, end_date: datetime) -> List[ConsentRecord]:
        """الحصول على سجلات الموافقة في فترة محددة"""
        
        consents = []
        for consent in self.consent_records.values():
            if (start_date <= consent.granted_date <= end_date and
                (not entity_id or consent.patient_id == entity_id)):
                consents.append(consent)
        
        return consents
    
    def _analyze_compliance_trends(self, assessments: List[ComplianceAssessment]) -> Dict:
        """تحليل اتجاهات الامتثال"""
        
        if not assessments:
            return {'overall_score': 0, 'trend': 'no_data'}
        
        # حساب النقاط الإجمالية
        scores = [assessment.overall_score for assessment in assessments]
        overall_score = sum(scores) / len(scores)
        
        # تحديد الاتجاه
        if len(scores) >= 2:
            recent_scores = scores[-3:]  # آخر 3 تقييمات
            older_scores = scores[:-3] if len(scores) > 3 else scores[:1]
            
            if recent_scores and older_scores:
                recent_avg = sum(recent_scores) / len(recent_scores)
                older_avg = sum(older_scores) / len(older_scores)
                
                if recent_avg > older_avg + 0.1:
                    trend = 'improving'
                elif recent_avg < older_avg - 0.1:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
        else:
            trend = 'insufficient_data'
        
        return {
            'overall_score': round(overall_score, 3),
            'trend': trend,
            'total_assessments': len(assessments),
            'average_compliance_percentage': round(sum(a.compliance_percentage for a in assessments) / len(assessments), 2)
        }
    
    def _analyze_incident_trends(self, incidents: List[ComplianceIncident]) -> Dict:
        """تحليل اتجاهات الحوادث"""
        
        if not incidents:
            return {'total_incidents': 0, 'severity_breakdown': {}}
        
        # تحليل الخطورة
        severity_counts = {}
        for incident in incidents:
            severity_counts[incident.severity] = severity_counts.get(incident.severity, 0) + 1
        
        # تحليل الأنواع
        type_counts = {}
        for incident in incidents:
            type_counts[incident.incident_type] = type_counts.get(incident.incident_type, 0) + 1
        
        # حساب معدل الحل
        resolved_incidents = [i for i in incidents if i.status == 'resolved']
        resolution_rate = (len(resolved_incidents) / len(incidents)) * 100 if incidents else 0
        
        return {
            'total_incidents': len(incidents),
            'severity_breakdown': severity_counts,
            'type_breakdown': type_counts,
            'resolution_rate': round(resolution_rate, 2),
            'average_resolution_time': self._calculate_average_resolution_time(resolved_incidents)
        }
    
    def _analyze_consent_compliance(self, consent_records: List[ConsentRecord]) -> Dict:
        """تحليل امتثال الموافقات"""
        
        if not consent_records:
            return {'compliance_rate': 0, 'total_consents': 0}
        
        # حساب الموافقات النشطة
        active_consents = [c for c in consent_records if c.is_active]
        compliance_rate = (len(active_consents) / len(consent_records)) * 100
        
        # تحليل أنواع الموافقة
        consent_types = {}
        for consent in consent_records:
            consent_types[consent.consent_type] = consent_types.get(consent.consent_type, 0) + 1
        
        # حساب الموافقات منتهية الصلاحية
        now = datetime.now()
        expired_consents = [
            c for c in consent_records 
            if c.expiry_date and c.expiry_date <= now and c.is_active
        ]
        
        return {
            'compliance_rate': round(compliance_rate, 2),
            'total_consents': len(consent_records),
            'active_consents': len(active_consents),
            'expired_consents': len(expired_consents),
            'consent_type_breakdown': consent_types
        }
    
    def _calculate_average_resolution_time(self, resolved_incidents: List[ComplianceIncident]) -> float:
        """حساب متوسط وقت حل الحوادث"""
        
        if not resolved_incidents:
            return 0.0
        
        total_time = 0
        for incident in resolved_incidents:
            if incident.resolution_date:
                resolution_time = (incident.resolution_date - incident.detected_date).total_seconds() / 3600  # بالساعات
                total_time += resolution_time
        
        return round(total_time / len(resolved_incidents), 2)
    
    def _summarize_audit_trail(self, start_date: datetime, end_date: datetime) -> Dict:
        """تلخيص سجل المراجعة"""
        
        total_events = 0
        event_types = {}
        
        for date_key, logs in self.audit_logs.items():
            log_date = datetime.strptime(date_key, '%Y-%m-%d')
            if start_date <= log_date <= end_date:
                for log_entry in logs:
                    total_events += 1
                    event_type = log_entry['event_type']
                    event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            'total_events': total_events,
            'event_type_breakdown': event_types,
            'period_coverage': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
        }
    
    def _identify_key_achievements(self, assessments: List[ComplianceAssessment], incidents: List[ComplianceIncident]) -> List[str]:
        """تحديد الإنجازات الرئيسية"""
        
        achievements = []
        
        # تحسن في نقاط الامتثال
        if assessments and len(assessments) >= 2:
            latest_score = assessments[-1].overall_score
            previous_score = assessments[-2].overall_score
            
            if latest_score > previous_score + 0.1:
                achievements.append(f'تحسن في نقاط الامتثال بنسبة {round((latest_score - previous_score) * 100, 1)}%')
        
        # انخفاض في الحوادث الحرجة
        critical_incidents = [i for i in incidents if i.severity == 'critical']
        if len(critical_incidents) == 0:
            achievements.append('عدم وجود حوادث حرجة في الفترة المحددة')
        
        # معدل حل عالي للحوادث
        resolved_incidents = [i for i in incidents if i.status == 'resolved']
        if incidents and (len(resolved_incidents) / len(incidents)) > 0.8:
            achievements.append('معدل حل عالي للحوادث (أكثر من 80%)')
        
        return achievements
    
    def _identify_major_concerns(self, assessments: List[ComplianceAssessment], incidents: List[ComplianceIncident]) -> List[str]:
        """تحديد المخاوف الرئيسية"""
        
        concerns = []
        
        # نقاط امتثال منخفضة
        if assessments:
            avg_score = sum(a.overall_score for a in assessments) / len(assessments)
            if avg_score < 0.7:
                concerns.append(f'نقاط امتثال منخفضة (متوسط {round(avg_score * 100, 1)}%)')
        
        # حوادث حرجة غير محلولة
        critical_open_incidents = [
            i for i in incidents 
            if i.severity == 'critical' and i.status != 'resolved'
        ]
        if critical_open_incidents:
            concerns.append(f'{len(critical_open_incidents)} حادث حرج غير محلول')
        
        # مشاكل متكررة
        incident_types = {}
        for incident in incidents:
            incident_types[incident.incident_type] = incident_types.get(incident.incident_type, 0) + 1
        
        for incident_type, count in incident_types.items():
            if count >= 3:
                concerns.append(f'مشاكل متكررة من نوع {incident_type} ({count} مرات)')
        
        return concerns
    
    def _analyze_compliance_by_standard(self, assessments: List[ComplianceAssessment]) -> Dict:
        """تحليل الامتثال حسب المعيار"""
        
        standard_scores = {}
        
        for assessment in assessments:
            standards = assessment.standard.split(', ')
            for standard in standards:
                if standard not in standard_scores:
                    standard_scores[standard] = []
                standard_scores[standard].append(assessment.overall_score)
        
        # حساب متوسط كل معيار
        standard_averages = {}
        for standard, scores in standard_scores.items():
            standard_averages[standard] = {
                'average_score': round(sum(scores) / len(scores), 3),
                'assessment_count': len(scores),
                'compliance_percentage': round((sum(scores) / len(scores)) * 100, 2)
            }
        
        return standard_averages
    
    def _generate_compliance_recommendations(self, compliance_analysis: Dict, incident_analysis: Dict, consent_analysis: Dict) -> List[str]:
        """إنتاج توصيات الامتثال"""
        
        recommendations = []
        
        # توصيات بناءً على نقاط الامتثال
        if compliance_analysis.get('overall_score', 0) < 0.8:
            recommendations.append('تحسين الامتثال العام من خلال معالجة النقاط الضعيفة')
        
        # توصيات بناءً على الحوادث
        if incident_analysis.get('total_incidents', 0) > 5:
            recommendations.append('تعزيز إجراءات الوقاية لتقليل عدد الحوادث')
        
        # توصيات بناءً على الموافقات
        if consent_analysis.get('compliance_rate', 0) < 90:
            recommendations.append('تحسين إدارة موافقات المرضى وتجديدها بانتظام')
        
        # توصيات عامة
        recommendations.extend([
            'تدريب منتظم للفريق على متطلبات الامتثال',
            'مراجعة دورية للسياسات والإجراءات',
            'تحسين أنظمة المراقبة والتنبيه المبكر'
        ])
        
        return recommendations[:10]  # أقصى 10 توصيات
    
    def _create_action_plan(self, recommendations: List[str]) -> List[Dict]:
        """إنشاء خطة عمل"""
        
        action_plan = []
        
        for i, recommendation in enumerate(recommendations[:5]):  # أول 5 توصيات
            action = {
                'action_id': str(uuid.uuid4()),
                'recommendation': recommendation,
                'priority': 'high' if i < 2 else 'medium',
                'assigned_to': 'compliance_team',
                'due_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'status': 'pending',
                'estimated_effort': 'medium',
                'success_criteria': f'تطبيق {recommendation} بنجاح'
            }
            action_plan.append(action)
        
        return action_plan

