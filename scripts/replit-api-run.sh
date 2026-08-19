#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
: "${SESSION_SECRET:?Set SESSION_SECRET in Replit Secrets before starting the API}"
: "${DATABASE_URL:?Set DATABASE_URL to the Replit PostgreSQL connection string}"
export PORT="${PORT:-5000}"
export FLASK_ENV="${FLASK_ENV:-production}"
if [ "$FLASK_ENV" = "production" ]; then
  : "${CORS_ORIGINS:?Set CORS_ORIGINS to the public Replit origin}"
else
  export CORS_ORIGINS="${CORS_ORIGINS:-*}"
fi

if [ -z "${RATELIMIT_STORAGE_URI:-}" ]; then
  if [ "${ALLOW_INSECURE_MEMORY_RATE_LIMITER:-no}" = "yes" ] && [ "$FLASK_ENV" != "production" ]; then
    export RATELIMIT_STORAGE_URI="memory://"
    echo 'WARNING: using an in-memory rate limiter for temporary non-production preview only' >&2
  else
    echo 'Set RATELIMIT_STORAGE_URI to a shared Redis-compatible store; for temporary preview only set ALLOW_INSECURE_MEMORY_RATE_LIMITER=yes and FLASK_ENV=development' >&2
    exit 1
  fi
fi

npm run build
flask --app main db upgrade

DIRECTORY_CSV_PATH="${DIRECTORY_CSV_PATH:-data/processed/egypt_directory_hdx_target.csv}"
if [ -f "$DIRECTORY_CSV_PATH" ]; then
  python3 scripts/import_directory_csv.py "$DIRECTORY_CSV_PATH"
else
  echo "Directory CSV not found at $DIRECTORY_CSV_PATH; database migrations still completed" >&2
fi

exec gunicorn --bind "0.0.0.0:${PORT}" --workers "${WEB_CONCURRENCY:-2}" --access-logfile '-' --error-logfile '-' wsgi:application
