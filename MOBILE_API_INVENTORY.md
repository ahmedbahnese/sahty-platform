# Sahty Mobile API Inventory

**Inventory date:** 2026-08-16  
**Source of truth:** Flask route decorators, blueprint registration in `main.py`,
the existing API audit, models, and authorization decorators. This is a source
inventory, not a claim that every route is currently healthy against the
tracked database.

`/mobile` uses `API_BASE_URL` as the URL through `/api`. For example, the
development value is `http://10.0.2.2:5001/api` for an Android emulator, and
the login client sends `POST /auth/login` relative to that base URL.

| Module | Endpoint | Method | Authentication | Role | Request | Response | Mobile Use | Status |
|---|---|---:|---|---|---|---|---|---|
| Authentication | `/api/auth/register` | POST | Public | Patient or requested professional role | JSON registration fields | Token + user | Future registration screen | EXISTS BUT NEEDS VERIFICATION |
| Authentication | `/api/auth/login` | POST | Public | Any active account | `{email,password}` | JWT token + user | Implemented by mobile foundation | READY |
| Authentication | `/api/auth/profile` | GET/PUT | Bearer JWT | Any authenticated user | JSON profile fields for PUT | User profile, active roles | Session restoration/profile | EXISTS BUT NEEDS VERIFICATION |
| Authentication | `/api/auth/switch-role` | POST | Bearer JWT | Approved active role | `{role}` | Rotated JWT + user | Future role switcher | EXISTS BUT NEEDS VERIFICATION |
| Authentication | `/api/auth/apply-role` | POST | Bearer JWT | Patient account | `{role: doctor|nurse}` plus request data | Role request result | Future application flow | EXISTS BUT NEEDS VERIFICATION |
| Authentication | `/api/auth/logout` | POST | Bearer JWT | Any authenticated user | None | Message | Implemented by mobile foundation | READY |
| Authentication | `/api/auth/change-password` | POST | Bearer JWT | Any authenticated user | Current/new password | Message | Future security settings | EXISTS BUT NEEDS VERIFICATION |
| User/admin | `/api/users...` | GET/POST/PUT/DELETE | Bearer JWT | Admin/super admin decorators | JSON | User records | Admin boundary only | EXISTS BUT NEEDS VERIFICATION |
| Health | `/api/health` | GET | Public | None | None | Health payload | Connectivity probe | READY |
| Doctors | `/api/doctors` | GET | Public | None | Search/filter query | Doctor list | Directory | EXISTS BUT NEEDS VERIFICATION |
| Doctors | `/api/doctors/<id>` | GET | Public | None | Path id | Doctor + details | Doctor profile | EXISTS BUT NEEDS VERIFICATION |
| Doctors | `/api/doctors/<id>/available-slots` | GET | Public | None | Date query | Availability | Appointment booking | EXISTS BUT NEEDS VERIFICATION |
| Doctors | `/api/doctors/me` | GET/PUT | Bearer JWT | Doctor/ownership checks | JSON profile fields | Doctor profile | Provider profile | EXISTS BUT NEEDS VERIFICATION |
| Doctors | `/api/doctors/me/availability` | POST | Bearer JWT | Doctor | Availability JSON | Message/data | Provider availability | EXISTS BUT NEEDS VERIFICATION |
| Doctors | `/api/doctors/<id>/rate` | POST | Bearer JWT | Patient | Rating JSON | Rating result | Patient feedback | EXISTS BUT NEEDS VERIFICATION |
| Healthcare directory | `/api/hospitals...` | GET | Public | None | Filters/path id | Hospital records | Directory | EXISTS BUT NEEDS VERIFICATION |
| Healthcare directory | `/api/facilities...` | GET | Public | None | Governorate/type/filter query | Facility list/metadata/detail | Unified directory | EXISTS BUT NEEDS VERIFICATION |
| Appointments | `/api/appointments` | GET/POST | Bearer JWT | Patient/doctor workflow | Appointment JSON or filters | Appointment list/detail | Patient/doctor appointments | EXISTS BUT NEEDS VERIFICATION |
| Appointments | `/api/appointments/<id>` | GET/PUT | Bearer JWT | Object ownership | Appointment fields | Appointment | Appointment detail/reschedule | EXISTS BUT NEEDS VERIFICATION |
| Appointments | `/api/appointments/<id>/cancel` | POST | Bearer JWT | Object ownership | Optional reason | Message | Cancellation | EXISTS BUT NEEDS VERIFICATION |
| Appointments | `/api/appointments/<id>/confirm` | POST | Bearer JWT | Doctor | Path id | Message | Doctor workflow | EXISTS BUT NEEDS VERIFICATION |
| Appointments | `/api/appointments/<id>/complete` | POST | Bearer JWT | Doctor | Path id | Message | Doctor workflow | EXISTS BUT NEEDS VERIFICATION |
| Prescriptions | `/api/prescriptions...` | GET/POST | Bearer JWT | Patient/doctor workflow | Prescription JSON | Prescription records | Patient/doctor medication | EXISTS BUT NEEDS VERIFICATION |
| Prescriptions | `/api/prescriptions/<id>/send-pharmacy` | POST | Bearer JWT | Doctor | Path id | Message | Pharmacy handoff | EXISTS BUT NEEDS VERIFICATION |
| Prescriptions | `/api/prescriptions/<id>/dispense` | POST | Bearer JWT | Pharmacy | Path id | Message | Pharmacy workflow | EXISTS BUT NEEDS VERIFICATION |
| Medications | `/api/medications...` | GET/POST/PUT/DELETE | Bearer JWT | Owner | Medication JSON/path id | Medication records | Patient medication | PARTIAL |
| Medications | `/api/medications/<id>/log` | POST | Bearer JWT | Owner | Dose log JSON | Log result | Adherence | PARTIAL |
| Medications | `/api/medications/adherence-stats` | GET | Bearer JWT | Owner | None | Stats | Adherence dashboard | PARTIAL |
| Vaccinations | `/api/vaccinations...` | GET/POST/PUT/DELETE | Bearer JWT | Patient/family ownership | Vaccination JSON/path id | Vaccination records | Patient/family records | PARTIAL |
| Lab requests | `/api/lab-requests...` | GET/POST/PUT/DELETE | Bearer JWT | Patient/doctor/lab workflow | JSON; some multipart | Request records | Lab feature boundary | PARTIAL |
| Lab results | `/api/lab-requests/<id>/results` | POST | Bearer JWT | Laboratory | Multipart result file | Result record | PDF/image upload hook | PARTIAL |
| Radiology requests | `/api/radiology-requests...` | GET/POST/PUT/DELETE | Bearer JWT | Patient/doctor/radiology workflow | JSON; some multipart | Request records | Radiology feature boundary | PARTIAL |
| Radiology files | `/api/radiology-requests/<id>/images` and `/report` | POST | Bearer JWT | Radiology center | Multipart or JSON | Result/report | Image/report upload hook | PARTIAL |
| Uploads | `/api/uploads/<path>` | GET | Bearer JWT | File owner/provider policy | Path | File bytes | Authenticated download hook | BROKEN |
| Medical records | `/api/medical-record...` | GET/POST/PUT/DELETE | Bearer JWT | Patient/doctor/object ownership | JSON/path | Clinical record data | Medical record boundary | PARTIAL |
| Family | `/api/family/...` | GET/POST/PUT/DELETE | Bearer JWT | Group owner | JSON/path | Groups/members/goals | Family boundary | PARTIAL |
| Notifications | `/api/notifications...` | GET/POST/DELETE | Bearer JWT | Account owner | Filters/path | Notifications | Notification boundary | PARTIAL |
| Emergency | `/api/emergency/...` | GET/POST/PUT | Bearer JWT | Account owner/provider workflow | SOS/ambulance/alert JSON | Alert data | Emergency boundary | EXISTS BUT NEEDS VERIFICATION |
| Blood bank | `/api/blood-bank/...` | GET/POST/PUT | Mixed | Donor/request/provider workflow | Donor/request JSON | Donor/request/inventory | Blood bank boundary | PARTIAL |
| Pharmacy orders | `/api/pharmacy-orders...` | GET/POST/PUT | Bearer JWT | Patient/pharmacy | Order JSON/path | Order records | Pharmacy boundary | PARTIAL |
| Nursing | `/api/nursing/...` | GET/POST | Bearer JWT | Nurse for provider mutations | Request JSON/path | Nursing requests | Nurse boundary | PARTIAL |
| Hospitals | `/api/hospitals/<id>/review` | POST | Bearer JWT | Patient | Review JSON | Review | Directory feedback | EXISTS BUT NEEDS VERIFICATION |
| AI | `/api/ai/...` | GET/POST | Mixed, mostly Bearer JWT | Patient/account policy | JSON or multipart | AI result | Not wired in foundation | EXISTS BUT NEEDS VERIFICATION |
| Admin | `/api/admin/...` | GET/PATCH | Bearer JWT | Admin/super admin | JSON/path | Admin data | Admin feature boundary | EXISTS BUT NEEDS VERIFICATION |
| Feedback | `/api/feedback` | GET/POST/PATCH | Mixed | User; admin for review | Feedback JSON | Feedback records | Future support flow | EXISTS BUT NEEDS VERIFICATION |

## Contract findings

- The backend uses `POST /api/auth/logout` and revokes the server-side session;
  the mobile foundation clears secure storage even if logout returns an error.
- The backend's actual profile route is `/api/auth/profile`; the older
  `docs/API.md` entry naming `/api/auth/me` is not used by the mobile client.
- Multipart request and authenticated download hooks exist in the mobile client,
  but no medical file is uploaded or downloaded by the foundation.
- The existing audit reports missing or unverified tables for several route
  families (`lab_requests`, `radiology_requests`, notifications, family,
  vaccination, nursing, and others). Those features remain explicitly
  unconnected.
- No push notification endpoint/service was confirmed. Push notifications are
  **NOT CURRENTLY AVAILABLE**.