# Sehaty services activation

## Medical consultations

The API now exposes `POST /api/consultations` for a patient to request a doctor consultation, `GET /api/consultations` and `GET /api/consultations/<id>` for authorized participants, `POST /api/consultations/<id>/messages` for authenticated chat, and `POST /api/consultations/<id>/attachments` for medical reports, analyses, images, and PDF files up to 25 MB. The consultation generates a unique meeting room using `VIDEO_MEETING_BASE_URL` and stores the meeting URL, diagnosis, treatment plan, prescription payload, referral details, and emergency flag. A doctor can close the consultation through `POST /api/consultations/<id>/complete`.

The React page is available at `/consultations` and `/consultations/:id`. It includes the video room link, chat, attachment upload, and doctor result form. The video room defaults to a Jitsi-compatible URL for testing; production deployments should set `VIDEO_MEETING_BASE_URL` to the organization-approved provider.

## Home visits

The existing nursing workflow was extended so a patient can request a visit as before, while an authenticated doctor or nurse can create a request for a target patient by sending `patient_id`. The request persists `requester_role`, `requested_by_user_id`, `doctor_id`, `provider_role`, and `request_type`. The doctor can use `/nursing` to request a nursing home visit or another service, and the approved nurse can accept, reject, and complete the visit through the existing workflow.

## Digital blood bank

Blood requests now persist `component_type` (`whole_blood`, `plasma`, `platelets`, `cryoprecipitate`, or `other`), `is_irradiated`, the stamped transfusion document path/name, and a document workflow status. The frontend submits the document using `multipart/form-data`. A request without the document is saved as `document_required` but cannot be forwarded. The patient can upload the document through `POST /api/blood-bank/requests/<id>/document`, and an authorized hospital, blood-bank, or admin user can forward only a verified request using `POST /api/blood-bank/requests/<id>/forward`. Active blood-bank accounts receive notifications for forwarded requests.

## AI widget

The closed floating assistant now calculates the dimensions of the closed button while dragging on touch devices, so it stays movable and does not clamp against the dimensions of the expanded chat window.

## Bootstrap accounts

The application supports these default email addresses:

| Role | Email | Secret variables |
|---|---|---|
| Administrator | `admin@sehaty.com` | `ADMIN_PASSWORD` or `SEHATY_BOOTSTRAP_PASSWORD` |
| Doctor | `doctor@sehaty.com` | `DOCTOR_PASSWORD` or shared bootstrap secret |
| Nurse | `nurse@sehaty.com` | `NURSE_PASSWORD` or shared bootstrap secret |
| Hospital | `hospital@sehaty.com` | `HOSPITAL_PASSWORD` or shared bootstrap secret |
| Pharmacy | `pharma@sehaty.com` | `PHARMACY_PASSWORD` or shared bootstrap secret |
| Laboratory | `lab@sehaty.com` | `LAB_PASSWORD` or shared bootstrap secret |
| Radiology | `rad@sehaty.com` | `RADIOLOGY_PASSWORD` or shared bootstrap secret |
| Blood bank | `bloodbank@sehaty.com` | `BLOOD_BANK_PASSWORD` or shared bootstrap secret |

For a new Replit environment, add `SEHATY_BOOTSTRAP_PASSWORD` as a Replit Secret with the initial password provided by the system owner. The value is read only from the environment and is never stored in GitHub. Existing passwords are preserved on restart; change all initial passwords immediately after the first successful login through the password-management flow.

After setting PostgreSQL and the required secrets, run migrations before the first login:

```bash
flask db upgrade
bash scripts/import_directory_csv.py
bash scripts/replit-api-run.sh
```

The production migration is `0004_consultations_and_blood_workflow`.
