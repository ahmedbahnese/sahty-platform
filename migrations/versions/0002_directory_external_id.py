"""Add source identity to imported healthcare directory rows.

Revision ID: 0002_directory_external_id
Revises: 0001_reconcile_model_schema
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_directory_external_id"
down_revision = "0001_reconcile_model_schema"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "healthcare_directory_records" not in tables:
        return
    columns = {column["name"] for column in inspector.get_columns("healthcare_directory_records")}
    if "external_id" not in columns:
        op.add_column(
            "healthcare_directory_records",
            sa.Column("external_id", sa.String(length=120), nullable=True),
        )
        op.create_index(
            "ix_healthcare_directory_records_external_id",
            "healthcare_directory_records",
            ["external_id"],
            unique=False,
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "healthcare_directory_records" not in tables:
        return
    columns = {column["name"] for column in inspector.get_columns("healthcare_directory_records")}
    if "external_id" in columns:
        op.drop_index(
            "ix_healthcare_directory_records_external_id",
            table_name="healthcare_directory_records",
        )
        op.drop_column("healthcare_directory_records", "external_id")
