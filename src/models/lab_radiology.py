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

    # معلومات الطلب
    test_name           = db.Column(db.String(200), nullable=False)
    test_category       = db.Column(db.String(100))   # blood / urine / culture / hormones / ...
    urgency             = db.Column(db.String(20), default='normal')   # urgent / normal / routine
    clinical_notes      = db.Column(db.Text)
    ordering_doctor     = db.Column(db.String(200))

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
    result_file_path    = db.Column(db.String(500))  # مسار الملف المرفوع
    result_file_name    = db.Column(db.String(200))
    result_uploaded_at  = db.Column(db.DateTime)
    result_uploaded_by  = db.Column(db.Integer, db.ForeignKey('users.id'))

    # الإشعارات
    notified_at         = db.Column(db.DateTime)

    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':                    self.id,
            'patient_id':            self.patient_id,
            'requesting_user_id':    self.requesting_user_id,
            'test_name':             self.test_name,
            'test_category':         self.test_category,
            'urgency':               self.urgency,
            'clinical_notes':        self.clinical_notes,
            'ordering_doctor':       self.ordering_doctor,
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
    urgency             = db.Column(db.String(20), default='normal')
    clinical_reason     = db.Column(db.Text)
    ordering_doctor     = db.Column(db.String(200))

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
            'id':                   self.id,
            'patient_id':           self.patient_id,
            'requesting_user_id':   self.requesting_user_id,
            'scan_type':            self.scan_type,
            'body_part':            self.body_part,
            'urgency':              self.urgency,
            'clinical_reason':      self.clinical_reason,
            'ordering_doctor':      self.ordering_doctor,
            'status':               self.status,
            'rejection_reason':     self.rejection_reason,
            'image_paths':          self.image_paths,
            'images_uploaded_at':   self.images_uploaded_at.isoformat() if self.images_uploaded_at else None,
            'facility':             self.facility,
            'radiologist_name':     self.radiologist_name,
            'findings':             self.findings,
            'impression':           self.impression,
            'recommendation':       self.recommendation,
            'report_file_path':     self.report_file_path,
            'report_file_name':     self.report_file_name,
            'report_uploaded_at':   self.report_uploaded_at.isoformat() if self.report_uploaded_at else None,
            'shared_at':            self.shared_at.isoformat() if self.shared_at else None,
            'created_at':           self.created_at.isoformat() if self.created_at else None,
            'updated_at':           self.updated_at.isoformat() if self.updated_at else None,
        }
