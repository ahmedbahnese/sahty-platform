from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class BloodDonor(db.Model):
    __tablename__ = 'blood_donors'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # معلومات المتبرع
    blood_type = db.Column(db.String(5), nullable=False)  # A+, B-, O+, etc.
    weight = db.Column(db.Float, nullable=False)  # minimum 50kg
    age = db.Column(db.Integer, nullable=False)
    
    # حالة الأهلية للتبرع
    is_eligible = db.Column(db.Boolean, default=True)
    last_donation_date = db.Column(db.Date)
    next_eligible_date = db.Column(db.Date)
    
    # معلومات الصحة
    has_chronic_diseases = db.Column(db.Boolean, default=False)
    chronic_diseases_list = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    
    # معلومات الاتصال للطوارئ
    emergency_contact = db.Column(db.Boolean, default=False)
    available_for_emergency = db.Column(db.Boolean, default=True)
    
    # الموقع
    city = db.Column(db.String(100))
    district = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # إعدادات التنبيهات
    notification_enabled = db.Column(db.Boolean, default=True)
    emergency_notification = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    donations = db.relationship('BloodDonation', backref='donor', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'blood_type': self.blood_type,
            'weight': self.weight,
            'age': self.age,
            'is_eligible': self.is_eligible,
            'last_donation_date': self.last_donation_date.isoformat() if self.last_donation_date else None,
            'next_eligible_date': self.next_eligible_date.isoformat() if self.next_eligible_date else None,
            'has_chronic_diseases': self.has_chronic_diseases,
            'chronic_diseases_list': self.chronic_diseases_list,
            'current_medications': self.current_medications,
            'emergency_contact': self.emergency_contact,
            'available_for_emergency': self.available_for_emergency,
            'city': self.city,
            'district': self.district,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'notification_enabled': self.notification_enabled,
            'emergency_notification': self.emergency_notification,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BloodRequest(db.Model):
    __tablename__ = 'blood_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    
    # تفاصيل الطلب
    blood_type = db.Column(db.String(5), nullable=False)
    units_needed = db.Column(db.Integer, nullable=False)
    component_type = db.Column(db.String(30), nullable=False, default='whole_blood')  # whole_blood, plasma, platelets, cryoprecipitate, other
    is_irradiated = db.Column(db.Boolean, nullable=False, default=False)
    urgency_level = db.Column(db.String(20), nullable=False)  # critical, urgent, routine
    
    # معلومات المريض
    patient_name = db.Column(db.String(200), nullable=False)
    patient_age = db.Column(db.Integer)
    medical_condition = db.Column(db.Text)
    
    # معلومات المستشفى
    hospital_name = db.Column(db.String(200), nullable=False)
    hospital_address = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20), nullable=False)
    
    # الموقع
    city = db.Column(db.String(100))
    district = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # حالة الطلب
    status = db.Column(db.String(20), default='active')  # active, fulfilled, cancelled, expired
    needed_by_date = db.Column(db.DateTime, nullable=False)
    
    # معلومات إضافية
    description = db.Column(db.Text)
    special_requirements = db.Column(db.Text)
    transfusion_request_file_path = db.Column(db.String(500))
    transfusion_request_file_name = db.Column(db.String(200))
    document_status = db.Column(db.String(30), nullable=False, default='document_required')  # document_required, verified, forwarded
    forwarded_to_centers_at = db.Column(db.DateTime)
    forwarded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    responses = db.relationship('BloodRequestResponse', backref='request', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'hospital_id': self.hospital_id,
            'blood_type': self.blood_type,
            'units_needed': self.units_needed,
            'component_type': self.component_type,
            'is_irradiated': self.is_irradiated,
            'urgency_level': self.urgency_level,
            'patient_name': self.patient_name,
            'patient_age': self.patient_age,
            'medical_condition': self.medical_condition,
            'hospital_name': self.hospital_name,
            'hospital_address': self.hospital_address,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'city': self.city,
            'district': self.district,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'needed_by_date': self.needed_by_date.isoformat() if self.needed_by_date else None,
            'description': self.description,
            'special_requirements': self.special_requirements,
            'transfusion_request_file_path': self.transfusion_request_file_path,
            'transfusion_request_file_name': self.transfusion_request_file_name,
            'document_status': self.document_status,
            'forwarded_to_centers_at': self.forwarded_to_centers_at.isoformat() if self.forwarded_to_centers_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BloodRequestResponse(db.Model):
    __tablename__ = 'blood_request_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('blood_requests.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('blood_donors.id'), nullable=False)
    
    # استجابة المتبرع
    response_type = db.Column(db.String(20), nullable=False)  # willing, maybe, not_available
    available_date = db.Column(db.DateTime)
    message = db.Column(db.Text)
    
    # حالة الاستجابة
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, completed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'donor_id': self.donor_id,
            'response_type': self.response_type,
            'available_date': self.available_date.isoformat() if self.available_date else None,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BloodDonation(db.Model):
    __tablename__ = 'blood_donations'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('blood_donors.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('blood_requests.id'))
    
    # تفاصيل التبرع
    donation_date = db.Column(db.DateTime, nullable=False)
    units_donated = db.Column(db.Integer, default=1)
    donation_type = db.Column(db.String(20), default='whole_blood')  # whole_blood, plasma, platelets
    
    # معلومات المركز
    donation_center = db.Column(db.String(200))
    center_address = db.Column(db.Text)
    
    # الفحوصات
    pre_donation_screening = db.Column(db.JSON)  # blood pressure, hemoglobin, etc.
    post_donation_tests = db.Column(db.JSON)  # infectious diseases screening
    
    # حالة التبرع
    status = db.Column(db.String(20), default='completed')  # completed, rejected, deferred
    rejection_reason = db.Column(db.Text)
    
    # معلومات إضافية
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'donor_id': self.donor_id,
            'request_id': self.request_id,
            'donation_date': self.donation_date.isoformat() if self.donation_date else None,
            'units_donated': self.units_donated,
            'donation_type': self.donation_type,
            'donation_center': self.donation_center,
            'center_address': self.center_address,
            'pre_donation_screening': self.pre_donation_screening,
            'post_donation_tests': self.post_donation_tests,
            'status': self.status,
            'rejection_reason': self.rejection_reason,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BloodInventory(db.Model):
    __tablename__ = 'blood_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    
    # معلومات المخزون
    blood_type = db.Column(db.String(5), nullable=False)
    units_available = db.Column(db.Integer, default=0)
    units_reserved = db.Column(db.Integer, default=0)
    
    # تواريخ الصلاحية
    expiry_date = db.Column(db.Date)
    days_until_expiry = db.Column(db.Integer)
    
    # حالة المخزون
    status = db.Column(db.String(20), default='available')  # available, low, critical, expired
    minimum_threshold = db.Column(db.Integer, default=5)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'blood_type': self.blood_type,
            'units_available': self.units_available,
            'units_reserved': self.units_reserved,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'days_until_expiry': self.days_until_expiry,
            'status': self.status,
            'minimum_threshold': self.minimum_threshold,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

