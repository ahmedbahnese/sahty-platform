# Sahty QA Test Plan and Audit Execution Record

**Audit date:** 2026-08-12  
**Purpose:** establish a repeatable QA baseline without changing product behavior.

## Audit execution record

| Command/check | Result | Evidence |
|---|---|---|
| `npm run build` | NOT RUNNABLE | `vite: not found`; frontend dependencies are not installed |
| `npm run lint` | NOT RUNNABLE | `eslint: not found`; frontend dependencies are not installed |
| `pytest -q` | NOT RUNNABLE | `pytest: command not found`; Python test dependencies are not installed |
| Route/model static inventory | COMPLETED | AST/source inspection of `src/routes`, `src/models`, `src/App.jsx` |
| Tracked SQLite table comparison | COMPLETED | 24 actual tables compared with current source model tables |
| Browser screenshot/e2e | NOT RUN | No configured workflow/server and no browser test harness available |
| Production deployment test | NOT RUN | No deployment was requested; render config was inspected only |

No command above constitutes a passing application test. Installing dependencies and running the suite is the first prerequisite for runtime verification.

## Existing QA assets

- `tests/test_backend.py`: backend smoke tests for authentication, public/protected endpoints, blood bank, emergency, AI input handling, security checks, and model creation.
- `tests/test_comprehensive.py`: broader auth, protected-route, directory, AI, and model checks.
- `tests/conftest.py`: in-memory SQLite fixture intent.
- No frontend test script or browser/e2e dependency is defined in `package.json`.

## Existing test weaknesses

- Some assertions accept `404`, `401`, or `500`, which can turn a missing endpoint or server error into a passing test.
- Some comprehensive tests skip when token setup fails, masking broken registration/login.
- The two suites configure the imported app/database independently, risking fixture coupling and order dependence.
- No test currently proves migration compatibility, PostgreSQL behavior, restart persistence, uploaded-file ownership, or deployment startup.
- No frontend unit, accessibility, mobile viewport, keyboard, touch, service-worker, or browser permission suite is present.

## Test levels

### Level 0 — Static and contract checks

- Parse all Python modules and compile the frontend after dependency installation.
- Build a generated API route inventory from blueprint registration.
- Compare SQLAlchemy metadata, migration state, and database tables/columns.
- Validate that every frontend API call has a backend route and expected method/payload.
- Scan for unhandled `fetch` failures, swallowed catches, direct token storage, unsafe file path handling, and privileged role inputs.

### Level 1 — Backend unit tests

- Password hash verification, invalid credentials, duplicate registration, password change, and password policy.
- JWT expiry, invalid signature, revoked session, logout, and inactive user.
- Role activation/switching and public-role restrictions.
- Object ownership for every patient/provider/family/file resource.
- Upload extension/content/size/path traversal checks.
- AI key absent/provider failure returns safe stable error responses.
- Notification creation/read/delete and appointment state transitions.

### Level 2 — API integration tests

Use a clean database and a migrated copy of the current database. Assert exact status codes and response schemas:

| Area | Minimum scenarios |
|---|---|
| Registration/login/logout | patient success; duplicate; invalid password; privileged role rejection; logout revokes old token; reload/session validity |
| Patient record | patient CRUD; second patient denied; provider relationship rules; public-token scope/expiry |
| Roles/admin | patient/doctor/nurse/provider/admin/super-admin matrix; role request approval/rejection; session rotation |
| Appointments | book, list, reschedule, cancel, confirm, complete, ratings, reminders, family member appointment |
| Prescriptions/medications | doctor create; patient read; pharmacy send/dispense; adherence log; cross-user denial |
| Family | group/member/record/goal CRUD; owner and member visibility; deletion constraints |
| Lab/radiology | request, approval, result, upload, share, download, cross-user file denial |
| Emergency | SOS/ambulance/alerts/resolve; family contact ownership; delivery limitation is explicit |
| Blood bank | donor consent/profile; compatible search privacy; request/response/inventory |
| Directory/search | filters, pagination, empty results, nearest query, invalid coordinates |
| Notifications/vaccination | persistence, unread count, mark-read, schedule/upcoming, family member vaccine |
| AI | auth policy, missing key, valid input, invalid file, provider error, safe redaction |

### Level 3 — Frontend component/integration tests

- Register/login/logout/loading/error states.
- Protected/public/role-specific route redirects.
- Dashboard rendering for every role.
- Medical record CRUD and visible error/retry states.
- Appointment lifecycle and notification bell.
- File selection, upload progress/error, download authorization handling.
- Static directory pages must be either explicitly labeled as sample content or API-backed.

### Level 4 — Browser/e2e and responsive tests

Required browsers/viewports:

- Chromium desktop and mobile viewport.
- Keyboard-only navigation and focus order.
- Arabic RTL layout, long names, empty/error/loading states.
- Mobile navigation, modals, tables, file inputs, touch targets.
- Browser geolocation denied/allowed.
- Microphone/camera denied/allowed and policy alignment.
- Refresh, back/forward, expired token, two-tab logout.

### Level 5 — Deployment smoke tests

1. Install Node/Python dependencies from committed manifests.
2. Build frontend assets.
3. Create a clean DB and apply migrations.
4. Start Gunicorn on `$PORT`.
5. Verify `/`, `/api/health`, static assets, login, and one protected route.
6. Restart and verify data persistence.
7. Repeat with PostgreSQL if it is the production target.

## Acceptance gates

The project should not be marked release-ready until:

- build, lint, backend tests, and browser smoke tests run in CI;
- no critical/high auth, authorization, upload, donor-privacy, or schema findings remain open;
- migrations upgrade both clean and existing databases;
- deployment builds and serves the frontend from the documented process;
- each requested feature in the feature matrix has a tested status;
- all known limitations (AI, messaging, maps, exports) are visible to product owners.

## QA verdict

**Status: NOT VERIFIED.** The repository has useful backend smoke tests but no executable toolchain in this checkout and no browser/deployment coverage for the healthcare workflows.