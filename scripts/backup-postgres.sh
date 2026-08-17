#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?Set DATABASE_URL to the managed PostgreSQL connection string}"
: "${BACKUP_DIR:=backups}"

case "$DATABASE_URL" in
  postgresql://*|postgresql+psycopg2://*) ;;
  *) echo 'Refusing backup: DATABASE_URL must be PostgreSQL' >&2; exit 1 ;;
esac

command -v pg_dump >/dev/null 2>&1 || { echo 'pg_dump is required' >&2; exit 1; }
mkdir -p "$BACKUP_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
output="$BACKUP_DIR/sehaty_${timestamp}.dump"
pg_dump --format=custom --no-owner --no-acl --file="$output" "$DATABASE_URL"
chmod 600 "$output"
printf 'BACKUP_FILE=%s\n' "$output"
