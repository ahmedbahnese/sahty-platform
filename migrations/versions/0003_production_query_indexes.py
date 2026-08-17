"""Add production query indexes for common API access paths.

Revision ID: 0003_production_query_indexes
Revises: 0002_directory_external_id
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_production_query_indexes"
down_revision = "0002_directory_external_id"
branch_labels = None
depends_on = None

INDEXES = {
    "ix_appointments_patient_id": ("appointments", ["patient_id"]),
    "ix_appointments_doctor_id": ("appointments", ["doctor_id"]),
    "ix_appointments_date": ("appointments", ["appointment_date"]),
    "ix_medical_records_patient_id": ("medical_records", ["patient_id"]),
    "ix_medical_records_doctor_id": ("medical_records", ["doctor_id"]),
    "ix_notifications_user_read": ("notifications", ["user_id", "is_read"]),
    "ix_family_members_group_id": ("family_members", ["family_group_id"]),
    "ix_lab_requests_patient_id": ("lab_requests", ["patient_id"]),
    "ix_radiology_requests_patient_id": ("radiology_requests", ["patient_id"]),
    "ix_prescriptions_patient_id": ("prescriptions", ["patient_id"]),
    "ix_prescriptions_doctor_id": ("prescriptions", ["doctor_id"]),
    "ix_blood_requests_patient_id": ("blood_requests", ["patient_id"]),
    "ix_blood_requests_status": ("blood_requests", ["status"]),
    "ix_doctors_specialization": ("doctors", ["specialization"]),
    "ix_directory_governorate_type": (
        "healthcare_directory_records",
        ["governorate", "facility_type"],
    ),
}


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    for index_name, (table_name, columns) in INDEXES.items():
        if table_name not in tables:
            continue
        available = {column["name"] for column in inspector.get_columns(table_name)}
        if not set(columns).issubset(available):
            continue
        existing = {index.get("name") for index in inspector.get_indexes(table_name)}
        if index_name not in existing:
            op.create_index(index_name, table_name, columns, unique=False)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    for index_name, (table_name, _columns) in INDEXES.items():
        if table_name in tables:
            existing = {index.get("name") for index in inspector.get_indexes(table_name)}
            if index_name in existing:
                op.drop_index(index_name, table_name=table_name)
