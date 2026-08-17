# Sehaty (صحتي) — API Reference

Base URL (development): `http://localhost:5001`  
All authenticated endpoints require `Authorization: Bearer <JWT_TOKEN>`.  
Content-Type: `application/json` unless otherwise noted.

---

## Authentication

### POST /api/auth/register
Register a new user.

**Body**
```json
{
  "first_name": "أحمد",
  "last_name": "علي",
  "email": "ahmed@example.com",
  "password": "Secure123!",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "user_type": "patient|doctor|nurse|hospital|pharmacy|laboratory|radiology|blood_bank",
  "national_id": "12345678901234",
  "phone": "01012345678"        // optional
}
```
`user_type` is `patient` for the account's base access. Professional roles can be requested during registration or later through `POST /api/auth/apply-role`; they become usable only after server-side approval. `admin` and `super_admin` are never public registration roles.

**Response 201**
```json
{ "message": "تم التسجيل بنجاح", "token": "<JWT>", "user": { ... } }
```

---

### POST /api/auth/login
```json
{ "email": "ahmed@example.com", "password": "Secure123!" }
```
**Response 200** `{ "token": "<JWT>", "user": { ... } }`

---

### POST /api/auth/logout `[Auth]`
Revoke the current session server-side.

---

### POST /api/auth/change-password `[Auth]`
```json
{ "old_password": "...", "new_password": "..." }
```

---

### GET /api/auth/profile `[Auth]`
Returns the current user's profile and server-validated `active_roles`.

### POST /api/auth/switch-role `[Auth]`
Switches to a role already active for the account. The server rejects roles that are not assigned and approved.

```json
{ "role": "patient" }
```

### POST /api/auth/apply-role `[Auth]`
Creates a pending request for `doctor` or `nurse` without removing patient access. The requested role is inactive until approved by an administrator.

### GET /healthz
Lightweight liveness check. Returns HTTP 200 when the process is responding.

### GET /readyz
Readiness check. Returns HTTP 200 only when the application can reach its configured database.

### GET /api/health
API and database health check used by deployment health monitors.

---

## Doctors

### GET /api/doctors
Search / list approved doctors.  
**Query**: `specialty`, `city`, `name`, `page`, `per_page`

### GET /api/doctors/{id}
Doctor profile + availability slots.

### GET /api/doctors/{id}/slots `[Auth]`
Available appointment slots for a given `?date=YYYY-MM-DD`.

### PUT /api/doctors/profile `[Auth, Doctor]`
Update own profile.

### POST /api/doctors/availability `[Auth, Doctor]`
Set availability slots.

### POST /api/doctors/{id}/rate `[Auth, Patient]`
```json
{ "rating": 5, "comment": "ممتاز" }
```

---

## Appointments

### POST /api/appointments `[Auth]`
```json
{
  "doctor_id": 1,
  "appointment_date": "2026-08-01",
  "appointment_time": "10:00",
  "type": "in_person|video",
  "reason": "فحص دوري"
}
```

### GET /api/appointments `[Auth]`
List user's appointments. Query: `status`, `page`, `per_page`.

### GET /api/appointments/{id} `[Auth]`

### PUT /api/appointments/{id}/confirm `[Auth, Doctor]`
### PUT /api/appointments/{id}/complete `[Auth, Doctor]`
### PUT /api/appointments/{id}/cancel `[Auth]`

---

## Prescriptions

### POST /api/prescriptions `[Auth, Doctor]`
```json
{
  "patient_id": 5,
  "medications": [{ "name": "باراسيتامول", "dosage": "500mg", "frequency": "ثلاث مرات يومياً", "duration": "7 أيام" }],
  "diagnosis": "صداع",
  "notes": ""
}
```

### GET /api/prescriptions `[Auth]`
### GET /api/prescriptions/{id} `[Auth]`
### PUT /api/prescriptions/{id}/send-pharmacy `[Auth, Doctor]`
### PUT /api/prescriptions/{id}/dispense `[Auth, Pharmacy]`
### DELETE /api/prescriptions/{id} `[Auth, Doctor]`

---

## Medications

### POST /api/medications `[Auth]`
```json
{
  "medication_name": "أسبرين", "dosage": "100mg",
  "frequency": "مرة يومياً", "start_date": "2026-01-01",
  "end_date": "2026-06-01", "reminder_times": ["08:00"]
}
```
### GET /api/medications `[Auth]`
### GET /api/medications/{id} `[Auth]`
### PUT /api/medications/{id} `[Auth]`
### DELETE /api/medications/{id} `[Auth]`
### GET /api/medications/adherence-stats `[Auth]`
### POST /api/medications/{id}/log `[Auth]` — log a dose taken/skipped
### POST /api/medications/import-from-prescription `[Auth]`

---

## Vaccinations

### POST /api/vaccinations `[Auth]`
```json
{
  "vaccine_name": "COVID-19", "vaccination_date": "2025-01-15",
  "dose_number": 1, "batch_number": "LOT123",
  "next_dose_date": "2025-02-15"
}
```
### GET /api/vaccinations `[Auth]`
### PUT /api/vaccinations/{id} `[Auth]`
### DELETE /api/vaccinations/{id} `[Auth]`

Family member vaccinations:
### GET /api/family-vaccinations/{member_id} `[Auth]`
### POST /api/family-vaccinations/{member_id} `[Auth]`

---

## Blood Bank

### GET /api/blood-bank/requests
List active blood requests. Query: `blood_type`, `city`, `urgency_level`, `page`, `per_page`.

### POST /api/blood-bank/requests `[Auth]`
```json
{
  "patient_name": "سارة", "blood_type": "O+", "units_needed": 2,
  "hospital_name": "مستشفى القاهرة", "city": "القاهرة",
  "urgency_level": "urgent|critical|routine",
  "contact_phone": "01012345678",
  "needed_by_date": "2026-08-15T00:00:00",
  "description": ""
}
```

### POST /api/blood-bank/donors/register `[Auth]`
```json
{
  "blood_type": "A+", "city": "الجيزة", "weight": 75, "age": 30,
  "district": "الدقي", "has_chronic_diseases": false,
  "current_medications": "", "available_for_emergency": true
}
```

### GET /api/blood-bank/donors/me `[Auth]`
### PUT /api/blood-bank/donors/me `[Auth]`
### GET /api/blood-bank/inventory `[Auth]`
### GET /api/blood-bank/stats
```json
{
  "total_donors": 0, "active_requests": 0,
  "total_donations": 0, "critical_requests": 0
}
```

---

## Hospitals

### GET /api/hospitals
Query: `search`, `city`, `type` (public|private|specialized), `emergency=1`, `verified=1`, `page`, `per_page`.

**Response 200**
```json
{
  "hospitals": [{ "id":1, "name":"...", "city":"...", "phone":"...",
    "has_emergency":true, "rating":4.2, "latitude":30.0, "longitude":31.2, ... }],
  "total": 20, "page": 1, "pages": 2
}
```

### GET /api/hospitals/{id}
Includes `departments[]` and last 5 approved `reviews[]`.

### POST /api/hospitals `[Auth, Admin]`
### PUT /api/hospitals/{id} `[Auth, Admin]`
### DELETE /api/hospitals/{id} `[Auth, Admin]` — soft delete

### GET /api/hospitals/{id}/departments
### POST /api/hospitals/{id}/departments `[Auth, Admin]`

### POST /api/hospitals/{id}/review `[Auth, Patient]`
```json
{
  "overall_rating": 4, "cleanliness_rating": 5, "staff_rating": 4,
  "facilities_rating": 3, "waiting_time_rating": 4,
  "review_title": "تجربة ممتازة", "review_text": "...", "would_recommend": true
}
```

### GET /api/emergency-services
Query: `city`, `type`.

---

## Medical Records

### GET /api/medical-records `[Auth]`
### POST /api/medical-records/diseases `[Auth]`
### POST /api/medical-records/surgeries `[Auth]`
### POST /api/medical-records/allergies `[Auth]`
### POST /api/medical-records/lab-tests `[Auth]`
### POST /api/medical-records/radiology `[Auth]`
### DELETE /api/medical-records/{type}/{id} `[Auth]`

---

## Lab & Radiology

### POST /api/lab-requests `[Auth]` — multipart supported
### GET /api/lab-requests `[Auth]`
### GET /api/lab-requests/{id} `[Auth]`
### PUT /api/lab-requests/{id}/approve `[Auth, Doctor]`
### PUT /api/lab-requests/{id}/reject `[Auth, Doctor]`
### POST /api/lab-requests/{id}/results `[Auth, Lab]` — multipart
### POST /api/lab-requests/{id}/notify `[Auth, Lab]`

### POST /api/radiology-requests `[Auth]`
### GET /api/radiology-requests `[Auth]`
### GET /api/radiology-requests/{id} `[Auth]`
### PUT /api/radiology-requests/{id}/reject `[Auth, Doctor]`
### POST /api/radiology-requests/{id}/images `[Auth, Radiology]` — multipart
### POST /api/radiology-requests/{id}/report `[Auth, Radiology]`
### POST /api/radiology-requests/{id}/share `[Auth, Radiology]`

---

## Family Health

### GET /api/family/groups `[Auth]`
### POST /api/family/groups `[Auth]`
### GET /api/family/groups/{id} `[Auth]`
### PUT /api/family/groups/{id} `[Auth]`
### DELETE /api/family/groups/{id} `[Auth]`
### GET /api/family/groups/{id}/members `[Auth]`
### POST /api/family/groups/{id}/members `[Auth]`
### GET /api/family/members/{id} `[Auth]`
### PUT /api/family/members/{id} `[Auth]`
### DELETE /api/family/members/{id} `[Auth]`
### POST /api/family/members/{id}/records `[Auth]`
### GET /api/family/goals `[Auth]`
### POST /api/family/goals `[Auth]`

---

## Notifications

### GET /api/notifications `[Auth]`
Query: `unread_only=true`, `page`, `per_page`.

### GET /api/notifications/unread-count `[Auth]`
### PUT /api/notifications/{id}/read `[Auth]`
### PUT /api/notifications/read-all `[Auth]`
### DELETE /api/notifications/{id} `[Auth]`
### DELETE /api/notifications/clear-all `[Auth]`

---

## Emergency

### POST /api/emergency/sos `[Auth]` — SOS alert
### POST /api/emergency/ambulance `[Auth]` — ambulance request
### GET /api/emergency/alerts `[Auth]`
### GET /api/family-contacts `[Auth]`
### POST /api/family-contacts `[Auth]`
### DELETE /api/family-contacts/{id} `[Auth]`

---

## Pharmacy Orders

### POST /api/pharmacy-orders `[Auth]`
### GET /api/pharmacy-orders `[Auth]`
### GET /api/pharmacy-orders/{id} `[Auth]`
### PUT /api/pharmacy-orders/{id}/status `[Auth, Pharmacy]`

---

## Feedback

### POST /api/feedback `[Auth]`
```json
{ "subject": "...", "message": "...", "category": "general|bug|feature", "rating": 5 }
```
### GET /api/feedback `[Auth, Admin]`
### PATCH /api/feedback/{id} `[Auth, Admin]`
```json
{ "status": "new|reviewed|resolved", "admin_notes": "..." }
```

---

## AI Assistant

### POST /api/ai/chat `[Auth]`
```json
{ "message": "...", "conversation_id": null }
```

### POST /api/ai/symptom-checker `[Auth]`
```json
{ "symptoms": ["صداع", "حمى"], "age": 30, "gender": "male" }
```

### POST /api/ai/analyze-image `[Auth]` — multipart image upload
### POST /api/ai/analyze-document `[Auth]` — multipart PDF/image

---

## Admin

### GET /api/admin/stats `[Auth, Admin]`
### GET /api/admin/users `[Auth, Admin]`
### PUT /api/admin/users/{id}/status `[Auth, Admin]`
### GET /api/admin/providers/pending `[Auth, Admin]`
### PUT /api/admin/providers/{id}/approve `[Auth, Admin]`
### PUT /api/admin/providers/{id}/reject `[Auth, Admin]`
### GET /api/admin/audit-logs `[Auth, Admin]`

---

## File Uploads

Uploaded files are served from:
```
GET /api/uploads/<subdir>/<filename>
```
Auth required. Files include lab results, radiology images, and prescription documents.

---

## Error Format

All error responses follow:
```json
{ "message": "وصف الخطأ بالعربية" }
```
HTTP status: `400` validation, `401` unauthenticated, `403` forbidden, `404` not found, `500` server error.

---

## Authentication Notes

- JWT tokens are returned on login/register and must be sent as `Authorization: Bearer <token>`.
- Tokens are revocable server-side via `POST /api/auth/logout`.
- Role-based access: `patient`, `doctor`, `admin`, `super_admin`, `pharmacy`, `lab`, `radiology`.
