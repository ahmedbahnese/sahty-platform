# Sahty / صحتك في أمان — Current State Report

**Audit date:** 2026-08-12  
**Audit mode:** Read-only source/configuration audit. No product features, business logic, or existing files were changed.  
**Scope:** React/Vite frontend, Flask/SQLAlchemy backend, tracked SQLite database, tests, deployment configuration, and documented environment variables.

## Executive summary

Sahty is a substantial healthcare portal with an Arabic React frontend and a Flask API. The repository contains real models and API routes for identity, appointments, records, providers, family health, medication, lab/radiology requests, emergency workflows, blood bank, notifications, vaccination, and AI-assisted workflows.

The project is **not release-verifiable from the current checkout**:

- `npm run build` and `npm run lint` could not start because `vite` and `eslint` are not installed.
- `pytest -q` could not start because `pytest` is not installed.
- No Replit workflow is configured in the project snapshot.
- The tracked `src/database/app.db` predates many current models. It has 24 tables, while source models declare substantially more; the missing tables include family health, current directory, lab/radiology requests, most medical-record subtypes, notifications, prescriptions, professional roles, nursing, provider registrations, sessions, and pharmacy orders.
- Flask-Migrate is initialized but there are no migration revisions, and production configuration does not run `flask db upgrade`.
- The production/render configuration installs Python dependencies but does not build the React app.

The application should therefore be treated as **a feature-rich development baseline with important security, schema, deployment, and authorization risks**, not as a verified healthcare production system.

## Architecture observed

- **Frontend:** React 19 + Vite + React Router, `src/App.jsx`, `src/pages/`, `src/components/`.
- **Backend:** Flask 3 + Flask-SQLAlchemy + Flask-Migrate, initialized in `main.py`; WSGI entry point is `wsgi.py`.
- **Authentication:** HS256 JWTs, a server-side `user_sessions` revocation table in the current source model, bearer tokens read from browser `localStorage`.
- **Default database:** repository-local SQLite at `src/database/app.db`; PostgreSQL is supported through `DATABASE_URL`.
- **API surface:** approximately 20 registered blueprints under `/api`, `/api/auth`, `/api/admin`, `/api/medical-record`, `/api/appointments`, and related prefixes.
- **Optional services:** OpenAI-dependent assistant features; no external messaging, maps, storage, payment, SMS, or email integration is configured in the repository.

## Status classification

The classifications in `FEATURE_MATRIX.md` mean:

1. **FULLY IMPLEMENTED AND WORKING** — runtime evidence exists for the complete trace.
2. **IMPLEMENTED BUT NOT VERIFIED** — source path exists, but this audit could not execute a reliable end-to-end test.
3. **PARTIALLY IMPLEMENTED** — a real path exists but an important workflow, role, persistence, or integration segment is incomplete.
4. **FRONTEND ONLY / MOCK** — UI or sample data exists without a confirmed backend flow.
5. **BACKEND ONLY** — backend capability exists without a matching usable frontend path.
6. **BROKEN** — source/configuration evidence identifies a failure in the normal workflow.
7. **NOT IMPLEMENTED** — no corresponding implementation was found.

## A. What is actually working

These are source-confirmed capabilities, not production-certified workflows:

- Flask application initialization, blueprint registration, JSON API patterns, security headers, CORS allowlist handling, and rate-limit setup.
- Password hashing with Werkzeug and JWT issuance/session tracking code.
- Real SQLAlchemy models and routes for patients, doctors, appointments, medical records, prescriptions, medication adherence, family health, nursing, lab/radiology requests, emergency alerts, blood bank, hospitals, notifications, vaccination, and the healthcare directory.
- Public doctor, hospital, and healthcare-directory API routes.
- A tracked SQLite database with a core subset of the original schema.
- Backend smoke-test intent covering authentication, protected routes, selected public routes, and model creation.

No feature qualifies as **FULLY IMPLEMENTED AND WORKING** under this audit because the required runtime toolchain was unavailable and no reliable browser/API end-to-end run was completed.

## B. What is partially implemented

- Professional-role onboarding and role switching: roles and approvals exist, but role enforcement is distributed and not fully verified.
- Provider dashboards: the app has admin and nursing pages, but the general dashboard is routed to multiple professional roles and calls admin endpoints.
- Medical records: the main patient record exists, while many newer sub-record models are absent from the tracked database.
- Family health: groups, members, records, and goals exist in source, but current database compatibility and all ownership branches are unverified.
- Lab/radiology: request/result/upload/share routes exist, but upload authorization and current schema need verification.
- Emergency: SOS, ambulance request, QR, alerts, and in-app family notification exist; real emergency dispatch/SMS is not present.
- AI: UI and API variants exist, but require `OPENAI_API_KEY`, are auth-inconsistent, and expose raw service errors.
- Search/location: some directory APIs and browser geolocation exist, while several provider directories use local sample arrays.
- Vaccination and notifications: source flows exist, but the tracked DB lacks their current tables.

## C. What is broken or high risk

- Current production/deployment setup does not build the frontend or apply migrations.
- The tracked database is schema-incomplete relative to current source models.
- Frontend route permissions send many professional roles to a dashboard that calls admin-only APIs.
- AI pages are publicly reachable while their operations require authentication and an optional external key.
- Authenticated upload serving does not visibly verify that the requested path belongs to the requesting user.
- Public compatible-donor search returns donor-identifying/location fields.
- Registration accepts a requested `user_type`; self-assigned privileged roles require explicit verification and hardening.
- Browser JWT storage in `localStorage` increases XSS impact.
- Tests are not runnable in this checkout and several existing assertions accept failure statuses or skip when setup fails.

See `BUG_LIST.md` for severity, reproduction, expected/actual behavior, and recommended next action.

## D. What is only UI/mock

- `LabsDirectoryPage.jsx` seeds `SAMPLE_LABS` and does not show a corresponding facility fetch.
- `PharmaciesPage.jsx` and `RadiologyCentersPage.jsx` are directory-style pages with local/static data behavior rather than a verified API-backed search.
- Services and pending-approval content is informational/static.
- Print-to-PDF controls are browser print actions, not a server-side PDF/Excel export pipeline.

## E. What is missing

- A reproducible installed Node/Python toolchain in the imported checkout.
- A configured Replit run workflow.
- Migration revision history and a tested production migration process.
- Production frontend build in the deployment definition.
- A durable production database configuration in `render.yaml`.
- Frontend unit, integration, browser, accessibility, responsive, upload, and deployment smoke tests.
- Verified export endpoints for PDF and Excel.
- A configured/verified OpenAI, messaging, maps, file storage, or emergency-dispatch integration.

## F. What must be fixed first

1. Protect healthcare data and privileged routes: verify registration role assignment, enforce server-side object ownership, lock down upload serving, and remove donor PII from public search.
2. Establish schema correctness: generate/commit migrations, reconcile the tracked development database, and test a clean and existing-database upgrade.
3. Make deployment reproducible: install/build frontend assets, configure a durable database, run migrations, set allowed origins, and add a Replit workflow.
4. Fix role-to-dashboard routing and the auth contract for AI/professional pages.
5. Install and run the toolchain, then add strict end-to-end tests before changing business behavior.

## G. What should NOT be touched yet

- Do not redesign the application or rewrite the React/Vite/Flask structure.
- Do not delete existing pages, routes, models, or seed data before a product decision.
- Do not replace SQLite/PostgreSQL or introduce a new hosting architecture as part of this baseline.
- Do not enable AI or invent external service credentials.
- Do not expose or migrate the tracked healthcare data to an external service without a privacy/data-retention decision.
- Do not implement exports, payments, SMS, maps, or dispatch until their requirements and security boundaries are defined.

## Evidence index

- Frontend route and role guards: `src/App.jsx`
- Auth persistence and login/register/logout: `src/contexts/AuthContext.jsx`, `src/routes/auth.py`
- Startup/schema handling: `main.py`
- Route inventory: `API_AUDIT.md`
- Model/database comparison: `DATABASE_AUDIT.md`
- Role findings: `ROLE_PERMISSION_AUDIT.md`
- Executed-check limitations and test plan: `QA_TEST_PLAN.md`