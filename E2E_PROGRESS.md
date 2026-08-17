# End-to-End Progress

## Definition of evidence

A workflow is marked `E2E PASS` only when a client-like request crosses authentication, authorization, validation, database persistence, state transition, and a subsequent read. A route-level or model-level unit test is reported separately and is not mislabeled as a full client journey.

## Verified journeys

| Journey | Evidence | Status |
|---|---|---|
| User registration → login → profile → role rejection → session | `scripts/e2e_user_doctor_appointments.py` plus authentication regression tests | PASS |
| Doctor search → specialty filter → profile/availability | E2E smoke script and doctor route tests | PASS |
| Patient booking → slot conflict guard → doctor confirmation → completion → patient read-back | `scripts/e2e_user_doctor_appointments.py` on isolated SQLite database | PASS |
| Medical records, prescriptions, medications | Domain API tests and ownership/input regression tests | API VERIFIED; browser E2E PENDING |
| Laboratory and radiology | Domain API tests, upload ownership and negative authorization tests | API VERIFIED; browser E2E PENDING |
| Hospitals, pharmacies, vaccinations, family health, blood bank, emergency, notifications, AI | Domain test selection: 55 passed in the latest run | API VERIFIED; browser E2E PENDING |

## Latest evidence

The user/doctor/appointment journey returned `E2E_USER_DOCTOR_APPOINTMENT=PASS` after creating a patient through the API, logging in, creating an isolated active doctor and availability record, searching/filtering, booking, logging in as the doctor, confirming, completing, and reading the completed appointment back as the patient.

The latest domain-focused test selection passed 55 tests, with 60 tests deselected because they belong to unrelated or shared suites. The complete backend suite remains at 115 passing tests.

## Remaining E2E acceptance

Full browser journeys still require running the built React client against a live Flask process and, for production acceptance, a Replit deployment using PostgreSQL and persistent Storage. Flutter has not been marked E2E because the native toolchain is unavailable in the current environment. No workflow is considered fully production-complete until the client journey, API, database, and deployment environment are exercised together.
