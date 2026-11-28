"""Per-user daily AI usage counters (free daily quotas, reset at Cairo midnight)."""

from src.models.user import db


class AIDailyUsage(db.Model):
    __tablename__ = "ai_daily_usage"

    id = db.Column(db.Integer, primary_key=True)
    # Exactly one of user_id / guest_key is set: logged-in users are counted
    # by user_id, guests by an IP-based guest_key.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    guest_key = db.Column(db.String(120), nullable=True)
    usage_date = db.Column(db.Date, nullable=False)
    chat_count = db.Column(db.Integer, nullable=False, default=0)
    image_count = db.Column(db.Integer, nullable=False, default=0)
    symptom_count = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        db.UniqueConstraint("user_id", "usage_date", name="uq_ai_usage_user_date"),
        db.UniqueConstraint("guest_key", "usage_date", name="uq_ai_usage_guest_date"),
    )
