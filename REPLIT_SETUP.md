# Replit setup for Sehaty

## Required Secrets

Configure these in the Replit Secrets panel; never commit their values:

```text
DATABASE_URL=the-Replit-PostgreSQL-connection-string
SESSION_SECRET=a-long-random-secret
CORS_ORIGINS=https://your-replit-domain
RATELIMIT_STORAGE_URI=redis://your-shared-redis/0
```

`PORT` is supplied by Replit and must not be hard-coded. The startup script binds Gunicorn to `0.0.0.0:$PORT`.

## Startup command

Use:

```bash
bash scripts/replit-api-run.sh
```

The script builds React, runs all migrations, imports the tracked verified directory CSV from `data/processed/egypt_directory_hdx_target.csv` using idempotent upsert, and starts Gunicorn. Set `DIRECTORY_CSV_PATH` only when using another reviewed data snapshot.

## Temporary preview only

If Redis is not available yet, a non-production preview may be started with:

```text
FLASK_ENV=development
ALLOW_INSECURE_MEMORY_RATE_LIMITER=yes
DATABASE_URL=...
SESSION_SECRET=...
```

This is not acceptable for Production or Staging. Production requires PostgreSQL and a shared Redis-compatible rate-limit store.

## Verification

After startup, check:

```text
https://your-replit-domain/healthz
https://your-replit-domain/readyz
https://your-replit-domain/api/facilities
```

`/readyz` must be successful before diagnosing missing directory data. `/api/facilities` should return the imported records and support governorate and facility-type filters.

## Common failure meanings

| Symptom | Likely cause |
|---|---|
| Server does not start | Missing `DATABASE_URL`, `SESSION_SECRET`, or production `RATELIMIT_STORAGE_URI` |
| Readiness is 503 | PostgreSQL connection string, database availability, or migrations |
| API is unreachable | Wrong Replit Run command, incorrect port binding, or process exited during startup |
| Empty facilities | Importer did not run, CSV path is absent, or the API filter does not match normalized types |
| Browser CORS error | `CORS_ORIGINS` does not contain the actual public Replit origin |
