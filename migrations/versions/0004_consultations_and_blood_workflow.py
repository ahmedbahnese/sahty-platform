"""Add consultations and blood request workflow fields.

Revision ID: 0004_consultations_and_blood_workflow
Revises: 0003_production_query_indexes
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_consultations_and_blood_workflow"
down_revision = "0003_production_query_indexes"
branch_labels = None
depends_on = None


def _columns(bind, table_name):
    return {column["name"] for column in sa.inspect(bind).get_columns(table_name)}


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("consultations"):
        op.create_table(
            "consultations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("patient_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False, server_default="requested"),
            sa.Column("scheduled_at", sa.DateTime()),
            sa.Column("meeting_provider", sa.String(length=40), nullable=False, server_default="jitsi"),
            sa.Column("meeting_room", sa.String(length=180), nullable=False, unique=True),
            sa.Column("meeting_url", sa.String(length=500), nullable=False),
            sa.Column("diagnosis", sa.Text()),
            sa.Column("treatment_plan", sa.Text()),
            sa.Column("prescription_data", sa.JSON()),
            sa.Column("referral_type", sa.String(length=40)),
            sa.Column("referral_note", sa.Text()),
            sa.Column("emergency_requested", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    inspector = sa.inspect(bind)
    if not any(index["name"] == "ix_consultations_patient_id" for index in inspector.get_indexes("consultations")):
        op.create_index("ix_consultations_patient_id", "consultations", ["patient_id"])
    if not any(index["name"] == "ix_consultations_doctor_id" for index in inspector.get_indexes("consultations")):
        op.create_index("ix_consultations_doctor_id", "consultations", ["doctor_id"])
    if not any(index["name"] == "ix_consultations_status" for index in inspector.get_indexes("consultations")):
        op.create_index("ix_consultations_status", "consultations", ["status"])

    inspector = sa.inspect(bind)
    if not inspector.has_table("consultation_messages"):
        op.create_table(
            "consultation_messages",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("consultation_id", sa.Integer(), sa.ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False),
            sa.Column("sender_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    inspector = sa.inspect(bind)
    if not any(index["name"] == "ix_consultation_messages_consultation_id" for index in inspector.get_indexes("consultation_messages")):
        op.create_index("ix_consultation_messages_consultation_id", "consultation_messages", ["consultation_id"])
    if not any(index["name"] == "ix_consultation_messages_sender_user_id" for index in inspector.get_indexes("consultation_messages")):
        op.create_index("ix_consultation_messages_sender_user_id", "consultation_messages", ["sender_user_id"])

    inspector = sa.inspect(bind)
    if not inspector.has_table("consultation_attachments"):
        op.create_table(
            "consultation_attachments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("consultation_id", sa.Integer(), sa.ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False),
            sa.Column("uploaded_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("file_path", sa.String(length=500), nullable=False),
            sa.Column("file_name", sa.String(length=255), nullable=False),
            sa.Column("mime_type", sa.String(length=120)),
            sa.Column("file_size", sa.Integer()),
            sa.Column("kind", sa.String(length=40), nullable=False, server_default="medical_report"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    inspector = sa.inspect(bind)
    if not any(index["name"] == "ix_consultation_attachments_consultation_id" for index in inspector.get_indexes("consultation_attachments")):
        op.create_index("ix_consultation_attachments_consultation_id", "consultation_attachments", ["consultation_id"])

    nursing_columns = _columns(bind, "nursing_service_requests")
    nursing_missing = []
    for name, column in (
        ("requested_by_user_id", sa.Column("requested_by_user_id", sa.Integer(), sa.ForeignKey("users.id"))),
        ("doctor_id", sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("users.id"))),
        ("requester_role", sa.Column("requester_role", sa.String(length=30), nullable=False, server_default="patient")),
        ("provider_role", sa.Column("provider_role", sa.String(length=30), nullable=False, server_default="nurse")),
        ("request_type", sa.Column("request_type", sa.String(length=30), nullable=False, server_default="home_visit")),
    ):
        if name not in nursing_columns:
            nursing_missing.append(column)
    if nursing_missing:
        with op.batch_alter_table("nursing_service_requests") as batch:
            for column in nursing_missing:
                batch.add_column(column)

    blood_columns = _columns(bind, "blood_requests")
    blood_missing = []
    for name, column in (
        ("component_type", sa.Column("component_type", sa.String(length=30), nullable=False, server_default="whole_blood")),
        ("is_irradiated", sa.Column("is_irradiated", sa.Boolean(), nullable=False, server_default=sa.false())),
        ("transfusion_request_file_path", sa.Column("transfusion_request_file_path", sa.String(length=500))),
        ("transfusion_request_file_name", sa.Column("transfusion_request_file_name", sa.String(length=200))),
        ("document_status", sa.Column("document_status", sa.String(length=30), nullable=False, server_default="document_required")),
        ("forwarded_to_centers_at", sa.Column("forwarded_to_centers_at", sa.DateTime())),
        ("forwarded_by_user_id", sa.Column("forwarded_by_user_id", sa.Integer(), sa.ForeignKey("users.id"))),
    ):
        if name not in blood_columns:
            blood_missing.append(column)
    if blood_missing:
        with op.batch_alter_table("blood_requests") as batch:
            for column in blood_missing:
                batch.add_column(column)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("blood_requests"):
        existing = _columns(bind, "blood_requests")
        with op.batch_alter_table("blood_requests") as batch:
            for name in ("forwarded_by_user_id", "forwarded_to_centers_at", "document_status", "transfusion_request_file_name", "transfusion_request_file_path", "is_irradiated", "component_type"):
                if name in existing:
                    batch.drop_column(name)
    if inspector.has_table("nursing_service_requests"):
        existing = _columns(bind, "nursing_service_requests")
        with op.batch_alter_table("nursing_service_requests") as batch:
            for name in ("request_type", "provider_role", "requester_role", "doctor_id", "requested_by_user_id"):
                if name in existing:
                    batch.drop_column(name)
    for index_name, table_name in (
        ("ix_consultation_attachments_consultation_id", "consultation_attachments"),
        ("ix_consultation_messages_sender_user_id", "consultation_messages"),
        ("ix_consultation_messages_consultation_id", "consultation_messages"),
        ("ix_consultations_status", "consultations"),
        ("ix_consultations_doctor_id", "consultations"),
        ("ix_consultations_patient_id", "consultations"),
    ):
        if inspector.has_table(table_name):
            op.drop_index(index_name, table_name=table_name)
    for table_name in ("consultation_attachments", "consultation_messages", "consultations"):
        if inspector.has_table(table_name):
            op.drop_table(table_name)
