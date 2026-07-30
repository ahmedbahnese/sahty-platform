# صحتك في أمان — Sehaty Healthcare Platform

A full-stack Arabic-language healthcare web application.

## Stack
- **Frontend**: React 19 + Vite (port 5000), Tailwind CSS v4, Radix UI, React Router v7
- **Backend**: Flask 3 (port 5001), SQLAlchemy, SQLite (dev) / PostgreSQL (prod)
- **Auth**: JWT via PyJWT + bcrypt

## Running the app
Two workflows must both be running:
1. **Flask API** — `python main.py` (port 5001)
2. **Start application** — `npm run dev` (port 5000, proxies `/api/*` → port 5001)

Open the preview on **port 5000** to see the app.

## Project structure
```
main.py              Flask entry point
requirements.txt     Python dependencies
package.json         Node dependencies
vite.config.js       Vite config (proxy, host)
index.html           Vite HTML entry
src/
  main.jsx           React entry
  App.jsx            Router + layout
  index.css          Global styles
  pages/             Page components
  components/        Shared UI components (ui/ = shadcn/radix)
  contexts/          AuthContext
  models/            SQLAlchemy models
  routes/            Flask blueprint routes
  services/          Business logic services
  database/app.db    SQLite database file
```

## Environment variables / secrets
| Name | Purpose | Required |
|------|---------|----------|
| `SESSION_SECRET` | Flask secret key + JWT signing | ✅ Required |
| `DATABASE_URL` | Override SQLite with PostgreSQL | Optional |
| `ADMIN_EMAIL` | Bootstrap admin account email (default: admin@sehaty.com) | Optional |
| `ADMIN_PASSWORD` | Bootstrap admin account password | Optional |

## User preferences
