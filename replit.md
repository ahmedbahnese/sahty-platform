# صحتك في أمان — Sehaty Healthcare Platform

A full-stack Arabic-language healthcare web application.

## Stack
- **Frontend**: React 19 + Vite (port 5000), Tailwind CSS v4, Radix UI, React Router v7
- **Backend**: Flask 3 (port 5001), SQLAlchemy, SQLite (dev) / PostgreSQL (prod)
- **Auth**: JWT via PyJWT + bcrypt (server-side session revocation)
- **AI**: OpenAI GPT-4o (chat, image analysis, voice, symptom checker)
- **Security**: Flask-Limiter (rate limiting), security headers on every response
- **Migrations**: Flask-Migrate / Alembic

## Running the app
Two workflows must both be running:
1. **Flask API** — `python main.py` (port 5001)
2. **Start application** — `npm run dev` (port 5000, proxies `/api/*` → port 5001)

Open the preview on **port 5000** to see the app.

## Project structure
```
main.py              Flask entry point (blueprints, limiter, security headers)
requirements.txt     Python dependencies
package.json         Node dependencies
vite.config.js       Vite config (proxy, host)
migrations/          Flask-Migrate / Alembic migration scripts
src/
  main.jsx           React entry
  App.jsx            Router + layout
  pages/             Page components (18 pages)
  components/        Shared UI + NotificationBell
  contexts/          AuthContext (JWT, token, roles)
  models/            SQLAlchemy models (17 models)
  routes/            Flask blueprint routes (15 blueprints)
  services/          Business logic (ai_service.py)
  database/app.db    SQLite database (dev)
```

## API Blueprints
| Prefix | Module | Description |
|--------|--------|-------------|
| `/api/auth` | auth.py | Register, login, logout, profile |
| `/api/doctors` | doctor.py | Doctor search, profiles, availability slots, ratings |
| `/api/appointments` | appointment.py | Book, confirm, cancel, reschedule, complete |
| `/api/blood-bank` | blood_bank.py | Donors, requests, inventory, compatible search |
| `/api/notifications` | notification.py | List, mark-read, unread count, delete |
| `/api/ai` | ai.py | Chat (multi-turn), image analysis, voice, symptom checker |
| `/api/medical-record` | medical_record.py | EMR, diseases, surgery, vaccinations |
| `/api/prescriptions` | prescription.py | Prescriptions + pharmacy workflow |
| `/api/family` | family_health.py | Family groups, members, shared records |
| `/api/medications` | medication.py | Medication tracking + logs |
| `/api/admin` | admin.py | Admin dashboard, user/provider management |

## Environment variables / secrets
| Name | Purpose | Required |
|------|---------|----------|
| `SESSION_SECRET` | Flask secret key + JWT signing | ✅ Required |
| `OPENAI_API_KEY` | GPT-4o AI assistant, image analysis, voice | ✅ For AI features |
| `DATABASE_URL` | Override SQLite with PostgreSQL | Optional |
| `ADMIN_EMAIL` | Bootstrap admin account email (default: admin@sehaty.com) | Optional |
| `ADMIN_PASSWORD` | Bootstrap admin account password | Optional |
| `OPENAI_API_BASE` | Custom OpenAI-compatible base URL | Optional |

## PostgreSQL Migration (production)
```bash
# 1. Set DATABASE_URL secret to your PostgreSQL connection string
# 2. Initialize (already done — migrations/ folder exists)
flask db migrate -m "description"
flask db upgrade
```

## Security features
- JWT with server-side session revocation (token hash stored in DB)
- Rate limiting: 200/hr global, 20/min on auth, 30/hr on AI
- Security headers: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy
- HSTS enabled automatically in production (FLASK_ENV=production)
- Connection pool with pre-ping for stale connection detection

## Deployment
- `Procfile` included for Heroku/Render: `web: gunicorn wsgi:application`
- `render.yaml` included for Render.com one-click deploy
- Set `FLASK_ENV=production` in production to enable HSTS

## User preferences
