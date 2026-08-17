# Backend Production Status

## Request path

```text
Internet
  -> HTTPS/Replit proxy
  -> Gunicorn WSGI (`wsgi:application`)
  -> Flask application
  -> PostgreSQL / Storage / server-side external APIs
```

## Verified components

| Component | Status | Evidence |
|---|---|---|
| WSGI | WORKING | `wsgi.py` exports `application`; import check passed |
| Gunicorn | WORKING | Gunicorn 22.0.0 installed and pinned in `requirements.txt` |
| Replit start script | WORKING | `scripts/replit-api-run.sh` validates `SESSION_SECRET`, builds frontend, upgrades migrations, and starts Gunicorn on `0.0.0.0:$PORT` |
| Production DB guard | WORKING | production startup rejects SQLite and requires PostgreSQL URL |
| Environment variables | WORKING | `SESSION_SECRET`, `DATABASE_URL`, `CORS_ORIGINS`, `PORT`, `FLASK_ENV`, `LOG_LEVEL` are read from environment; values are not committed |
| Logging | WORKING | configurable `LOG_LEVEL` and structured timestamped application logging |
| Error handling | WORKING | API HTTP errors return JSON; unexpected errors are logged server-side and return a generic message |
| Health | WORKING | `/healthz` liveness, `/api/health` database health |
| Readiness | WORKING | `/readyz` executes `SELECT 1` and returns 503 when DB is unavailable |
| Authentication | WORKING on test suite | JWT/session routes and invalid-input regression tests pass |
| Authorization | WORKING on test suite | role and cross-patient isolation regression tests pass |
| CORS | WORKING | explicit `CORS_ORIGINS` plus development origins and configured public domain |
| Migrations | WORKING on SQLite test DB | clean database migration and directory migration passed |
| API routing | WORKING | unknown `/api/*` paths now return JSON 404 instead of SPA HTTP 200 |

## Remaining production verification

A real Replit deployment still needs a managed PostgreSQL `DATABASE_URL`, production `SESSION_SECRET`, configured `CORS_ORIGINS`, and a public smoke test against `/healthz`, `/readyz`, authentication, and a protected endpoint. Medical file uploads currently use local filesystem storage and require an external persistent Storage provider before production acceptance.
