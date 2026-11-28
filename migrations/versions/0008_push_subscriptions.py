"""Add Web Push subscriptions for emergency notifications.

Revision ID: 0008_push_subscriptions
Revises: 0007_ai_daily_usage
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_push_subscriptions"
down_revision = "0007_ai_daily_usage"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("endpoint", sa.Text(), nullable=False, unique=True),
        sa.Column("p256dh", sa.String(length=200), nullable=False),
        sa.Column("auth", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table("push_subscriptions")
