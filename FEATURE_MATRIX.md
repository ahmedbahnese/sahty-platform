# Sahty Feature Matrix

**Audit date:** 2026-08-12  
**Tested means runtime-tested during this audit.** Source inspection is not counted as a passing test.

| Feature | Status | Frontend | Backend | Database | Tested | Bugs | Priority |
|---|---|---|---|---|---|---|---|
| Registration | IMPLEMENTED BUT NOT VERIFIED | `RegisterPage.jsx` and auth context submit registration | `POST /api/auth/register` in `src/routes/auth.py` | `users`, `patients` present; session/current role tables not fully present | No; pytest unavailable | Caller-supplied `user_type` needs privileged-role protection; runtime unverified | CRITICAL |
| Login | IMPLEMENTED BUT NOT VERIFIED | `LoginPage.jsx`, bearer token saved in context | `POST /api/auth/login`, password hash/JWT/session logic | `users` present; `user_sessions` absent in tracked DB | No | Persistence/revocation and current DB compatibility unverified | HIGH |
| Logout | IMPLEMENTED BUT NOT VERIFIED | Auth context removes local token and calls logout | `POST /api/auth/logout` revokes session | `user_sessions` missing from tracked DB | No | Cross-tab/session-expiry behavior untested | HIGH |
| Password handling | IMPLEMENTED BUT NOT VERIFIED | Login/change-password UI exists | Hashing, `change-password`, profile paths | `password_hash` present | No | Password policy, reset/recovery, brute-force behavior not fully tested | HIGH |
| Patient account | IMPLEMENTED BUT NOT VERIFIED | Register/profile/dashboard/records pages | Patient model and auth/profile routes | `patients` present | No | Complete patient lifecycle and ownership branches unverified | HIGH |
| Doctor account | PARTIALLY IMPLEMENTED | Doctor list/profile and booking UI | Doctor profile, availability, ratings, provider approval paths | `doctors`, availability present; role/provider tables missing | No | Professional approval/role activation and provider dashboard mismatch | HIGH |
| Nurse account | PARTIALLY IMPLEMENTED | Nursing dashboard and request actions | Nursing role request and request lifecycle routes | Nursing model tables absent | No | Current DB cannot prove workflow; `/nursing` route is allowed to patients | HIGH |
| Admin account | IMPLEMENTED BUT NOT VERIFIED | Admin dashboard | Admin provider/user/audit/stats routes with role checks | Admin/audit tables present | No | Existing dashboard duplication and bootstrap behavior need deployment test | HIGH |
| Role permissions | BROKEN | `RoleRoute` uses `user.user_type` | Mixed `@token_required`, `@role_required`, and ad-hoc checks | Role/UserRole tables absent | No | Professional roles can reach admin-backed general dashboard; full matrix unverified | CRITICAL |
| Dashboards | PARTIALLY IMPLEMENTED | Admin, general, nursing pages | Dashboard data comes from protected APIs | Admin tables present; nursing tables absent | No | General dashboard fetches admin endpoints for non-admin roles | HIGH |
| Medical record | PARTIALLY IMPLEMENTED | Medical record, clinical summary, medical report | Medical record and sub-record routes exist | Core records present; diseases/surgeries/vaccinations/labs/radiology/history absent | No | Existing DB schema drift; some detail errors only go to console | CRITICAL |
| Family accounts | PARTIALLY IMPLEMENTED | Family health and family appointment selectors | `/api/family/*` group/member/record/goal routes | All family-health tables absent | No | Current DB incompatibility and ownership branches unverified | HIGH |
| Appointments | IMPLEMENTED BUT NOT VERIFIED | List/book/reschedule/cancel/confirm/complete UI | `/api/appointments` lifecycle and notifications | `appointments`, history, ratings present | No | Role/object authorization and reminder behavior unverified | HIGH |
| Doctors directory | IMPLEMENTED BUT NOT VERIFIED | Search/filter/list/profile | Public list/profile/availability/rating routes | `doctors`, specializations present | No | Search semantics and inactive/unverified filtering need runtime test | MEDIUM |
| Hospitals | IMPLEMENTED BUT NOT VERIFIED | Hospital list/detail/review UI | Public list/detail plus admin mutation routes | Hospital tables present | No | Admin ownership and review constraints unverified | MEDIUM |
| Pharmacies | FRONTEND ONLY / MOCK | `PharmaciesPage.jsx` directory uses local/static presentation | Pharmacy orders exist in `pharmacy_order.py`; no verified directory page integration | `pharmacy_orders` absent; facility-directory tables absent | No | Directory search is not backed by the facility API | HIGH |
| Laboratories | PARTIALLY IMPLEMENTED | Request page uses facility API; directory page has sample data | Lab request CRUD/result/upload routes | `lab_requests` absent; current facility tables absent | No | Directory page static; schema and upload flow unverified | HIGH |
| Radiology | PARTIALLY IMPLEMENTED | Request page uses facility API; center directory is static | Radiology request/result/upload/share routes | `radiology_requests` absent; current facility tables absent | No | Directory page static; upload authorization unverified | HIGH |
| Blood bank | IMPLEMENTED BUT NOT VERIFIED | Donor/request/inventory UI | Donor/request/inventory/donation/compatibility routes | Blood-bank tables present | No | Public compatible-donor response exposes donor city/district/name fields | CRITICAL |
| Emergency services | PARTIALLY IMPLEMENTED | SOS, ambulance, alerts, QR, family contacts | Alert and ambulance request routes | `emergency_alerts`/`family_contacts` absent; legacy service table present | No | No confirmed external dispatch/SMS; current tables absent | CRITICAL |
| Smart assistant | PARTIALLY IMPLEMENTED | Floating chat and assistant page | Chat, voice, image, document, symptom, interaction, adherence routes | Mostly stateless; AI configuration external | No | Requires `OPENAI_API_KEY`; auth mismatch; raw errors returned | HIGH |
| Medical image/report upload | PARTIALLY IMPLEMENTED | Lab/radiology/AI/document file inputs | Multipart upload and authenticated file serving | File paths/data columns only in newer model paths | No | Served path lacks visible per-user authorization and upload limits need verification | CRITICAL |
| Medication management | IMPLEMENTED BUT NOT VERIFIED | Tracking, schedules, logs, order UI | Medication CRUD/log/adherence and pharmacy order routes | Medication tables present; `pharmacy_orders` absent | No | Current order schema absent; AI adherence depends on key | HIGH |
| Vaccination | IMPLEMENTED BUT NOT VERIFIED | Schedule, add/edit/delete, family member UI | Vaccination CRUD/schedule/upcoming routes | `vaccinations` absent in tracked DB | No | Startup/schema compatibility unverified | HIGH |
| Notifications | IMPLEMENTED BUT NOT VERIFIED | Notification bell and appointment notifications | General notification CRUD plus appointment notifications | `notifications` absent in tracked DB | No | Bell error/polling lifecycle and persistence unverified | MEDIUM |
| Location services | PARTIALLY IMPLEMENTED | Browser geolocation used for nearest pharmacy | Facility query accepts nearest/lat/lng | Current directory tables absent | No | No maps/geocoding/external location integration; permission failures need UX test | MEDIUM |
| Search and filters | PARTIALLY IMPLEMENTED | Doctor/hospital/directory filters; static lab/pharmacy/radiology search | Public list/filter endpoints exist | Directory data incomplete in tracked DB | No | Some page searches are local/sample-only; parameter behavior unverified | MEDIUM |
| File uploads | PARTIALLY IMPLEMENTED | Several multipart inputs | Lab/radiology/AI/pharmacy upload code | Path/data columns vary by model | No | File authorization, size/content validation, cleanup, and storage persistence unverified | CRITICAL |
| PDF/Excel export | NOT IMPLEMENTED | Browser `window.print()` / print-to-PDF labels only | No confirmed export endpoint or Excel generator | No export artifact model | No | No server-generated PDF/Excel workflow | MEDIUM |
| APIs | IMPLEMENTED BUT NOT VERIFIED | Many pages call `/api` routes | Broad blueprint API surface | Depends on incomplete current schema | No | No live contract test or OpenAPI/schema validation | HIGH |
| Database | BROKEN | UI cannot establish DB health | `db.create_all()` plus ad-hoc startup ALTERs | Tracked DB missing many declared tables | No | Schema drift; no migration revisions; persistence/deploy undefined | CRITICAL |
| Authentication persistence | PARTIALLY IMPLEMENTED | JWT in `localStorage`; startup user load | Session validity/revocation code | `user_sessions` absent from tracked DB | No | XSS exposure; refresh/expiry/cross-tab behavior untested | HIGH |
| Session persistence | PARTIALLY IMPLEMENTED | Token survives reload while present | Server-side session model and logout revocation | Session table absent in tracked DB | No | A current deployment may fail or behave differently from source model | HIGH |
| Mobile responsiveness | IMPLEMENTED BUT NOT VERIFIED | Responsive utility classes and mobile layouts appear throughout | N/A | N/A | No browser/device test | No mobile, viewport, touch, voice, permission, or accessibility run | MEDIUM |

## Overall classification counts

| Classification | Count |
|---|---:|
| Fully implemented and working | 0 |
| Implemented but not verified | 13 |
| Partially implemented | 15 |
| Frontend only / mock | 1 |
| Backend only | 0 |
| Broken | 3 |
| Not implemented | 1 |

Counts are intentionally conservative because no executable test stack was available.