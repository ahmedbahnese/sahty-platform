# Sehaty (صحتي) — Deployment Guide

## Overview

Sehaty is a full-stack application:
- **Backend**: Flask (Python 3.12) — port 5001
- **Frontend**: React + Vite — port 5000 (dev) / static build (production)
- **Database**: SQLite (development) · PostgreSQL (production)

---

## Environment Variables / Secrets

| Variable | Required | Description |
|----------|----------|-------------|
| `SESSION_SECRET` | ✅ | Flask session secret key (also used as JWT fallback) |
| `JWT_SECRET_KEY` | Recommended | Dedicated JWT signing key (more secure than sharing SESSION_SECRET) |
| `DATABASE_URL` | Production | PostgreSQL connection string, e.g. `postgresql://user:pass@host/dbname` |
| `FLASK_ENV` | Recommended | Set to `development` to enable debug mode; defaults to `production` |
| `OPENAI_API_KEY` | For AI features | Required for AI chat, symptom checker, image analysis |
| `PORT` | Optional | Backend port (defaults to 5001) |

> ⚠️ Never commit secrets. Use Replit Secrets (or your provider's secret manager) to inject these at runtime.

---

## Local Development

### 1. Install dependencies

**Backend (Python)**
```bash
pip install flask flask-cors flask-sqlalchemy flask-migrate flask-limiter \
    werkzeug pyjwt bcrypt cryptography openai gunicorn psycopg2-binary
```

**Frontend (Node.js)**
```bash
npm install
```

### 2. Configure secrets

Set the required environment variables in your shell or `.env`:
```bash
export SESSION_SECRET="your-very-long-random-secret"
export FLASK_ENV=development
```

### 3. Start services

In two terminals (or via Replit workflows):
```bash
# Backend
python main.py          # runs on port 5001

# Frontend
npm run dev             # runs on port 5000
```

The frontend Vite dev server proxies `/api/*` requests to `http://localhost:5001` (see `vite.config.js`).

---

## Database Setup

### SQLite (default — development only)
The database is created automatically at `src/database/app.db` on first startup.  
An admin user is bootstrapped if none exists (`admin@sehaty.com` / `Admin123!`).  
**Change the admin password immediately after first login.**

### PostgreSQL (production)
```bash
export DATABASE_URL=postgresql://sehaty:password@db.host.com:5432/sehaty_prod
python main.py            # or gunicorn
```

The app detects `DATABASE_URL` and switches to PostgreSQL automatically.

### Migrations
```bash
flask db init      # once only
flask db migrate -m "description"
flask db upgrade
```

---

## Production Deployment on Replit

1. **Set secrets** in the Replit Secrets panel:
   - `SESSION_SECRET` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
   - `DATABASE_URL` (optional — use Replit PostgreSQL or external DB)
   - `OPENAI_API_KEY` (if using AI features)

2. **Configure workflows** (already set up in `.replit`):
   - **Flask API**: `python main.py`
   - **Start application**: `npm run dev` (or `npm run build && npm run preview` for a production build)

3. **Click Publish / Deploy** in Replit. The platform will:
   - Inject secrets into the production environment
   - Start both workflows
   - Expose the app on your `.replit.app` domain

4. **Switch to PostgreSQL** for production persistence:
   - Add a Replit PostgreSQL database or connect an external one
   - Set `DATABASE_URL` in production secrets

---

## Production Build (Frontend)

For a proper production frontend build (instead of the Vite dev server):

```bash
npm run build         # outputs to dist/
```

Then serve the `dist/` directory from Flask:

```python
# In main.py, Flask already serves dist/ as static root on non-API routes
```

Or use a CDN / separate static host (Netlify, Vercel, Cloudflare Pages) with `VITE_API_URL` pointing to your deployed backend.

---

## Running with Gunicorn (Production WSGI)

```bash
gunicorn --workers 4 --bind 0.0.0.0:5001 \
    --timeout 120 --access-logfile - main:app
```

For async workloads (file uploads, AI calls):
```bash
pip install gunicorn[eventlet]
gunicorn --worker-class eventlet --workers 2 --bind 0.0.0.0:5001 main:app
```

---

## Health Check

```bash
curl https://your-app.replit.app/api/health
# or
curl http://localhost:5001/api/health
```

Expected response: `{ "status": "ok", "timestamp": "..." }`

---

## Security Checklist (Pre-Launch)

- [ ] `FLASK_ENV` is NOT set to `development` in production
- [ ] `SESSION_SECRET` is at least 32 random bytes
- [ ] `JWT_SECRET_KEY` is set separately from `SESSION_SECRET`
- [ ] Admin default password changed
- [ ] PostgreSQL used (not SQLite) for persistent production data
- [ ] HTTPS enforced (Replit handles this automatically on `.replit.app`)
- [ ] CORS `origins` list is explicit (no wildcards in production)
- [ ] File upload directory is outside the web root or protected by auth
- [ ] Rate limiting is enabled for auth endpoints (`flask-limiter` is installed)

---

## Monitoring & Logs

- **Replit**: View workflow stdout/stderr in the Replit console
- **Gunicorn**: Access logs go to stdout (`--access-logfile -`)
- **Application**: Audit logs are stored in the `AuditLog` table, viewable via Admin Dashboard → Audit Logs

---

## Resetting the Database

**Development only:**
```bash
rm src/database/app.db
python main.py    # re-creates and bootstraps admin
```

**Production (PostgreSQL):**
```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
-- then run: flask db upgrade
```

---

## File Uploads

Uploaded files (lab results, radiology images, prescription scans) are stored in:
```
static/uploads/
  lab_requests/
  radiology/
  prescriptions/
  ...
```

In production, consider mounting a persistent volume or using cloud storage (S3-compatible):
- Install `boto3`
- Modify `_save_uploaded_file()` in `src/routes/lab_radiology.py` to write to S3
- Update `/api/uploads/...` route to generate signed S3 URLs

---

## Backup

**SQLite**
```bash
cp src/database/app.db backups/app.db.$(date +%Y%m%d)
```

**PostgreSQL**
```bash
pg_dump $DATABASE_URL > backups/sehaty_$(date +%Y%m%d).sql
```

Automate with a cron job or Replit scheduled workflow.
