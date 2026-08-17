#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
: "${SESSION_SECRET:?Set SESSION_SECRET in Replit Secrets before starting the API}"
export PORT="${PORT:-5000}"
export FLASK_ENV="${FLASK_ENV:-production}"

npm run build
flask --app main db upgrade
exec gunicorn --bind "0.0.0.0:${PORT}" wsgi:application
