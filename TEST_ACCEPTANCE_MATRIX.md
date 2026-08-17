# Sehaty Test Acceptance Matrix

## Acceptance rule

A successful build proves only that the source can be compiled or bundled. It does not prove authentication, authorization, persistence, workflow correctness, ownership, browser behavior, or native-device behavior. A release candidate is accepted only when the required gates for its target environment are green.

## Backend

| Level | Scope | Current command/evidence | Status |
|---|---|---|---|
| Unit | Model and helper behavior | `python3 -m pytest -q` with focused tests | VERIFIED in the current suite |
| Integration | Flask routes with isolated SQLite and SQLAlchemy persistence | `python3 -m pytest -q` and `scripts/e2e_user_doctor_appointments.py` | VERIFIED for covered workflows |
| API | Request/response contracts, validation, status codes, filters, pagination | API tests and `docs/API_CONTRACT.md` | VERIFIED for covered endpoints |
| Security | JWT/session revocation, role checks, IDOR, input rejection, file ownership | `tests/test_authorization_negative.py` and full suite | VERIFIED for covered controls |
| PostgreSQL acceptance | Migrations, indexes, backup/restore, `/readyz` on real PostgreSQL | Requires a real Replit `DATABASE_URL` | NOT VERIFIED |

## Web

| Level | Scope | Current command/evidence | Status |
|---|---|---|---|
| Component | React component rendering and interactions | No dedicated Vitest/Testing Library suite is configured | NOT IMPLEMENTED |
| Integration | React page calls Flask API and reflects persisted state | Dashboard API wiring and API tests; no browser harness | PARTIAL |
| E2E | Login → dashboard → action → database update → UI refresh | Backend-like E2E exists for user/doctor/appointments; browser E2E is absent | PARTIAL |
| Build/lint | Vite bundle and ESLint | `npm run build`, `npm run lint` | VERIFIED; not a product acceptance gate |

## Mobile

| Level | Scope | Current command/evidence | Status |
|---|---|---|---|
| Unit | API client, secure session, User model | `mobile/test/` exists | NOT EXECUTED: Flutter unavailable |
| Widget | Login, session home, doctors screen | No widget suite yet | NOT IMPLEMENTED |
| Integration | Flutter client against a running Flask API | No integration test suite yet | NOT IMPLEMENTED |
| Real device | Android and iOS builds and workflows | Requires Flutter, Android SDK, macOS/Xcode for iOS | NOT VERIFIED |

## Production-like environment gates

The acceptance environment must use PostgreSQL rather than SQLite, a shared Redis-compatible rate-limit store rather than `memory://`, HTTPS at the public edge, explicit CORS origins, persistent file storage, production secrets from Replit Secrets, and a separate restore target for backup verification. The current sandbox can verify configuration guards and SQLite workflow behavior, but it cannot truthfully certify these deployment gates without the actual services.

## Release decision

The current project is suitable for continued implementation and backend/API QA. It is not yet a fully accepted production release because Web browser E2E, Flutter analysis/widget/integration tests, real-device testing, and PostgreSQL backup/restore acceptance remain open. These statuses are intentional and must not be replaced by build-success claims.
