# Sehaty Operations Runbook

## Runtime signals

The application exposes `/healthz` for process health and `/readyz` for dependency readiness. Readiness executes a database probe and returns a failure status when PostgreSQL is unavailable. Gunicorn writes access and error logs to stdout/stderr so the deployment platform can collect them. Flask logs unhandled exceptions without returning stack traces or health data to users.

| Signal | Source | Alert condition |
|---|---|---|
| Liveness | `/healthz` | Any non-200 response or repeated timeout |
| Readiness | `/readyz` | Any 503, database connection failure, or migration mismatch |
| HTTP errors | Reverse proxy/Gunicorn logs | 5xx rate above the agreed threshold |
| Latency | Reverse proxy access logs/APM | p95 above the agreed endpoint budget |
| Authentication abuse | Rate-limit logs and application logs | Repeated login failures or token abuse |
| Database | PostgreSQL provider metrics | Connection exhaustion, storage, replication, or backup failure |
| Storage | Storage provider metrics | Upload failures, quota, or durability alerts |
| Mobile crashes | Sentry/Crashlytics or equivalent | New release crash-free rate below the release threshold |

The actual thresholds and notification destinations are deployment-specific and must be configured in the selected monitoring provider; they are not hard-coded into the application or committed as secrets.

## Backup and restore

Use `scripts/backup-postgres.sh` with a PostgreSQL `DATABASE_URL`. Store the custom-format dump in encrypted durable storage with a retention policy and environment label. Use `scripts/restore-postgres.sh` only against a separate restore target with `CONFIRM_RESTORE=YES`. A restore test is an acceptance gate: restore into an isolated database, run migrations if required, call `/readyz`, and execute read/write API smoke tests. Production backups must never be tested by destructive restore in place.

## Rollback

The application artifact is immutable and identified by its Git commit or container digest. To roll back, stop promotion, select the last accepted artifact, deploy it to the same runtime configuration, confirm `/healthz` and `/readyz`, then run the critical API smoke suite. Database migrations must be backward-compatible where rollback is required; destructive schema changes require an expand/contract migration plan and a backup before deployment.

## CI/CD promotion path

```text
Git Push → Automated Tests → Build → Security Checks → Staging → Acceptance → Production
```

The repository workflow runs deterministic Python tests, ESLint, Vite build, shell syntax checks, and a Dockerfile/Compose configuration check when Docker is available. Deployment to Staging and Production is intentionally environment-specific: the hosting provider must connect the workflow to its own deployment API or runner and supply secrets through a protected environment. No provider token is stored in the repository.

## Incident response

For an incident, first check `/readyz`, recent deploy commit, database provider status, rate-limit store, and storage provider status. If the release is implicated, use the rollback procedure and preserve logs. If data integrity is implicated, stop destructive writes, take a backup, and restore only to an isolated target for investigation. Security incidents require credential rotation, token/session invalidation, access-log preservation, and a documented post-incident review.
