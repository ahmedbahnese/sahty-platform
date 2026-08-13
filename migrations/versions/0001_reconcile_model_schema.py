"""Reconcile the imported database with the SQLAlchemy model schema.

This is the first revision in the imported project.  The database shipped with
the project predates Flask-Migrate and contains only a subset of the current
models, so the revision is intentionally safe for both an empty database and
an existing installation:

* missing model tables are created;
* missing columns on legacy tables are added with SQLite batch mode; and
* missing foreign keys are added while rebuilding the affected legacy table.

The model metadata is loaded here only to keep this one-time baseline in sync
with the schema that was audited when the revision was created.  Future schema
changes must be separate, immutable Alembic revisions.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, MetaData, Table, inspect


revision = "0001_reconcile_model_schema"
down_revision = None
branch_labels = None
depends_on = None


def _model_metadata():
    """Return all model tables without importing the Flask application."""
    from src.models.user import db

    # Importing the model modules registers their tables on the shared
    # Flask-SQLAlchemy metadata.  Importing main.py here would execute
    # application startup code and is deliberately avoided.
    for module in (
        "patient",
        "doctor",
        "appointment",
        "medication",
        "blood_bank",
        "hospital",
        "egypt_healthcare",
        "professional",
        "admin",
        "provider",
        "medical_record",
        "prescription",
        "notification",
        "lab_radiology",
        "emergency",
        "family_health",
    ):
        __import__(f"src.models.{module}")
    # Feedback is defined alongside its blueprint rather than in src/models,
    # but it is still a db.Model and must be part of the migration snapshot.
    __import__("src.routes.feedback")
    return db.metadata


def _column_copy(column):
    """Create an unbound column suitable for Alembic batch operations."""
    return Column(
        column.name,
        column.type,
        nullable=column.nullable,
        server_default=column.server_default,
    )


def upgrade():
    bind = op.get_bind()
    metadata = _model_metadata()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # Table.create emits normal SQLAlchemy DDL through the Alembic connection
    # and preserves the model's columns, constraints, and indexes.  It is not
    # db.create_all(): each table is an explicit, versioned migration action.
    for table in metadata.sorted_tables:
        if table.name not in existing_tables:
            table.create(bind=bind, checkfirst=False)

    # Existing project databases contain two legacy tables with columns and
    # foreign keys that were added to the models later.  SQLite cannot add a
    # foreign key in place, so batch mode rebuilds only tables that need drift
    # reconciliation while copying all existing rows.
    inspector = inspect(bind)
    for table_name in sorted(set(metadata.tables) & existing_tables):
        model_table = metadata.tables[table_name]
        existing_columns = {
            column["name"] for column in inspector.get_columns(table_name)
        }
        missing_columns = [
            column
            for column in model_table.columns
            if column.name not in existing_columns
        ]

        existing_fks = {
            (
                tuple(foreign_key["constrained_columns"]),
                foreign_key["referred_table"],
                tuple(foreign_key["referred_columns"]),
            )
            for foreign_key in inspector.get_foreign_keys(table_name)
        }
        missing_fks = [
            foreign_key
            for foreign_key in model_table.foreign_key_constraints
            if (
                tuple(element.parent.name for element in foreign_key.elements),
                foreign_key.referred_table.name,
                tuple(element.column.name for element in foreign_key.elements),
            )
            not in existing_fks
        ]

        if not missing_columns and not missing_fks:
            continue

        reflected = Table(
            table_name,
            MetaData(),
            autoload_with=bind,
        )
        with op.batch_alter_table(
            table_name,
            recreate="always",
            copy_from=reflected,
        ) as batch:
            for column in missing_columns:
                batch.add_column(_column_copy(column))
            for foreign_key in missing_fks:
                local_columns = [
                    element.parent.name
                    for element in foreign_key.elements
                ]
                remote_columns = [
                    element.column.name
                    for element in foreign_key.elements
                ]
                batch.create_foreign_key(
                    "fk_{}_{}_{}".format(
                        table_name,
                        "_".join(local_columns),
                        foreign_key.referred_table,
                    ),
                    foreign_key.referred_table,
                    local_columns,
                    remote_columns,
                )


def downgrade():
    # This baseline may have been applied to a live legacy database.  A
    # destructive downgrade would delete pre-existing application data, so
    # rollback is intentionally explicit rather than silently destructive.
    raise RuntimeError(
        "The initial schema reconciliation is not safely reversible; "
        "restore a database backup instead."
    )