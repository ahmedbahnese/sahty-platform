"""Add per-user daily AI usage counters (free daily quotas).

Revision ID: 0007_ai_daily_usage
Revises: 0006_supabase_rate_limits
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_ai_daily_usage"
down_revision = "0006_supabase_rate_limits"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ai_daily_usage",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("guest_key", sa.String(length=120), nullable=True),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("chat_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("image_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("symptom_count", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "usage_date", name="uq_ai_usage_user_date"),
        sa.UniqueConstraint("guest_key", "usage_date", name="uq_ai_usage_guest_date"),
    )


def downgrade():
    op.drop_table("ai_daily_usage")
