from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
from src.models.user import db

class Medication(db.Model):
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'))   # مصدر الوصفة
    source = db.Column(db.String(30), default='manual')  # manual / prescription / import
    
    # معلومات الدواء
    name = db.Column(db.String(200), nullable=False)
    generic_name = db.Column(db.String(200))
    dosage = db.Column(db.String(100), nullable=False)
    form = db.Column(db.String(50))  # tablet, capsule, syrup, injection, etc.
    
    # تعليمات الاستخدام
    frequency = db.Column(db.String(100), nullable=False)  # once daily, twice daily, etc.
    duration = db.Column(db.String(100))  # 7 days, 2 weeks, etc.
    instructions = db.Column(db.Text)
    
    # مواعيد التناول
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    
    # حالة الدواء
    is_active = db.Column(db.Boolean, default=True)
    is_completed = db.Column(db.Boolean, default=False)
    
    # معلومات إضافية
    side_effects = db.Column(db.Text)
    warnings = db.Column(db.Text)
    interactions = db.Column(db.Text)
    attachment_data = db.Column(db.Text)                      # base64 صورة الروشتة
    
    # إعدادات الإشعارات
    notify_family = db.Column(db.Boolean, default=False)
    notify_doctor_on_missed = db.Column(db.Boolean, default=False)
    missed_dose_threshold = db.Column(db.Integer, default=3)  # عدد الجرعات الفائتة قبل إشعار الطبيب
    
    # تواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    schedules = db.relationship('MedicationSchedule', backref='medication', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('MedicationLog', backref='medication', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'prescription_id': self.prescription_id,
            'source': self.source,
            'name': self.name,
            'generic_name': self.generic_name,
            'dosage': self.dosage,
            'form': self.form,
            'frequency': self.frequency,
            'duration': self.duration,
            'instructions': self.instructions,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'side_effects': self.side_effects,
            'warnings': self.warnings,
            'interactions': self.interactions,
            'attachment_data': self.attachment_data,
            'notify_family': self.notify_family,
            'notify_doctor_on_missed': self.notify_doctor_on_missed,
            'missed_dose_threshold': self.missed_dose_threshold,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MedicationSchedule(db.Model):
    __tablename__ = 'medication_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    
    # جدولة التناول
    time_of_day = db.Column(db.Time, nullable=False)
    days_of_week = db.Column(db.String(20))  # JSON string: [1,2,3,4,5] for weekdays
    
    # تذكيرات
    reminder_enabled = db.Column(db.Boolean, default=True)
    reminder_minutes_before = db.Column(db.Integer, default=15)
    
    # حالة الجدولة
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'medication_id': self.medication_id,
            'time_of_day': self.time_of_day.isoformat() if self.time_of_day else None,
            'days_of_week': self.days_of_week,
            'reminder_enabled': self.reminder_enabled,
            'reminder_minutes_before': self.reminder_minutes_before,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MedicationLog(db.Model):
    __tablename__ = 'medication_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # سجل التناول
    scheduled_time = db.Column(db.DateTime, nullable=False)
    actual_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)  # taken, missed, skipped, delayed
    
    # تفاصيل إضافية
    notes = db.Column(db.Text)
    side_effects_experienced = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'medication_id': self.medication_id,
            'patient_id': self.patient_id,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'actual_time': self.actual_time.isoformat() if self.actual_time else None,
            'status': self.status,
            'notes': self.notes,
            'side_effects_experienced': self.side_effects_experienced,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PharmacyOrder(db.Model):
    """طلبات أدوية المريض من الصيدلية."""
    __tablename__ = 'pharmacy_orders'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    # نوع الطلب: paper_prescription / manual / from_prescription
    order_type = db.Column(db.String(30), nullable=False, default='manual')

    # الوصفة الورقية (رفع صورة)
    prescription_image_path = db.Column(db.String(500))
    prescription_image_name = db.Column(db.String(200))

    # الوصفة من المنصة (from_prescription)
    source_prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'))

    # الأدوية المدخلة يدوياً أو المعدّلة
    # JSON: [{"name":"...", "dosage":"...", "quantity":"...", "notes":"..."}]
    medications_json = db.Column(db.Text, default='[]')

    # الصيدلية المفضّلة
    preferred_pharmacy_name = db.Column(db.String(200))
    preferred_pharmacy_id   = db.Column(db.Integer)   # قد يُربط بجدول مزودين مستقبلاً

    # ملاحظات عامة
    notes = db.Column(db.Text)

    # سير العمل: pending → confirmed → dispensed | cancelled
    status = db.Column(db.String(30), default='pending')
    dispensed_at = db.Column(db.DateTime)
    cancelled_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def medications(self):
        import json as _json
        try:
            return _json.loads(self.medications_json or '[]')
        except Exception:
            return []

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'order_type': self.order_type,
            'prescription_image_path': self.prescription_image_path,
            'prescription_image_name': self.prescription_image_name,
            'source_prescription_id': self.source_prescription_id,
            'medications': self.medications,
            'preferred_pharmacy_name': self.preferred_pharmacy_name,
            'preferred_pharmacy_id': self.preferred_pharmacy_id,
            'notes': self.notes,
            'status': self.status,
            'dispensed_at': self.dispensed_at.isoformat() if self.dispensed_at else None,
            'cancelled_reason': self.cancelled_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class DrugDatabase(db.Model):
    __tablename__ = 'drug_database'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات الدواء
    trade_name = db.Column(db.String(200), nullable=False)
    generic_name = db.Column(db.String(200), nullable=False)
    manufacturer = db.Column(db.String(200))
    
    # التصنيف
    category = db.Column(db.String(100))
    therapeutic_class = db.Column(db.String(100))
    
    # معلومات الجرعة
    available_strengths = db.Column(db.Text)  # JSON string
    dosage_forms = db.Column(db.Text)  # JSON string
    
    # معلومات السلامة
    contraindications = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    drug_interactions = db.Column(db.Text)
    warnings = db.Column(db.Text)
    
    # معلومات إضافية
    pregnancy_category = db.Column(db.String(10))
    storage_conditions = db.Column(db.Text)
    
    # السعر والتوفر
    average_price = db.Column(db.Float)
    is_available = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trade_name': self.trade_name,
            'generic_name': self.generic_name,
            'manufacturer': self.manufacturer,
            'category': self.category,
            'therapeutic_class': self.therapeutic_class,
            'available_strengths': self.available_strengths,
            'dosage_forms': self.dosage_forms,
            'contraindications': self.contraindications,
            'side_effects': self.side_effects,
            'drug_interactions': self.drug_interactions,
            'warnings': self.warnings,
            'pregnancy_category': self.pregnancy_category,
            'storage_conditions': self.storage_conditions,
            'average_price': self.average_price,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
