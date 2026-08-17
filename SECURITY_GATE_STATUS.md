# Security Gate Status

## Verified controls

| Control | Status | Evidence |
|---|---|---|
| Authentication | WORKING | JWT signature, expiry, server-side hashed session lookup, revocation, active-account check |
| Authorization | WORKING on regression suite | Server-side role validation and role assignment checks |
| Resource ownership / IDOR | WORKING on current negative suite | Cross-patient records and upload access are denied; pharmacy orders now bind patient/pharmacy/admin access explicitly |
| Input validation | WORKING on tested routes | Invalid JSON, appointment fields, prescription fields, emergency and family data are rejected without 500 |
| File path security | WORKING on lab/radiology downloads | Traversal-like paths rejected; record ownership is required before `send_from_directory` |
| File extension and size boundary | PARTIAL | Extension allowlists and Flask request-size boundary exist; content scanning and external persistent storage remain deployment requirements |
| Password security | WORKING | Werkzeug password hashes; password change validates JSON and minimum length; active sessions are revoked after change |
| Token/session security | WORKING | Short-lived JWT, JTI, hashed token storage, expiry, revocation, last-seen tracking |
| Rate limiting | WORKING in development; production guard active | Auth and AI limits exist; production refuses the in-memory store and requires shared `RATELIMIT_STORAGE_URI` |
| CORS | CONFIGURED | Explicit production origins via `CORS_ORIGINS`; development localhost origins only outside production |
| Secrets management | CONFIGURED | Required secrets are read from environment/Replit Secrets and are not committed |
| HTTPS | DEPLOYMENT CONTROL | HSTS is emitted in production; TLS termination must be enabled at the Replit/edge proxy |
| Error leakage | IMPROVED | Auth exceptions are logged server-side and generic messages are returned to clients |

## Pharmacy IDOR fix

A pharmacy can no longer choose an arbitrary `pharmacy_id` query parameter to list orders. The server resolves the approved pharmacy registration from the authenticated user. A pharmacy can read, confirm, dispense, or cancel only orders whose `preferred_pharmacy_id` matches its approved registration. Patients can access only their own orders, and other roles receive 403 unless they are admin or super_admin.

## Test evidence

The targeted security suite passed 108 tests and the full suite passed 115 tests. The production configuration was also tested to ensure that importing the application without a shared rate-limit store fails with an explicit `RATELIMIT_STORAGE_URI` requirement rather than silently using process-local memory.

## Remaining deployment verification

A complete production security acceptance still requires a real Replit deployment with PostgreSQL, a shared Redis-compatible rate-limit store, explicit CORS origins, HTTPS at the public edge, and external persistent medical-file storage. These cannot be truthfully marked verified from the local sandbox alone.
