"""
نماذج طلبات التحاليل المخبرية والأشعة مع دعم سير العمل الكامل.

المراحل:
  LabRequest:      requested → approved → results_uploaded → completed
  RadiologyRequest: requested → images_uploaded → report_uploaded → shared
"""
from datetime import datetime
import json
from src.models.user import db


# ─────────────────────────────────────────────────────────
# طلبات التحاليل المخبرية
# ─────────────────────────────────────────────────────────

class LabRequest(db.Model):
    __tablename__ = 'lab_requests'

    id                  = db.Column(db.Integer, primary_key=True)

    # الأطراف المعنية
    patient_id          = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    requesting_user_id  = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)

    # معلومات الطلب — اسم تحليل واحد (للتوافق العكسي) أو قائمة JSON
    test_name           = db.Column(db.String(200), nullable=False)
    tests_json          = db.Column(db.Text, default='[]')   # [{"name":"CBC","category":"blood","preparation":"..."}]
    test_category       = db.Column(db.String(100))
    urgency             = db.Column(db.String(20), default='routine')   # routine / urgent / emergency
    clinical_notes      = db.Column(db.Text)
    ordering_doctor     = db.Column(db.String(200))

    # مركز التحاليل
    lab_center_name     = db.Column(db.String(200))

    # تعليمات التحضير
    preparation_instructions = db.Column(db.Text)   # JSON list of strings

    # وثيقة الطلب الأصلي
    request_doc_path    = db.Column(db.String(500))
    request_doc_name    = db.Column(db.String(200))

    # موعد التحليل
    scheduled_datetime  = db.Column(db.DateTime)

    # التحصيل المنزلي
    home_collection          = db.Column(db.Boolean, default=False)
    collection_address       = db.Column(db.Text)
    collection_lat           = db.Column(db.Float)
    collection_lng           = db.Column(db.Float)
    collection_date          = db.Column(db.Date)
    collection_time          = db.Column(db.String(10))   # HH:MM
    collection_staff_name    = db.Column(db.String(200))

    # سير العمل: requested → approved → results_uploaded → completed | rejected
    status              = db.Column(db.String(30), default='requested')

    # الاعتماد
    approved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at         = db.Column(db.DateTime)
    approval_notes      = db.Column(db.Text)
    rejection_reason    = db.Column(db.Text)

    # النتائج
    lab_name            = db.Column(db.String(200))
    result_value        = db.Column(db.String(200))
    result_unit         = db.Column(db.String(50))
    reference_range     = db.Column(db.String(200))
    result_status       = db.Column(db.String(20))   # normal / abnormal / critical
    result_interpretation = db.Column(db.Text)
    result_file_path    = db.Column(db.String(500))
    result_file_name    = db.Column(db.String(200))
    result_uploaded_at  = db.Column(db.DateTime)
    result_uploaded_by  = db.Column(db.Integer, db.ForeignKey('users.id'))

    # الإشعارات
    notified_at         = db.Column(db.DateTime)

    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def tests(self):
        try:
            return json.loads(self.tests_json or '[]')
        except Exception:
            return []

    def to_dict(self):
        return {
            'id':                    self.id,
            'patient_id':            self.patient_id,
            'requesting_user_id':    self.requesting_user_id,
            'test_name':             self.test_name,
            'tests':                 self.tests,
            'test_category':         self.test_category,
            'urgency':               self.urgency,
            'clinical_notes':        self.clinical_notes,
            'ordering_doctor':       self.ordering_doctor,
            'lab_center_name':       self.lab_center_name,
            'preparation_instructions': self.preparation_instructions,
            'request_doc_path':      self.request_doc_path,
            'request_doc_name':      self.request_doc_name,
            'scheduled_datetime':    self.scheduled_datetime.isoformat() if self.scheduled_datetime else None,
            'home_collection':       self.home_collection,
            'collection_address':    self.collection_address,
            'collection_lat':        self.collection_lat,
            'collection_lng':        self.collection_lng,
            'collection_date':       self.collection_date.isoformat() if self.collection_date else None,
            'collection_time':       self.collection_time,
            'collection_staff_name': self.collection_staff_name,
            'status':                self.status,
            'approved_by_user_id':   self.approved_by_user_id,
            'approved_at':           self.approved_at.isoformat()  if self.approved_at  else None,
            'approval_notes':        self.approval_notes,
            'rejection_reason':      self.rejection_reason,
            'lab_name':              self.lab_name,
            'result_value':          self.result_value,
            'result_unit':           self.result_unit,
            'reference_range':       self.reference_range,
            'result_status':         self.result_status,
            'result_interpretation': self.result_interpretation,
            'result_file_path':      self.result_file_path,
            'result_file_name':      self.result_file_name,
            'result_uploaded_at':    self.result_uploaded_at.isoformat() if self.result_uploaded_at else None,
            'notified_at':           self.notified_at.isoformat() if self.notified_at else None,
            'created_at':            self.created_at.isoformat() if self.created_at else None,
            'updated_at':            self.updated_at.isoformat() if self.updated_at else None,
        }


# ─────────────────────────────────────────────────────────
# طلبات الأشعة والتصوير الطبي
# ─────────────────────────────────────────────────────────

class RadiologyRequest(db.Model):
    __tablename__ = 'radiology_requests'

    id                  = db.Column(db.Integer, primary_key=True)

    # الأطراف المعنية
    patient_id          = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    requesting_user_id  = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)

    # معلومات الطلب
    scan_type           = db.Column(db.String(50), nullable=False)  # xray/mri/ct/ultrasound/pet/mammo
    body_part           = db.Column(db.String(200), nullable=False)
    urgency             = db.Column(db.String(20), default='routine')  # routine / urgent / emergency
    clinical_reason     = db.Column(db.Text)
    ordering_doctor     = db.Column(db.String(200))

    # مركز الأشعة
    radiology_center_name = db.Column(db.String(200))

    # وثيقة الطلب الأصلي (PDF/صورة)
    request_doc_path    = db.Column(db.String(500))
    request_doc_name    = db.Column(db.String(200))

    # موعد الفحص
    scheduled_datetime  = db.Column(db.DateTime)

    # سير العمل: requested → images_uploaded → report_uploaded → shared | rejected
    status              = db.Column(db.String(30), default='requested')

    rejection_reason    = db.Column(db.Text)

    # الصور المرفوعة (مسارات JSON)
    image_paths_json    = db.Column(db.Text, default='[]')
    images_uploaded_at  = db.Column(db.DateTime)
    images_uploaded_by  = db.Column(db.Integer, db.ForeignKey('users.id'))

    # التقرير
    facility            = db.Column(db.String(200))
    radiologist_name    = db.Column(db.String(200))
    findings            = db.Column(db.Text)
    impression          = db.Column(db.Text)
    recommendation      = db.Column(db.Text)
    report_file_path    = db.Column(db.String(500))
    report_file_name    = db.Column(db.String(200))
    report_uploaded_at  = db.Column(db.DateTime)
    report_uploaded_by  = db.Column(db.Integer, db.ForeignKey('users.id'))

    # المشاركة / الإشعار
    shared_at           = db.Column(db.DateTime)

    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def image_paths(self):
        try:
            return json.loads(self.image_paths_json or '[]')
        except Exception:
            return []

    def to_dict(self):
        return {
            'id':                     self.id,
            'patient_id':             self.patient_id,
            'requesting_user_id':     self.requesting_user_id,
            'scan_type':              self.scan_type,
            'body_part':              self.body_part,
            'urgency':                self.urgency,
            'clinical_reason':        self.clinical_reason,
            'ordering_doctor':        self.ordering_doctor,
            'radiology_center_name':  self.radiology_center_name,
            'request_doc_path':       self.request_doc_path,
            'request_doc_name':       self.request_doc_name,
            'scheduled_datetime':     self.scheduled_datetime.isoformat() if self.scheduled_datetime else None,
            'status':                 self.status,
            'rejection_reason':       self.rejection_reason,
            'image_paths':            self.image_paths,
            'images_uploaded_at':     self.images_uploaded_at.isoformat() if self.images_uploaded_at else None,
            'facility':               self.facility,
            'radiologist_name':       self.radiologist_name,
            'findings':               self.findings,
            'impression':             self.impression,
            'recommendation':         self.recommendation,
            'report_file_path':       self.report_file_path,
            'report_file_name':       self.report_file_name,
            'report_uploaded_at':     self.report_uploaded_at.isoformat() if self.report_uploaded_at else None,
            'shared_at':              self.shared_at.isoformat() if self.shared_at else None,
            'created_at':             self.created_at.isoformat() if self.created_at else None,
            'updated_at':             self.updated_at.isoformat() if self.updated_at else None,
        }
