# Sahty API Audit

**Audit date:** 2026-08-12  
**Audit method:** Route decorator inventory, frontend call-site inspection, model tracing, and test/config review. No live API run was possible because Python test dependencies are unavailable.

## API registration and entry points

Blueprint registration is in `main.py:127-147`. The public root/health/static behavior is also defined in `main.py`. The frontend Vite proxy sends `/api` to `http://localhost:5001` unless `API_URL` is set; the Replit-facing production process is intended to run Flask/Gunicorn on `$PORT`.

## Endpoint inventory by area

### Authentication and users

| Method | Endpoint | Source | Auth/role |
|---|---|---|---|
| POST | `/api/auth/register` | `src/routes/auth.py` | Public; requested type is accepted |
| POST | `/api/auth/login` | `src/routes/auth.py` | Public |
| GET/PUT | `/api/auth/profile` | `src/routes/auth.py` | Token |
| POST | `/api/auth/switch-role` | `src/routes/auth.py` | Token |
| POST | `/api/auth/apply-role` | `src/routes/auth.py` | Token |
| POST | `/api/auth/logout` | `src/routes/auth.py` | Token |
| GET | `/api/auth/doctors` | `src/routes/auth.py` | Source route; access needs runtime verification |
| GET | `/api/auth/patients` | `src/routes/auth.py` | Source route; access needs runtime verification |
| POST | `/api/auth/change-password` | `src/routes/auth.py` | Token |
| GET/POST | `/api/users` | `src/routes/user.py` | Admin decorators |
| GET/PUT/DELETE | `/api/users/<id>` | `src/routes/user.py` | Admin decorators |
| GET | `/api/health` | `src/routes/user.py` | Health check |

### Administration

| Method | Endpoint | Source | Auth/role |
|---|---|---|---|
| GET | `/api/admin/providers` | `admin.py` | Admin |
| GET | `/api/admin/role-requests` | `admin.py` | Admin |
| PATCH | `/api/admin/role-requests/<id>/review` | `admin.py` | Admin |
| PATCH | `/api/admin/providers/<id>/review` | `admin.py` | Admin |
| GET | `/api/admin/users` | `admin.py` | Admin |
| PATCH | `/api/admin/users/<id>/status` | `admin.py` | Admin |
| GET | `/api/admin/audit-logs` | `admin.py` | Admin |
| GET | `/api/admin/stats` | `admin.py` | Admin |

### Doctors, hospitals, and directory

| Method | Endpoint | Source | Auth/role |
|---|---|---|---|
| GET | `/api/doctors` | `doctor.py` / auth route variant | Public |
| GET | `/api/doctors/<id>` | `doctor.py` | Public |
| GET | `/api/doctors/<id>/available-slots` | `doctor.py` | Public |
| GET/PUT | `/api/doctors/me` | `doctor.py` | Token; professional ownership needs test |
| POST | `/api/doctors/me/availability` | `doctor.py` | Token; professional ownership needs test |
| POST | `/api/doctors/<id>/rate` | `doctor.py` | Token |
| GET | `/api/hospitals` and `/api/hospitals/<id>` | `hospital.py` | Public |
| POST/PUT/DELETE | `/api/hospitals...` | `hospital.py` | Admin checks |
| GET/POST | `/api/hospitals/<id>/departments` | `hospital.py` | Mixed |
| POST | `/api/hospitals/<id>/review` | `hospital.py` | Patient |
| GET | `/api/facilities` | `egypt_healthcare.py` | Public |
| GET | `/api/facilities/metadata` | `egypt_healthcare.py` | Public |
| GET | `/api/facilities/<id>` | `egypt_healthcare.py` | Public |

### Appointments and prescriptions

| Method | Endpoint | Source | Auth/role |
|---|---|---|---|
| GET/POST | `/api/appointments` | `appointment.py` | Token |
| GET | `/api/appointments/stats` | `appointment.py` | Token; role semantics need test |
| GET/PUT | `/api/appointments/<id>` | `appointment.py` | Token/object checks |
| POST | `/api/appointments/<id>/cancel` | `appointment.py` | Token/object checks |
| POST | `/api/appointments/<id>/confirm` | `appointment.py` | Token/object checks |
| POST | `/api/appointments/<id>/complete` | `appointment.py` | Token/object checks |
| GET | `/api/appointments/notifications` | `appointment.py` | Token |
| POST | `/api/appointments/notifications/mark-read` | `appointment.py` | Token |
| GET/POST | `/api/prescriptions` | `prescription.py` | Token/mixed workflow |
| GET | `/api/prescriptions/<id>` | `prescription.py` | Token/object checks |
| POST | `/api/prescriptions/<id>/send-pharmacy` | `prescription.py` | Token/mixed workflow |
| POST | `/api/prescriptions/<id>/dispense` | `prescription.py` | Token/mixed workflow |
| POST | `/api/prescriptions/<id>/cancel` | `prescription.py` | Token/mixed workflow |

### Medical records, lab, and radiology

The medical-record blueprint is registered with `/api/medical-record`. It contains patient-scoped record CRUD, clinical summary/visit paths, public-record token paths, and sub-record operations for diseases, surgeries, allergies, vaccinations, labs, radiology, ECG, blood gas, and history.

The lab/radiology blueprint is registered under `/api` and includes:

- Lab request list/create/detail/update/delete, approve/reject, results, notify, and document upload routes.
- Radiology request list/create/detail/update/delete, approve/reject, report upload, and share routes.
- Authenticated `/api/uploads/<path:filepath>` serving.

The source has real backend paths, but the tracked DB lacks `lab_requests`, `radiology_requests`, and most medical-record extension tables. Upload serving is token-protected but does not visibly resolve the file to an authorized patient/provider before sending it.

### Medication, pharmacy, vaccination, notifications

| Method | Endpoint family | Source | Assessment |
|---|---|---|---|
| CRUD/GET | `/api/medications...` | `medication.py` | Real source routes; current tables partially absent |
| CRUD/GET | `/api/pharmacy-orders...` | `pharmacy_order.py` | Real backend order workflow; `pharmacy_orders` table absent |
| CRUD/GET | `/api/vaccinations...` | `vaccination.py` | Real source routes; `vaccinations` table absent |
| GET/POST/DELETE | `/api/notifications...` | `notification.py` | Real source routes; `notifications` table absent |

### Family, nursing, emergency, and blood bank

| Method | Endpoint family | Source | Assessment |
|---|---|---|---|
| CRUD | `/api/family/groups...` | `family_health.py` | Real source workflow; family tables absent |
| CRUD | `/api/family/members...` | `family_health.py` | Real source workflow; ownership needs tests |
| CRUD | `/api/family/records...`, `/goals...` | `family_health.py` | Real source workflow; current DB unverified |
| POST/GET | `/api/nursing/role-request`, `/api/nursing/requests...` | `nursing.py` | Real source workflow; nursing tables absent |
| GET/POST/PUT/DELETE | `/api/emergency/...` | `emergency.py` | In-app emergency workflow; no confirmed external dispatch |
| CRUD | `/api/blood-bank/...` | `blood_bank.py` | Real source workflow; compatible-donor privacy issue |

### AI

| Method | Endpoint | Source | Assessment |
|---|---|---|---|
| POST | `/api/ai/chat` | `ai.py` | Requires token/service key; UI mapping needs verification |
| POST | `/api/ai/voice-assistant` | `ai.py` | Browser voice + OpenAI dependent |
| POST | `/api/ai/analyze-image` | `ai.py` | Multipart; file validation and key required |
| POST | `/api/ai/analyze-voice` | `ai.py` | Backend route; UI coverage unclear |
| POST | `/api/ai/symptom-checker` and `-v2` | `ai.py` | Auth/UI policy mismatch |
| GET | `/api/ai/medication-adherence` | `ai.py` | Medication + AI dependent |
| POST | `/api/ai/drug-interaction` | `ai.py` | Backend route; UI coverage needs test |
| GET | `/api/ai/health-report` | `ai.py` | Backend route; UI coverage needs test |
| POST | `/api/ai/analyze-document` | `ai.py` | Multipart PDF/image; storage/privacy needs test |
| GET | `/api/ai/health-tips` | `ai.py` | Backend route; key/config behavior needs test |

## Frontend/API contract findings

- Vite development expects the API at port 5001, while the Replit-oriented documentation says `PORT=5000 python main.py`; the production process uses one Gunicorn port. This needs one documented development workflow.
- `DashboardPage.jsx` calls admin endpoints but `App.jsx` allows all professional roles to reach it.
- Lab/pharmacy/radiology directory pages do not have the same facility API integration as request pages.
- AI pages are route-public while backend operations are bearer-token protected.
- Error handling is inconsistent: some page catches only log to console or swallow the exception, leaving no visible retry state.

## API test verdict

**Status: IMPLEMENTED BUT NOT VERIFIED.** The source contains a broad API, but this audit did not run a live server, contract suite, browser request trace, or database-backed end-to-end flow.