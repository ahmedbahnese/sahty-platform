#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?Set DATABASE_URL to the managed PostgreSQL connection string}"
: "${BACKUP_FILE:?Set BACKUP_FILE to a pg_dump custom-format file}"
: "${CONFIRM_RESTORE:?Set CONFIRM_RESTORE=YES to authorize a destructive restore}"

case "$DATABASE_URL" in
  postgresql://*|postgresql+psycopg2://*) ;;
  *) echo 'Refusing restore: DATABASE_URL must be PostgreSQL' >&2; exit 1 ;;
esac
[ "$CONFIRM_RESTORE" = YES ] || { echo 'Refusing restore: set CONFIRM_RESTORE=YES' >&2; exit 1; }
[ -s "$BACKUP_FILE" ] || { echo 'Backup file is missing or empty' >&2; exit 1; }
command -v pg_restore >/dev/null 2>&1 || { echo 'pg_restore is required' >&2; exit 1; }

pg_restore --clean --if-exists --no-owner --no-acl --dbname="$DATABASE_URL" "$BACKUP_FILE"
printf 'RESTORE_COMPLETED=yes\n'
