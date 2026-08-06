"""
نماذج الملف الطبي الإلكتروني الكامل.
يشمل: الأمراض، العمليات، التطعيمات، التحاليل، الأشعة، التاريخ المرضي.
الحساسية والأدوية موجودة في patient.py و medication.py.
"""
from datetime import datetime
from src.models.user import db


class Disease(db.Model):
    """الأمراض والتشخيصات."""
    __tablename__ = 'diseases'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)          # اسم المرض
    icd_code = db.Column(db.String(20))                       # رمز ICD
    status = db.Column(db.String(30), default='active')       # active / chronic / resolved
    severity = db.Column(db.String(20))                       # mild / moderate / severe
    diagnosis_date = db.Column(db.Date)
    resolution_date = db.Column(db.Date)                      # تاريخ الشفاء
    treating_doctor = db.Column(db.String(200))
    hospital = db.Column(db.String(200))
    treatment_summary = db.Column(db.Text)
    notes = db.Column(db.Text)
    attachment_data = db.Column(db.Text)                      # base64 صورة الروشتة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'name': self.name,
            'icd_code': self.icd_code,
            'status': self.status,
            'severity': self.severity,
            'diagnosis_date': self.diagnosis_date.isoformat() if self.diagnosis_date else None,
            'resolution_date': self.resolution_date.isoformat() if self.resolution_date else None,
            'treating_doctor': self.treating_doctor,
            'hospital': self.hospital,
            'treatment_summary': self.treatment_summary,
            'notes': self.notes,
            'attachment_data': self.attachment_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Surgery(db.Model):
    """العمليات الجراحية."""
    __tablename__ = 'surgeries'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)          # اسم العملية
    surgery_type = db.Column(db.String(100))                  # نوع العملية
    surgery_date = db.Column(db.Date)
    hospital = db.Column(db.String(200))
    surgeon = db.Column(db.String(200))
    anesthesia_type = db.Column(db.String(50))                # general / local / spinal / epidural
    duration_minutes = db.Column(db.Integer)
    outcome = db.Column(db.String(50))                        # successful / complicated / failed
    complications = db.Column(db.Text)
    post_op_notes = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'name': self.name,
            'surgery_type': self.surgery_type,
            'surgery_date': self.surgery_date.isoformat() if self.surgery_date else None,
            'hospital': self.hospital,
            'surgeon': self.surgeon,
            'anesthesia_type': self.anesthesia_type,
            'duration_minutes': self.duration_minutes,
            'outcome': self.outcome,
            'complications': self.complications,
            'post_op_notes': self.post_op_notes,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Vaccination(db.Model):
    """التطعيمات واللقاحات."""
    __tablename__ = 'vaccinations'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    vaccine_name = db.Column(db.String(200), nullable=False)
    disease_prevented = db.Column(db.String(200))             # المرض الذي يقي منه
    dose_number = db.Column(db.Integer, default=1)
    total_doses = db.Column(db.Integer)
    date_given = db.Column(db.Date)
    next_due_date = db.Column(db.Date)
    provider = db.Column(db.String(200))                      # الجهة المقدِّمة
    batch_number = db.Column(db.String(100))
    administration_site = db.Column(db.String(100))           # ذراع يمين / ذراع يسار / فخذ
    reaction = db.Column(db.Text)                             # تفاعل ما بعد التطعيم
    notes = db.Column(db.Text)
    attachment_data = db.Column(db.Text)                      # base64 صورة شهادة التطعيم
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'vaccine_name': self.vaccine_name,
            'disease_prevented': self.disease_prevented,
            'dose_number': self.dose_number,
            'total_doses': self.total_doses,
            'date_given': self.date_given.isoformat() if self.date_given else None,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'provider': self.provider,
            'batch_number': self.batch_number,
            'administration_site': self.administration_site,
            'reaction': self.reaction,
            'notes': self.notes,
            'attachment_data': self.attachment_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LabTest(db.Model):
    """التحاليل المخبرية."""
    __tablename__ = 'lab_tests'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    test_name = db.Column(db.String(200), nullable=False)
    test_category = db.Column(db.String(100))                 # blood / urine / culture / hormones / ...
    test_date = db.Column(db.Date)
    lab_name = db.Column(db.String(200))
    ordering_doctor = db.Column(db.String(200))
    result_value = db.Column(db.String(200))
    unit = db.Column(db.String(50))
    reference_range = db.Column(db.String(200))
    status = db.Column(db.String(20), default='normal')       # normal / abnormal / critical
    interpretation = db.Column(db.Text)
    notes = db.Column(db.Text)
    attachment_data = db.Column(db.Text)                      # base64 صورة نتيجة التحليل
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'test_name': self.test_name,
            'test_category': self.test_category,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'lab_name': self.lab_name,
            'ordering_doctor': self.ordering_doctor,
            'result_value': self.result_value,
            'unit': self.unit,
            'reference_range': self.reference_range,
            'status': self.status,
            'interpretation': self.interpretation,
            'notes': self.notes,
            'attachment_data': self.attachment_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Radiology(db.Model):
    """الأشعة والتصوير الطبي."""
    __tablename__ = 'radiology_scans'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    scan_type = db.Column(db.String(50), nullable=False)      # xray / mri / ct / ultrasound / pet / mammo
    body_part = db.Column(db.String(200), nullable=False)
    scan_date = db.Column(db.Date)
    facility = db.Column(db.String(200))
    radiologist = db.Column(db.String(200))
    ordering_doctor = db.Column(db.String(200))
    reason = db.Column(db.Text)                               # سبب الطلب
    findings = db.Column(db.Text)                             # النتائج
    impression = db.Column(db.Text)                           # التفسير النهائي
    recommendation = db.Column(db.Text)                       # التوصيات
    notes = db.Column(db.Text)
    attachment_data = db.Column(db.Text)                      # base64 صورة الأشعة
    report_data = db.Column(db.Text)                          # base64 صورة التقرير
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'scan_type': self.scan_type,
            'body_part': self.body_part,
            'scan_date': self.scan_date.isoformat() if self.scan_date else None,
            'facility': self.facility,
            'radiologist': self.radiologist,
            'ordering_doctor': self.ordering_doctor,
            'reason': self.reason,
            'findings': self.findings,
            'impression': self.impression,
            'recommendation': self.recommendation,
            'notes': self.notes,
            'attachment_data': self.attachment_data,
            'report_data': self.report_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class BloodGasReading(db.Model):
    """قراءات غازات الدم."""
    __tablename__ = 'blood_gas_readings'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    reading_date = db.Column(db.Date)
    reading_time = db.Column(db.String(10))        # HH:MM
    mode = db.Column(db.String(50))                # وضع التنفس (Room Air / O2 / Ventilator)
    ph = db.Column(db.String(20))
    pco2 = db.Column(db.String(20))
    hco3 = db.Column(db.String(20))
    o2 = db.Column(db.String(20))
    spo2 = db.Column(db.String(20))
    k = db.Column(db.String(20))
    lactate = db.Column(db.String(20))
    notes = db.Column(db.Text)
    attachment_data = db.Column(db.Text)            # base64 صورة مرفقة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'reading_date': self.reading_date.isoformat() if self.reading_date else None,
            'reading_time': self.reading_time,
            'mode': self.mode,
            'ph': self.ph,
            'pco2': self.pco2,
            'hco3': self.hco3,
            'o2': self.o2,
            'spo2': self.spo2,
            'k': self.k,
            'lactate': self.lactate,
            'notes': self.notes,
            'attachment_data': self.attachment_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ECGRecord(db.Model):
    """رسومات القلب (تخطيط القلب)."""
    __tablename__ = 'ecg_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    ecg_date = db.Column(db.Date)
    facility = db.Column(db.String(200))
    ordering_doctor = db.Column(db.String(200))
    findings = db.Column(db.Text)                   # النتائج / الملاحظات
    notes = db.Column(db.Text)
    attachment_data = db.Column(db.Text)            # base64 صورة رسم القلب
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'ecg_date': self.ecg_date.isoformat() if self.ecg_date else None,
            'facility': self.facility,
            'ordering_doctor': self.ordering_doctor,
            'findings': self.findings,
            'notes': self.notes,
            'attachment_data': self.attachment_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class MedicalHistory(db.Model):
    """التاريخ المرضي العام والعائلي."""
    __tablename__ = 'medical_history'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, unique=True)

    # العادات والنمط الصحي
    smoking_status = db.Column(db.String(30))                 # never / former / current
    smoking_years = db.Column(db.Integer)
    alcohol_use = db.Column(db.String(30))                    # never / occasional / regular
    physical_activity = db.Column(db.String(30))              # sedentary / light / moderate / active
    diet_type = db.Column(db.String(100))

    # التاريخ العائلي
    family_history = db.Column(db.JSON)                       # [{disease, relation, notes}]

    # أمراض مزمنة معروفة (نص حر)
    chronic_conditions = db.Column(db.Text)

    # الأمراض الوراثية
    genetic_conditions = db.Column(db.Text)

    # ملاحظات عامة
    general_notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'smoking_status': self.smoking_status,
            'smoking_years': self.smoking_years,
            'alcohol_use': self.alcohol_use,
            'physical_activity': self.physical_activity,
            'diet_type': self.diet_type,
            'family_history': self.family_history or [],
            'chronic_conditions': self.chronic_conditions,
            'genetic_conditions': self.genetic_conditions,
            'general_notes': self.general_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
