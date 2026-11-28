"""Add a shared PostgreSQL rate-limit counter for serverless deployments.

Revision ID: 0006_supabase_rate_limits
Revises: 0005_doctor_profile_locations
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_supabase_rate_limits"
down_revision = "0005_doctor_profile_locations"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "request_rate_limits",
        sa.Column("key", sa.String(length=80), primary_key=True),
        sa.Column("window_id", sa.BigInteger(), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("request_rate_limits")
