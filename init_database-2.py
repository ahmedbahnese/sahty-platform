#!/usr/bin/env python3
"""
ملف تهيئة قاعدة البيانات لمشروع صحتك في أمان
يقوم بإنشاء الجداول والبيانات الأولية المطلوبة
"""

import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"خطأ في استيراد المكتبات المطلوبة: {e}")
    print("يرجى تثبيت المتطلبات باستخدام: pip install -r requirements.txt")
    sys.exit(1)

# إعداد التطبيق
app = Flask(__name__)

# تحميل إعدادات قاعدة البيانات من متغيرات البيئة
database_url = os.environ.get('DATABASE_URL', 'sqlite:///sahty.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إنشاء كائن قاعدة البيانات
db = SQLAlchemy(app)

# تعريف النماذج الأساسية
class User(db.Model):
    """نموذج المستخدم الأساسي"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    user_type = db.Column(db.String(20), nullable=False)  # patient, doctor, hospital, admin
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Patient(db.Model):
    """نموذج المريض"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    national_id = db.Column(db.String(14), unique=True)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    blood_type = db.Column(db.String(5))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Doctor(db.Model):
    """نموذج الطبيب"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    license_number = db.Column(db.String(50), unique=True)
    specialization = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    clinic_address = db.Column(db.Text)
    consultation_fee = db.Column(db.Float)
    available_hours = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Hospital(db.Model):
    """نموذج المستشفى"""
    __tablename__ = 'hospitals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    license_number = db.Column(db.String(50), unique=True)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    emergency_phone = db.Column(db.String(20))
    hospital_type = db.Column(db.String(50))  # public, private, specialized
    services = db.Column(db.Text)
    bed_count = db.Column(db.Integer)
    rating = db.Column(db.Float, default=0.0)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    """نموذج المواعيد"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, completed, cancelled
    notes = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    fee = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Medication(db.Model):
    """نموذج الأدوية"""
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    medication_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    instructions = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BloodBank(db.Model):
    """نموذج بنك الدم"""
    __tablename__ = 'blood_bank'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    blood_type = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Float)  # باللتر
    collection_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='available')  # available, reserved, used, expired
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def create_admin_user():
    """إنشاء حساب المدير الافتراضي (المالك)"""
    try:
        # التحقق من وجود المدير
        admin_email = os.environ.get('OWNER_EMAIL', 'Ahmedbahnese@yahoo.com')
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            print(f"حساب المدير موجود بالفعل: {admin_email}")
            return existing_admin
        
        # إنشاء حساب المدير الجديد
        admin_password = os.environ.get('OWNER_PASSWORD', 'Bahnasy123')
        password_hash = generate_password_hash(admin_password)
        
        admin_user = User(
            email=admin_email,
            password_hash=password_hash,
            name=os.environ.get('OWNER_NAME', 'أحمد حامد أحمد بهنسي'),
            phone=os.environ.get('OWNER_PHONE', '01063299450'),
            user_type='admin',
            is_active=True,
            is_verified=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"تم إنشاء حساب المدير بنجاح: {admin_email}")
        print(f"كلمة المرور: {admin_password}")
        
        return admin_user
        
    except Exception as e:
        print(f"خطأ في إنشاء حساب المدير: {e}")
        db.session.rollback()
        return None

def create_sample_data():
    """إنشاء بيانات تجريبية للاختبار"""
    try:
        # إنشاء طبيب تجريبي
        doctor_email = "doctor@sahty.zya.me"
        if not User.query.filter_by(email=doctor_email).first():
            doctor_user = User(
                email=doctor_email,
                password_hash=generate_password_hash("doctor123"),
                name="د. محمد أحمد",
                phone="01234567890",
                user_type='doctor',
                is_active=True,
                is_verified=True
            )
            db.session.add(doctor_user)
            db.session.flush()
            
            doctor_profile = Doctor(
                user_id=doctor_user.id,
                license_number="DOC001",
                specialization="طب عام",
                experience_years=10,
                clinic_address="شارع الجمهورية، الإسكندرية",
                consultation_fee=200.0,
                available_hours="9:00 AM - 5:00 PM",
                is_verified=True
            )
            db.session.add(doctor_profile)
            print("تم إنشاء طبيب تجريبي")
        
        # إنشاء مستشفى تجريبي
        hospital_email = "hospital@sahty.zya.me"
        if not User.query.filter_by(email=hospital_email).first():
            hospital_user = User(
                email=hospital_email,
                password_hash=generate_password_hash("hospital123"),
                name="مستشفى الإسكندرية العام",
                phone="01234567891",
                user_type='hospital',
                is_active=True,
                is_verified=True
            )
            db.session.add(hospital_user)
            db.session.flush()
            
            hospital_profile = Hospital(
                user_id=hospital_user.id,
                name="مستشفى الإسكندرية العام",
                license_number="HOSP001",
                address="شارع الكورنيش، الإسكندرية",
                phone="01234567891",
                emergency_phone="123",
                hospital_type="public",
                services="طوارئ، جراحة، باطنة، أطفال",
                bed_count=200,
                is_verified=True
            )
            db.session.add(hospital_profile)
            print("تم إنشاء مستشفى تجريبي")
        
        # إنشاء مريض تجريبي
        patient_email = "patient@sahty.zya.me"
        if not User.query.filter_by(email=patient_email).first():
            patient_user = User(
                email=patient_email,
                password_hash=generate_password_hash("patient123"),
                name="أحمد محمد",
                phone="01234567892",
                user_type='patient',
                is_active=True,
                is_verified=True
            )
            db.session.add(patient_user)
            db.session.flush()
            
            patient_profile = Patient(
                user_id=patient_user.id,
                national_id="12345678901234",
                birth_date=datetime(1990, 1, 1).date(),
                gender="male",
                blood_type="O+",
                address="شارع السلام، الإسكندرية",
                emergency_contact="01234567893",
                medical_history="لا يوجد",
                allergies="لا يوجد"
            )
            db.session.add(patient_profile)
            print("تم إنشاء مريض تجريبي")
        
        db.session.commit()
        print("تم إنشاء البيانات التجريبية بنجاح")
        
    except Exception as e:
        print(f"خطأ في إنشاء البيانات التجريبية: {e}")
        db.session.rollback()

def init_database():
    """تهيئة قاعدة البيانات"""
    try:
        with app.app_context():
            print("بدء تهيئة قاعدة البيانات...")
            
            # إنشاء الجداول
            db.create_all()
            print("تم إنشاء جداول قاعدة البيانات")
            
            # إنشاء حساب المدير
            admin_user = create_admin_user()
            
            # إنشاء البيانات التجريبية
            create_sample_data()
            
            print("تم إكمال تهيئة قاعدة البيانات بنجاح!")
            print("\n" + "="*50)
            print("معلومات تسجيل الدخول:")
            print("="*50)
            print(f"المدير العام: {os.environ.get('OWNER_EMAIL', 'Ahmedbahnese@yahoo.com')}")
            print(f"كلمة المرور: {os.environ.get('OWNER_PASSWORD', 'Bahnasy123')}")
            print("\nحسابات تجريبية:")
            print("طبيب: doctor@sahty.zya.me / doctor123")
            print("مستشفى: hospital@sahty.zya.me / hospital123")
            print("مريض: patient@sahty.zya.me / patient123")
            print("="*50)
            
    except Exception as e:
        print(f"خطأ في تهيئة قاعدة البيانات: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # تحميل متغيرات البيئة من ملف .env إذا كان موجوداً
    env_file = project_root.parent / '.env'
    if env_file.exists():
        print(f"تحميل متغيرات البيئة من: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    # تهيئة قاعدة البيانات
    success = init_database()
    
    if success:
        print("\n🎉 تم إعداد قاعدة البيانات بنجاح!")
        print("يمكنك الآن تشغيل التطبيق.")
    else:
        print("\n❌ فشل في إعداد قاعدة البيانات!")
        sys.exit(1)

