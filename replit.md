# صحتك في أمان — Sahty Healthcare Platform

منصة طبية شاملة تجمع بين الأطباء والخدمات الصحية المتطورة.

## Stack

- **Backend:** Flask (Python 3.12), SQLAlchemy, PyJWT, bcrypt
- **Frontend:** React 19, Vite 6, Tailwind CSS 4, Radix UI
- **Database:** PostgreSQL (via `DATABASE_URL`) — falls back to SQLite for local dev
- **Auth:** JWT tokens + session management

## How to Run

Two workflows run in parallel:

| Workflow | Command | Port |
|----------|---------|------|
| Flask API | `python main.py` | 5001 |
| Start application | `npm run dev` | 5000 |

The Vite dev server proxies `/api` requests to the Flask backend on port 5001.

## Project Structure

```
main.py              — Flask app entry point
src/
  models/            — SQLAlchemy models (user, patient, doctor, appointment, …)
  routes/            — Flask blueprints (auth, user, admin)
  database/          — SQLite fallback DB
  components/        — React UI components
  pages/             — React page components
  contexts/          — React context (AuthContext)
```

## Environment Secrets

| Secret | Purpose |
|--------|---------|
| `SESSION_SECRET` | Flask secret key + JWT signing |
| `DATABASE_URL` | PostgreSQL connection string (auto-detected) |
| `ADMIN_EMAIL` + `ADMIN_PASSWORD` | Bootstrap first super-admin on startup |

## User Preferences

- Keep existing project structure and stack — do not restructure or migrate.
- Arabic is the primary UI language (RTL).
