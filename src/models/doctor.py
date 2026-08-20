from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # معلومات شخصية
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # معلومات مهنية
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    sub_specialization = db.Column(db.String(100))
    years_of_experience = db.Column(db.Integer)
    
    # معلومات العيادة/المستشفى
    clinic_name = db.Column(db.String(200))
    clinic_address = db.Column(db.Text)
    clinic_locations = db.Column(db.JSON, default=list)
    profile_image_url = db.Column(db.String(500))
    hospital_affiliation = db.Column(db.String(200))
    
    # معلومات الاستشارة
    consultation_fee = db.Column(db.Float)
    consultation_duration = db.Column(db.Integer)  # in minutes
    available_for_telemedicine = db.Column(db.Boolean, default=True)
    
    # تقييمات
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    
    # حالة الحساب
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # تواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    medical_records = db.relationship('MedicalRecord', backref='doctor', lazy=True)
    availability = db.relationship('DoctorAvailability', backref='doctor', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email,
            'license_number': self.license_number,
            'specialization': self.specialization,
            'sub_specialization': self.sub_specialization,
            'years_of_experience': self.years_of_experience,
            'clinic_name': self.clinic_name,
            'clinic_address': self.clinic_address,
            'clinic_locations': self.clinic_locations or [],
            'profile_image_url': self.profile_image_url,
            'hospital_affiliation': self.hospital_affiliation,
            'consultation_fee': self.consultation_fee,
            'consultation_duration': self.consultation_duration,
            'available_for_telemedicine': self.available_for_telemedicine,
            'rating': self.rating,
            'total_reviews': self.total_reviews,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Specialization(db.Model):
    __tablename__ = 'specializations'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

