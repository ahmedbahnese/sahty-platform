from datetime import datetime

from src.models.user import db


class RequestRateLimit(db.Model):
    """One counter per hashed client and fixed rate-limit window."""

    __tablename__ = "request_rate_limits"

    key = db.Column(db.String(80), primary_key=True)
    window_id = db.Column(db.BigInteger, nullable=False)
    request_count = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
