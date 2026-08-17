#!/usr/bin/env bash
set -euo pipefail

missing=0
for name in SESSION_SECRET DATABASE_URL; do
  if [[ -z "${!name:-}" ]]; then
    printf 'MISSING %s: set this variable in Replit Secrets\n' "$name" >&2
    missing=1
  else
    printf 'PRESENT %s\n' "$name"
  fi
done

if (( missing )); then
  exit 1
fi

if [[ "${FLASK_ENV:-production}" != "production" ]]; then
  printf 'WARNING FLASK_ENV=%s; this script validates production configuration only\n' "${FLASK_ENV:-unset}" >&2
fi

case "$DATABASE_URL" in
  postgresql://*|postgres://*)
    printf 'DATABASE_URL_SCHEME=postgresql\n'
    ;;
  *)
    printf 'INVALID DATABASE_URL: production requires PostgreSQL (postgresql:// or postgres://)\n' >&2
    exit 1
    ;;
esac

printf 'Production configuration shape is valid; secret values were not printed.\n'
