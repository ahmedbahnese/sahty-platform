from datetime import datetime

from src.models.user import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    label_ar = db.Column(db.String(80), nullable=False)


class UserRole(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="ACTIVE")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    activated_at = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint("user_id", "role_id", name="uq_user_role"),)
    role = db.relationship("Role")


class ProfessionalRoleRequest(db.Model):
    __tablename__ = "professional_role_requests"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    requested_role = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="PENDING_APPROVAL")
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    rejection_reason = db.Column(db.Text)
    documents = db.Column(db.JSON)
    credentials = db.Column(db.JSON)
    user = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "requested_role": self.requested_role,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewed_by": self.reviewed_by,
            "rejection_reason": self.rejection_reason,
            "documents": self.documents or {},
            "credentials": self.credentials or {},
            "applicant": {
                "email": self.user.email,
                "username": self.user.username,
            } if self.user else None,
        }


class NurseProfile(db.Model):
    __tablename__ = "nurse_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    full_name = db.Column(db.String(200), nullable=False)
    qualification = db.Column(db.String(200), nullable=False)
    license_number = db.Column(db.String(100), nullable=False)
    credentials = db.Column(db.JSON)
    availability = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "qualification": self.qualification,
            "license_number": self.license_number,
            "credentials": self.credentials or {},
            "availability": self.availability or {},
            "is_active": self.is_active,
        }


NURSING_STATUSES = (
    "PENDING", "UNDER_REVIEW", "ACCEPTED", "REJECTED", "SCHEDULED",
    "IN_PROGRESS", "COMPLETED", "CANCELLED",
)


class NursingServiceRequest(db.Model):
    __tablename__ = "nursing_service_requests"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    nurse_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    requested_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    requester_role = db.Column(db.String(30), nullable=False, default="patient")
    provider_role = db.Column(db.String(30), nullable=False, default="nurse")
    request_type = db.Column(db.String(30), nullable=False, default="home_visit")
    service_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text, nullable=False)
    scheduled_at = db.Column(db.DateTime)
    status = db.Column(db.String(30), nullable=False, default="PENDING")
    rejection_reason = db.Column(db.Text)
    visit_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "nurse_id": self.nurse_id,
            "requested_by_user_id": self.requested_by_user_id,
            "doctor_id": self.doctor_id,
            "requester_role": self.requester_role,
            "provider_role": self.provider_role,
            "request_type": self.request_type,
            "service_type": self.service_type,
            "description": self.description,
            "address": self.address,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "visit_notes": self.visit_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NursingRequestStatusHistory(db.Model):
    __tablename__ = "nursing_request_status_history"
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("nursing_service_requests.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)