"""
نماذج نظام الطوارئ الطبية.

EmergencyAlert  — تسجيل حوادث الطوارئ / SOS / طلبات الإسعاف
FamilyContact   — جهات الاتصال الأسرية المرتبطة بالمريض
"""
from datetime import datetime
from src.models.user import db


class EmergencyAlert(db.Model):
    """سجل حدث طوارئ (SOS أو طلب إسعاف)."""
    __tablename__ = 'emergency_alerts'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id      = db.Column(db.Integer, db.ForeignKey('patients.id'))

    alert_type      = db.Column(db.String(30), default='sos')
    # sos | ambulance_request | family_notify

    # الموقع
    latitude        = db.Column(db.Float)
    longitude       = db.Column(db.Float)
    location_text   = db.Column(db.String(500))   # نص العنوان

    # تفاصيل الحالة
    emergency_type  = db.Column(db.String(100))   # نوبة قلبية / حادث سير...
    severity        = db.Column(db.String(20))     # critical / urgent / moderate
    description     = db.Column(db.Text)
    caller_name     = db.Column(db.String(200))
    caller_phone    = db.Column(db.String(30))

    # الحالة
    status          = db.Column(db.String(30), default='active')
    # active | acknowledged | resolved | cancelled

    # العائلة
    family_notified = db.Column(db.Boolean, default=False)
    notified_at     = db.Column(db.DateTime)

    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':              self.id,
            'user_id':         self.user_id,
            'patient_id':      self.patient_id,
            'alert_type':      self.alert_type,
            'latitude':        self.latitude,
            'longitude':       self.longitude,
            'location_text':   self.location_text,
            'emergency_type':  self.emergency_type,
            'severity':        self.severity,
            'description':     self.description,
            'caller_name':     self.caller_name,
            'caller_phone':    self.caller_phone,
            'status':          self.status,
            'family_notified': self.family_notified,
            'notified_at':     self.notified_at.isoformat()  if self.notified_at  else None,
            'created_at':      self.created_at.isoformat()   if self.created_at   else None,
        }


class FamilyContact(db.Model):
    """جهة اتصال أسرية مرتبطة بمستخدم."""
    __tablename__ = 'family_contacts'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    name         = db.Column(db.String(200), nullable=False)
    phone        = db.Column(db.String(30),  nullable=False)
    relationship = db.Column(db.String(50))   # أب / أم / زوج / ابن ...
    is_primary   = db.Column(db.Boolean, default=False)

    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':           self.id,
            'user_id':      self.user_id,
            'name':         self.name,
            'phone':        self.phone,
            'relationship': self.relationship,
            'is_primary':   self.is_primary,
            'created_at':   self.created_at.isoformat() if self.created_at else None,
        }
