"""Add doctor profile image and clinic locations.

Revision ID: 0005_doctor_profile_locations
Revises: 0004_consultations_and_blood_workflow
"""
from alembic import op
import sqlalchemy as sa

revision = '0005_doctor_profile_locations'
down_revision = '0004_consultations_and_blood_workflow'
branch_labels = None
depends_on = None


def _columns(bind):
    return {column['name'] for column in sa.inspect(bind).get_columns('doctors')}


def upgrade():
    bind = op.get_bind()
    columns = _columns(bind)
    missing = []
    if 'clinic_locations' not in columns:
        missing.append(sa.Column('clinic_locations', sa.JSON(), nullable=True))
    if 'profile_image_url' not in columns:
        missing.append(sa.Column('profile_image_url', sa.String(length=500), nullable=True))
    if missing:
        with op.batch_alter_table('doctors') as batch:
            for column in missing:
                batch.add_column(column)


def downgrade():
    bind = op.get_bind()
    columns = _columns(bind)
    with op.batch_alter_table('doctors') as batch:
        if 'profile_image_url' in columns:
            batch.drop_column('profile_image_url')
        if 'clinic_locations' in columns:
            batch.drop_column('clinic_locations')
