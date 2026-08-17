# Staging and Promotion Guide

## Environment flow

```text
Development → CI → Testing → Staging → Acceptance → Production
```

Development is for local implementation with SQLite and local services. CI runs deterministic lint, build, backend tests, and security regression tests. Testing uses isolated databases and repeatable API smoke tests. Staging is the first production-like environment and must use an isolated PostgreSQL database, a shared Redis-compatible rate-limit store, explicit CORS origins, HTTPS at the edge, persistent storage, and secrets from the environment. Acceptance runs business workflows against Staging. Production promotion is blocked unless Acceptance is green.

## Staging startup

Use `scripts/staging-api-run.sh`. It sets `FLASK_ENV=staging`, refuses SQLite, requires `SESSION_SECRET`, `DATABASE_URL`, `RATELIMIT_STORAGE_URI`, and `CORS_ORIGINS`, builds the React client, runs Alembic migrations, and starts the WSGI application through Gunicorn. Staging and Production now share the PostgreSQL, rate-limit, CORS, HSTS, and security-guard behavior in `main.py`.

## Isolation requirements

The Staging PostgreSQL database must be a separate database or instance from Production. Staging secrets must be separate from Production secrets. Staging data must not contain real patient health data unless a lawful, documented de-identification and data-processing procedure exists. Backups must identify their environment and must never be restored across environments without an explicit approval and a verified target.

## Promotion gates

| Gate | Required evidence |
|---|---|
| CI | lint, Vite build, backend suite, security suite, shell syntax checks |
| Testing | migrations from a clean database, API contract tests, E2E smoke workflow, ownership regression |
| Staging startup | PostgreSQL migration succeeds, Gunicorn starts, `/healthz` is 200, `/readyz` is 200, explicit CORS and HTTPS headers are present |
| Acceptance | login, role authorization, real database write/read, appointment state transition, medical workflow smoke tests, backup/restore evidence |
| Production | approved Acceptance report, rollback plan, backup freshness, monitoring/logging, secrets review, and no open critical/high security findings |

## Current limitation

The local sandbox has no connected staging PostgreSQL, Redis, persistent Storage, or public HTTPS deployment. Therefore the scripts and guards are implemented and locally syntax-checked, but Staging and Acceptance cannot be marked passed until the isolated Replit services are configured and exercised.
