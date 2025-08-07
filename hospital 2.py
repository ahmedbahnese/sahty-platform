from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات أساسية
    name = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))
    type = db.Column(db.String(50), nullable=False)  # public, private, specialized
    
    # معلومات الاتصال
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    
    # العنوان والموقع
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # معلومات الخدمات
    specializations = db.Column(db.Text)  # JSON string of specializations
    services = db.Column(db.Text)  # JSON string of services
    facilities = db.Column(db.Text)  # JSON string of facilities
    
    # معلومات الطوارئ
    has_emergency = db.Column(db.Boolean, default=False)
    emergency_phone = db.Column(db.String(20))
    is_24_hours = db.Column(db.Boolean, default=False)
    
    # معلومات السعة
    total_beds = db.Column(db.Integer)
    available_beds = db.Column(db.Integer)
    icu_beds = db.Column(db.Integer)
    available_icu_beds = db.Column(db.Integer)
    
    # التقييمات
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    
    # معلومات التأمين
    accepted_insurance = db.Column(db.Text)  # JSON string of insurance providers
    
    # حالة المستشفى
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # ساعات العمل
    working_hours = db.Column(db.JSON)  # JSON object with daily hours
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    departments = db.relationship('HospitalDepartment', backref='hospital', lazy=True)
    blood_requests = db.relationship('BloodRequest', backref='hospital', lazy=True)
    blood_inventory = db.relationship('BloodInventory', backref='hospital', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'type': self.type,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'address': self.address,
            'city': self.city,
            'district': self.district,
            'postal_code': self.postal_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'specializations': self.specializations,
            'services': self.services,
            'facilities': self.facilities,
            'has_emergency': self.has_emergency,
            'emergency_phone': self.emergency_phone,
            'is_24_hours': self.is_24_hours,
            'total_beds': self.total_beds,
            'available_beds': self.available_beds,
            'icu_beds': self.icu_beds,
            'available_icu_beds': self.available_icu_beds,
            'rating': self.rating,
            'total_reviews': self.total_reviews,
            'accepted_insurance': self.accepted_insurance,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'working_hours': self.working_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class HospitalDepartment(db.Model):
    __tablename__ = 'hospital_departments'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    
    # معلومات القسم
    name = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # معلومات الاتصال
    phone = db.Column(db.String(20))
    extension = db.Column(db.String(10))
    
    # معلومات الموقع داخل المستشفى
    floor = db.Column(db.String(20))
    wing = db.Column(db.String(50))
    
    # الخدمات والمعدات
    services = db.Column(db.Text)  # JSON string
    equipment = db.Column(db.Text)  # JSON string
    
    # الطاقم الطبي
    head_of_department = db.Column(db.String(100))
    total_doctors = db.Column(db.Integer, default=0)
    total_nurses = db.Column(db.Integer, default=0)
    
    # ساعات العمل
    working_hours = db.Column(db.JSON)
    
    # حالة القسم
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'name': self.name,
            'name_en': self.name_en,
            'description': self.description,
            'phone': self.phone,
            'extension': self.extension,
            'floor': self.floor,
            'wing': self.wing,
            'services': self.services,
            'equipment': self.equipment,
            'head_of_department': self.head_of_department,
            'total_doctors': self.total_doctors,
            'total_nurses': self.total_nurses,
            'working_hours': self.working_hours,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EmergencyService(db.Model):
    __tablename__ = 'emergency_services'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات الخدمة
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # ambulance, fire, police, poison_control
    phone = db.Column(db.String(20), nullable=False)
    
    # معلومات الموقع
    city = db.Column(db.String(100))
    coverage_area = db.Column(db.Text)  # JSON string of covered areas
    
    # معلومات الخدمة
    is_24_hours = db.Column(db.Boolean, default=True)
    response_time = db.Column(db.Integer)  # average response time in minutes
    
    # معلومات إضافية
    description = db.Column(db.Text)
    languages_supported = db.Column(db.String(100))  # ar,en,fr
    
    # حالة الخدمة
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'phone': self.phone,
            'city': self.city,
            'coverage_area': self.coverage_area,
            'is_24_hours': self.is_24_hours,
            'response_time': self.response_time,
            'description': self.description,
            'languages_supported': self.languages_supported,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class HospitalReview(db.Model):
    __tablename__ = 'hospital_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # التقييم
    overall_rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    cleanliness_rating = db.Column(db.Integer)
    staff_rating = db.Column(db.Integer)
    facilities_rating = db.Column(db.Integer)
    waiting_time_rating = db.Column(db.Integer)
    
    # المراجعة
    review_title = db.Column(db.String(200))
    review_text = db.Column(db.Text)
    
    # معلومات إضافية
    visit_date = db.Column(db.Date)
    department_visited = db.Column(db.String(100))
    would_recommend = db.Column(db.Boolean)
    
    # حالة المراجعة
    is_verified = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'patient_id': self.patient_id,
            'overall_rating': self.overall_rating,
            'cleanliness_rating': self.cleanliness_rating,
            'staff_rating': self.staff_rating,
            'facilities_rating': self.facilities_rating,
            'waiting_time_rating': self.waiting_time_rating,
            'review_title': self.review_title,
            'review_text': self.review_text,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'department_visited': self.department_visited,
            'would_recommend': self.would_recommend,
            'is_verified': self.is_verified,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

