from datetime import datetime

from src.models.user import db


PROVIDER_ROLES = {
    'pharmacy': 'صيدلية',
    'lab': 'معمل',
    'radiology_center': 'مركز أشعة',
    'hospital': 'مستشفى',
    'nurse': 'ممرض',
}


class ProviderRegistration(db.Model):
    """بيانات الجهات الطبية التي تنتظر اعتماد الإدارة."""

    __tablename__ = 'provider_registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    provider_type = db.Column(db.String(40), nullable=False)
    legal_name = db.Column(db.String(200), nullable=False)
    license_number = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False, default='')
    details = db.Column(db.JSON)
    status = db.Column(db.String(20), nullable=False, default='pending')
    review_note = db.Column(db.Text)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('provider_registration', uselist=False))
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider_type': self.provider_type,
            'provider_label': PROVIDER_ROLES.get(self.provider_type, self.provider_type),
            'legal_name': self.legal_name,
            'license_number': self.license_number,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'details': self.details or {},
            'status': self.status,
            'review_note': self.review_note,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': {
                'id': self.user.id,
                'email': self.user.email,
                'username': self.user.username,
                'is_active': self.user.is_active,
            } if self.user else None,
        }