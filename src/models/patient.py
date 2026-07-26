from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Patient(db.Model):
    """
    نموذج قاعدة البيانات للمرضى.

    يمثل جدول المرضى في قاعدة البيانات ويحتوي على معلومات شخصية وطبية مفصلة عن المريض.
    """
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # معلومات شخصية
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # male, female
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text)
    
    # معلومات طبية
    blood_type = db.Column(db.String(5))  # A+, B-, O+, etc.
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    
    # معلومات إضافية
    insurance_number = db.Column(db.String(50))
    insurance_provider = db.Column(db.String(100))
    preferred_language = db.Column(db.String(10), default='ar')
    
    # تواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    medications = db.relationship('Medication', backref='patient', lazy=True)
    allergies = db.relationship('Allergy', backref='patient', lazy=True)
    
    def to_dict(self):
        """
        يحول كائن المريض إلى قاموس (dictionary).

        Returns:
            dict: قاموس يحتوي على جميع معلومات المريض.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'national_id': self.national_id,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'blood_type': self.blood_type,
            'height': self.height,
            'weight': self.weight,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'insurance_number': self.insurance_number,
            'insurance_provider': self.insurance_provider,
            'preferred_language': self.preferred_language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MedicalRecord(db.Model):
    """
    نموذج قاعدة البيانات للسجلات الطبية.

    يمثل جدول السجلات الطبية في قاعدة البيانات ويحتوي على تفاصيل الزيارات والتشخيصات.
    """
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    
    # تفاصيل السجل الطبي
    visit_date = db.Column(db.DateTime, nullable=False)
    diagnosis = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    treatment = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # نتائج الفحوصات
    vital_signs = db.Column(db.JSON)  # blood pressure, temperature, etc.
    lab_results = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        يحول كائن السجل الطبي إلى قاموس (dictionary).

        Returns:
            dict: قاموس يحتوي على جميع معلومات السجل الطبي.
        """
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'diagnosis': self.diagnosis,
            'symptoms': self.symptoms,
            'treatment': self.treatment,
            'notes': self.notes,
            'vital_signs': self.vital_signs,
            'lab_results': self.lab_results,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Allergy(db.Model):
    """
    نموذج قاعدة البيانات للحساسية.

    يمثل جدول الحساسية في قاعدة البيانات ويحتوي على تفاصيل الحساسية لدى المريض.
    """
    __tablename__ = 'allergies'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    allergen = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20))  # mild, moderate, severe
    reaction = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """
        يحول كائن الحساسية إلى قاموس (dictionary).

        Returns:
            dict: قاموس يحتوي على جميع معلومات الحساسية.
        """
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'allergen': self.allergen,
            'severity': self.severity,
            'reaction': self.reaction,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }



