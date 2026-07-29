"""
نماذج Family Health Manager - إدارة صحة الأسرة
"""

from datetime import datetime
from src.models.user import db


class FamilyGroup(db.Model):
    """مجموعة الأسرة"""
    __tablename__ = 'family_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)           # اسم المجموعة (مثل: عائلة محمد)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = db.relationship('FamilyMember', backref='group', lazy=True, cascade='all, delete-orphan')
    health_goals = db.relationship('FamilyHealthGoal', backref='group', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'owner_user_id': self.owner_user_id,
            'description': self.description,
            'members_count': len(self.members),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FamilyMember(db.Model):
    """أفراد الأسرة"""
    __tablename__ = 'family_members'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('family_groups.id'), nullable=False)

    # ربط بحساب موجود (اختياري)
    linked_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    linked_patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)

    # معلومات أساسية (حتى بدون حساب)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)    # أب، أم، أخ، ابن، زوج، ...
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))                          # male, female
    blood_type = db.Column(db.String(5))
    phone = db.Column(db.String(20))

    # المعلومات الطبية الأساسية
    chronic_diseases = db.Column(db.Text)                      # JSON list
    allergies = db.Column(db.Text)                             # JSON list
    current_medications = db.Column(db.Text)                   # JSON list
    notes = db.Column(db.Text)

    # الحالة
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    health_records = db.relationship('FamilyMemberHealthRecord', backref='member', lazy=True,
                                     cascade='all, delete-orphan')

    def to_dict(self):
        import json as _json
        from datetime import date

        age = None
        if self.date_of_birth:
            age = (date.today() - self.date_of_birth).days // 365

        def _safe_json(val):
            if not val:
                return []
            try:
                return _json.loads(val)
            except Exception:
                return [val]

        return {
            'id': self.id,
            'group_id': self.group_id,
            'linked_user_id': self.linked_user_id,
            'linked_patient_id': self.linked_patient_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'relationship': self.relationship,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': age,
            'gender': self.gender,
            'blood_type': self.blood_type,
            'phone': self.phone,
            'chronic_diseases': _safe_json(self.chronic_diseases),
            'allergies': _safe_json(self.allergies),
            'current_medications': _safe_json(self.current_medications),
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FamilyMemberHealthRecord(db.Model):
    """سجلات صحية لأفراد الأسرة"""
    __tablename__ = 'family_member_health_records'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('family_members.id'), nullable=False)

    record_type = db.Column(db.String(50), nullable=False)     # checkup, vaccination, test, medication, note
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    next_due_date = db.Column(db.Date)                         # موعد المتابعة التالي
    result = db.Column(db.Text)                                # نتيجة الفحص
    doctor_name = db.Column(db.String(200))
    hospital_name = db.Column(db.String(200))
    attachments = db.Column(db.Text)                           # JSON list of file paths

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'record_type': self.record_type,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'result': self.result,
            'doctor_name': self.doctor_name,
            'hospital_name': self.hospital_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FamilyHealthGoal(db.Model):
    """أهداف صحية للأسرة"""
    __tablename__ = 'family_health_goals'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('family_groups.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('family_members.id'), nullable=True)  # null = للأسرة كلها

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')        # active, completed, cancelled
    progress = db.Column(db.Integer, default=0)                # 0-100

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'member_id': self.member_id,
            'title': self.title,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'status': self.status,
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
