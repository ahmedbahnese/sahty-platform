"""
نموذج الوصفات الطبية — يشمل الوصفة ومحتوياتها وحالة الصرف.
"""
from datetime import datetime, date
from src.models.user import db


class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    patient_id  = db.Column(db.Integer, db.ForeignKey('patients.id'),  nullable=False)
    doctor_id   = db.Column(db.Integer, db.ForeignKey('doctors.id'),   nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)

    # التشخيص والملاحظات
    diagnosis = db.Column(db.Text)
    notes     = db.Column(db.Text)

    # الحالة: active | sent_to_pharmacy | dispensed | cancelled
    status = db.Column(db.String(30), default='active', nullable=False)

    # الصيدلية
    pharmacy_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    pharmacy_name    = db.Column(db.String(200))
    sent_to_pharmacy_at = db.Column(db.DateTime)
    dispensed_at        = db.Column(db.DateTime)
    dispensed_by        = db.Column(db.String(200))

    # صلاحية الوصفة
    valid_until = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    items = db.relationship(
        'PrescriptionItem', backref='prescription',
        lazy=True, cascade='all, delete-orphan'
    )

    def to_dict(self, include_items=True):
        d = {
            'id':             self.id,
            'patient_id':     self.patient_id,
            'doctor_id':      self.doctor_id,
            'appointment_id': self.appointment_id,
            'diagnosis':      self.diagnosis,
            'notes':          self.notes,
            'status':         self.status,
            'pharmacy_user_id':      self.pharmacy_user_id,
            'pharmacy_name':         self.pharmacy_name,
            'sent_to_pharmacy_at':   self.sent_to_pharmacy_at.isoformat() if self.sent_to_pharmacy_at else None,
            'dispensed_at':          self.dispensed_at.isoformat() if self.dispensed_at else None,
            'dispensed_by':          self.dispensed_by,
            'valid_until':           self.valid_until.isoformat() if self.valid_until else None,
            'created_at':            self.created_at.isoformat() if self.created_at else None,
            'updated_at':            self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_items:
            d['items'] = [i.to_dict() for i in self.items]
        return d


class PrescriptionItem(db.Model):
    __tablename__ = 'prescription_items'

    id              = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)

    drug_name    = db.Column(db.String(200), nullable=False)
    generic_name = db.Column(db.String(200))
    dosage       = db.Column(db.String(100), nullable=False)
    form         = db.Column(db.String(50))   # tablet, capsule, syrup …
    frequency    = db.Column(db.String(100), nullable=False)
    duration     = db.Column(db.String(100))
    quantity     = db.Column(db.String(100))
    instructions = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':              self.id,
            'prescription_id': self.prescription_id,
            'drug_name':       self.drug_name,
            'generic_name':    self.generic_name,
            'dosage':          self.dosage,
            'form':            self.form,
            'frequency':       self.frequency,
            'duration':        self.duration,
            'quantity':        self.quantity,
            'instructions':    self.instructions,
            'created_at':      self.created_at.isoformat() if self.created_at else None,
        }
