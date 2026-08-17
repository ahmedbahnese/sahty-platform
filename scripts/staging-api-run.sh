#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export FLASK_ENV=staging
: "${SESSION_SECRET:?Set SESSION_SECRET in the staging Secrets store}"
: "${DATABASE_URL:?Set the isolated staging PostgreSQL DATABASE_URL}"
: "${RATELIMIT_STORAGE_URI:?Set the shared staging RATELIMIT_STORAGE_URI, for example Redis}"
: "${CORS_ORIGINS:?Set the explicit staging CORS_ORIGINS}"

case "$DATABASE_URL" in
  postgresql://*|postgresql+psycopg2://*|postgres://*) ;;
  *) echo 'Staging requires PostgreSQL; refusing SQLite or another database' >&2; exit 1 ;;
esac

npm run build
flask --app main db upgrade
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers "${WEB_CONCURRENCY:-2}" --access-logfile '-' --error-logfile '-' wsgi:application
