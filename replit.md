# صحتك في أمان — Sahty Healthcare Platform

A full-stack Arabic healthcare web platform with a React/Vite frontend and Flask Python backend.

## Architecture

| Layer | Technology | Port |
|---|---|---|
| Frontend | React 19 + Vite + Tailwind CSS + shadcn/ui | 5000 |
| Backend API | Flask 3 + SQLAlchemy + SQLite | 5001 |
 | Database | PostgreSQL via `DATABASE_URL` (SQLite fallback for local use) | — |

## How to Run

Two workflows must be running simultaneously:

1. **Flask API** — `python main.py` → serves API on port 5001
2. **Start application** — `npm run dev` → serves React on port 5000, proxies `/api` → port 5001

## Project Structure

```
/
├── main.py                  # Flask application entry point
├── index.html               # Vite entry point
├── vite.config.js           # Vite config (proxy /api → :5001)
├── requirements.txt         # Python dependencies
├── package.json             # Node dependencies
├── src/
│   ├── models/              # SQLAlchemy models (Python)
│   │   ├── user.py          # User and server-side session models
│   │   ├── patient.py       # Patient, MedicalRecord, Allergy
│   │   ├── doctor.py        # Doctor, DoctorAvailability, Specialization
│   │   ├── appointment.py   # Appointment, AppointmentHistory, AppointmentRating
│   │   ├── medication.py    # Medication, MedicationSchedule, MedicationLog, DrugDatabase
│   │   ├── blood_bank.py    # BloodDonor, BloodRequest, BloodInventory
│   │   ├── hospital.py      # Hospital, HospitalDepartment, EmergencyService, HospitalReview
│   │   └── admin.py         # Admin, SystemOwner, SystemSettings, AuditLog
│   │   └── provider.py      # Registration and approval records for medical providers
│   ├── routes/              # Flask blueprints (Python)
│   │   ├── auth.py          # /api/auth/* — register, login, profile, logout
│   │   ├── admin.py         # /api/admin/* — approvals, statistics, user management
│   │   └── user.py          # /api/users/* — basic CRUD
│   ├── database/            # SQLite database file
│   ├── lib/utils.js         # shadcn/ui cn() utility
│   ├── contexts/            # React contexts
│   │   └── AuthContext.jsx  # JWT auth state management
│   ├── components/          # Shared React components
│   │   ├── Navbar.jsx
│   │   ├── Footer.jsx
│   │   └── ui/              # shadcn/ui component library
│   └── pages/               # React page components
│       ├── HomePage.jsx
│       ├── LoginPage.jsx
│       ├── RegisterPage.jsx
│       ├── DashboardPage.jsx
│       ├── DoctorsPage.jsx
│       ├── ServicesPage.jsx
│       ├── BloodBankPage.jsx
│       ├── EmergencyPage.jsx
└── init_database.py         # Database seeder (run once for sample data)
```

## API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| /api/health | GET | None | Health check |
| /api/auth/register | POST | None | User registration |
| /api/auth/login | POST | None | Login → signed token + persisted session |
| /api/auth/profile | GET | Bearer token | Get profile |
| /api/auth/logout | POST | Bearer token | Revoke the current session |
| /api/auth/change-password | POST | Bearer token | Change password and revoke active sessions |
| /api/users | GET/POST | Admin role | Protected user administration |
| /api/users/:id | GET/PUT | Own account or admin role | Protected user profile access |
| /api/users/:id | DELETE | Super-admin role | Protected user deletion |
| /api/admin/providers | GET | Admin role | List provider approval requests |
| /api/admin/providers/:id/review | PATCH | Admin role | Approve or reject a provider |
| /api/admin/users | GET | Admin role | List all users |
| /api/admin/users/:id/status | PATCH | Admin role | Activate or deactivate a user |
| /api/admin/stats | GET | Admin role | Dashboard statistics |

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| SESSION_SECRET | Yes | Flask secret key (set in Replit Secrets) |
| JWT_SECRET | Optional | JWT signing key (falls back to SESSION_SECRET) |
| DATABASE_URL | Managed | SQLAlchemy database URL; Replit supplies this for PostgreSQL |
| ADMIN_EMAIL | Optional | Creates the first super-admin when paired with `ADMIN_PASSWORD` |
| ADMIN_PASSWORD | Optional secret | Password for the first super-admin; never place it in source code |

## Database

- 29 tables fully created and relational, including `user_sessions` and `provider_registrations`
- Replit PostgreSQL is used when `DATABASE_URL` is present; SQLite is the fallback
- Run `python init_database.py` to seed sample data

## Security foundation

- Passwords are stored as Werkzeug hashes, never as plaintext.
- Every login creates a persisted `user_sessions` record with an expiry, token hash, client metadata, and revocation state.
- Bearer tokens are accepted only while their matching database session is active.
- Roles are enforced on the server (`patient`, `doctor`, `pharmacy`, `lab`, `radiology_center`, `hospital`, `admin`, `super_admin`); frontend visibility is not treated as authorization.
- Professional registrations remain pending until an administrator approves them; approval activates the account.

## User Preferences

- Keep existing Flask + React structure; do not migrate to another framework
- Arabic is the primary UI language (RTL layout)
