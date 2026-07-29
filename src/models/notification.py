"""
نموذج الإشعارات داخل التطبيق.
"""
from datetime import datetime
from src.models.user import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    title          = db.Column(db.String(200), nullable=False)
    message        = db.Column(db.Text, nullable=False)
    # appointment | prescription | system
    type           = db.Column(db.String(50), default='system')
    reference_id   = db.Column(db.Integer)
    reference_type = db.Column(db.String(50))   # appointment | prescription

    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'user_id':        self.user_id,
            'title':          self.title,
            'message':        self.message,
            'type':           self.type,
            'reference_id':   self.reference_id,
            'reference_type': self.reference_type,
            'is_read':        self.is_read,
            'created_at':     self.created_at.isoformat() if self.created_at else None,
        }
