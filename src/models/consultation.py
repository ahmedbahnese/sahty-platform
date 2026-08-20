from datetime import datetime

from src.models.user import db


class Consultation(db.Model):
    __tablename__ = "consultations"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="requested", index=True)
    scheduled_at = db.Column(db.DateTime)
    meeting_provider = db.Column(db.String(40), nullable=False, default="jitsi")
    meeting_room = db.Column(db.String(180), nullable=False, unique=True)
    meeting_url = db.Column(db.String(500), nullable=False)
    diagnosis = db.Column(db.Text)
    treatment_plan = db.Column(db.Text)
    prescription_data = db.Column(db.JSON)
    referral_type = db.Column(db.String(40))
    referral_note = db.Column(db.Text)
    emergency_requested = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship("ConsultationMessage", backref="consultation", lazy=True, cascade="all, delete-orphan")
    attachments = db.relationship("ConsultationAttachment", backref="consultation", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_private=True):
        data = {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "status": self.status,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "meeting_provider": self.meeting_provider,
            "meeting_room": self.meeting_room,
            "meeting_url": self.meeting_url,
            "diagnosis": self.diagnosis,
            "treatment_plan": self.treatment_plan,
            "referral_type": self.referral_type,
            "referral_note": self.referral_note,
            "emergency_requested": self.emergency_requested,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "attachments": [item.to_dict() for item in self.attachments],
        }
        if include_private:
            data["prescription_data"] = self.prescription_data or {}
            data["messages"] = [item.to_dict() for item in sorted(self.messages, key=lambda row: row.created_at)]
        return data


class ConsultationMessage(db.Model):
    __tablename__ = "consultation_messages"

    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "consultation_id": self.consultation_id,
            "sender_user_id": self.sender_user_id,
            "body": self.body,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ConsultationAttachment(db.Model):
    __tablename__ = "consultation_attachments"

    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(120))
    file_size = db.Column(db.Integer)
    kind = db.Column(db.String(40), nullable=False, default="medical_report")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "consultation_id": self.consultation_id,
            "uploaded_by_user_id": self.uploaded_by_user_id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "kind": self.kind,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
