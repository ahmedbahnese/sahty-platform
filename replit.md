# صحتك في أمان — Sahty Healthcare Platform

A full-stack Arabic healthcare web platform with a React/Vite frontend and Flask Python backend.

## Architecture

| Layer | Technology | Port |
|---|---|---|
| Frontend | React 19 + Vite + Tailwind CSS + shadcn/ui | 5000 |
| Backend API | Flask 3 + SQLAlchemy + SQLite | 5001 |
| Database | SQLite (`src/database/app.db`) | — |

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
│   │   ├── user.py          # User model (auth base)
│   │   ├── patient.py       # Patient, MedicalRecord, Allergy
│   │   ├── doctor.py        # Doctor, DoctorAvailability, Specialization
│   │   ├── appointment.py   # Appointment, AppointmentHistory, AppointmentRating
│   │   ├── medication.py    # Medication, MedicationSchedule, MedicationLog, DrugDatabase
│   │   ├── blood_bank.py    # BloodDonor, BloodRequest, BloodInventory
│   │   ├── hospital.py      # Hospital, HospitalDepartment, EmergencyService, HospitalReview
│   │   └── admin.py         # Admin, SystemOwner, SystemSettings, AuditLog
│   ├── routes/              # Flask blueprints (Python)
│   │   ├── auth.py          # /api/auth/* — register, login, profile, logout
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
│       └── AIAssistantPage.jsx
└── init_database.py         # Database seeder (run once for sample data)
```

## Test Accounts

| Role | Email | Password |
|---|---|---|
| Super Admin / Owner | Ahmedbahnese@yahoo.com | Bahnasy123 |
| Sample Doctor | doctor@sahty.zya.me | doctor123 |
| Sample Patient | patient@sahty.zya.me | patient123 |

## API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| /api/health | GET | None | Health check |
| /api/auth/register | POST | None | User registration |
| /api/auth/login | POST | None | Login → JWT token |
| /api/auth/owner-login | POST | None | Owner login |
| /api/auth/profile | GET | Bearer token | Get profile |
| /api/auth/logout | POST | Bearer token | Logout |
| /api/auth/change-password | POST | Bearer token | Change password |
| /api/users | GET/POST | None | User CRUD |
| /api/users/:id | GET/PUT/DELETE | None | User by ID |

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| SESSION_SECRET | Yes | Flask secret key (set in Replit Secrets) |
| OPENAI_API_KEY | For AI features | OpenAI API key for AI Assistant |
| JWT_SECRET | Optional | JWT signing key (falls back to SESSION_SECRET) |

## Database

- 27 tables fully created and relational
- SQLite at `src/database/app.db`
- Run `python init_database.py` to seed sample data

## User Preferences

- Keep existing Flask + React structure; do not migrate to another framework
- Arabic is the primary UI language (RTL layout)
- The project owner is Ahmed Bahnasi (Ahmedbahnese@yahoo.com)
