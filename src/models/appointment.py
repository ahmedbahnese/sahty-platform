from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    # تفاصيل الموعد
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=30)  # in minutes
    appointment_type = db.Column(db.String(20), nullable=False)  # in_person, telemedicine
    
    # حالة الموعد
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, completed, cancelled, no_show
    
    # تفاصيل إضافية
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    
    # معلومات الدفع
    fee = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, refunded
    payment_method = db.Column(db.String(50))
    
    # معلومات الاستشارة عن بُعد
    meeting_link = db.Column(db.String(500))
    meeting_id = db.Column(db.String(100))
    
    # تذكيرات
    reminder_sent = db.Column(db.Boolean, default=False)
    reminder_sent_at = db.Column(db.DateTime)

    # ── حجز لفرد من الأسرة ────────────────────────────────────────────────────
    for_family_member_id = db.Column(db.Integer, db.ForeignKey('family_members.id'), nullable=True)
    for_member_name = db.Column(db.String(200), nullable=True)   # اسم الفرد حتى بدون linked profile

    # تواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'duration': self.duration,
            'appointment_type': self.appointment_type,
            'status': self.status,
            'reason': self.reason,
            'notes': self.notes,
            'symptoms': self.symptoms,
            'fee': self.fee,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'meeting_link': self.meeting_link,
            'meeting_id': self.meeting_id,
            'reminder_sent': self.reminder_sent,
            'reminder_sent_at': self.reminder_sent_at.isoformat() if self.reminder_sent_at else None,
            'for_family_member_id': self.for_family_member_id,
            'for_member_name': self.for_member_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AppointmentHistory(db.Model):
    __tablename__ = 'appointment_history'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    
    # تغييرات الحالة
    previous_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    change_reason = db.Column(db.Text)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'previous_status': self.previous_status,
            'new_status': self.new_status,
            'change_reason': self.change_reason,
            'changed_by': self.changed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AppointmentRating(db.Model):
    __tablename__ = 'appointment_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    # التقييم
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)
    
    # جوانب التقييم
    punctuality_rating = db.Column(db.Integer)  # 1-5
    communication_rating = db.Column(db.Integer)  # 1-5
    treatment_effectiveness = db.Column(db.Integer)  # 1-5
    
    # توصية
    would_recommend = db.Column(db.Boolean)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'rating': self.rating,
            'review': self.review,
            'punctuality_rating': self.punctuality_rating,
            'communication_rating': self.communication_rating,
            'treatment_effectiveness': self.treatment_effectiveness,
            'would_recommend': self.would_recommend,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

