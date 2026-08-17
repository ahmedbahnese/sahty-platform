# PostgreSQL Production Status

## Policy

SQLite is restricted to development and tests. Production startup rejects any `DATABASE_URL` that is not PostgreSQL. Credentials are read from environment variables or Replit Secrets and are not committed to Git.

## Verified implementation

| Area | Status | Evidence |
|---|---|---|
| PostgreSQL driver | CONFIGURED | `psycopg2-binary` is pinned in `requirements.txt` |
| Production guard | WORKING | `main.py` rejects SQLite when `FLASK_ENV=production` |
| Migrations | WORKING on clean SQLite baseline | Revisions `0001`, `0002`, and `0003` apply successfully to a clean database |
| Foreign keys | PRESENT | SQLAlchemy models define foreign keys across users, patients, doctors, appointments, records, prescriptions, labs, radiology, family, and blood workflows |
| Unique constraints | PRESENT | User identity, doctor license, source identity support, roles, and normalized directory values include uniqueness where applicable |
| Query indexes | ADDED | Revision `0003_production_query_indexes` adds indexes for appointments, medical records, notifications, family, labs, radiology, prescriptions, blood requests, doctors, and directory filters |
| Connection pooling | CONFIGURED | PostgreSQL uses `pool_pre_ping`, `pool_recycle`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, and `DB_POOL_TIMEOUT`; SQLite keeps compatible defaults |
| Backup | IMPLEMENTED | `scripts/backup-postgres.sh` uses custom-format `pg_dump`, refuses SQLite, and writes mode 600 files |
| Restore | IMPLEMENTED | `scripts/restore-postgres.sh` uses `pg_restore`, refuses SQLite, requires `CONFIRM_RESTORE=YES`, and does not print credentials |
| Credential safety | WORKING | No database credentials are stored in source or backup filenames |

## Backup and restore runbook

Set `DATABASE_URL` only in the deployment environment. Run `scripts/backup-postgres.sh` to create a timestamped custom-format dump in a protected backup directory. Store the dump in encrypted, access-controlled object storage with a retention policy and a separate region or provider when required.

For a restore drill, provision an isolated PostgreSQL database, set its `DATABASE_URL`, set `BACKUP_FILE` to a backup file, and run `CONFIRM_RESTORE=YES scripts/restore-postgres.sh`. After restore, run `flask --app main db current`, `flask --app main db upgrade`, `/readyz`, row-count checks, and representative read-only API smoke tests. Never perform a destructive restore against the primary database during a routine test.

## Verification limitation

The sandbox used for this audit had no production `DATABASE_URL` and no PostgreSQL server connection. Therefore migrations, pooling, backup, and restore were syntax- and SQLite-compatibility-tested, and the scripts were verified to reject SQLite, but a real PostgreSQL migration and restore drill remain **NOT VERIFIED** until a managed Replit PostgreSQL connection is supplied through Secrets.
