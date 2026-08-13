# Sahty Database Audit

**Audit date:** 2026-08-12  
**Observed database:** `src/database/app.db` (tracked SQLite file)

## Database architecture

- SQLAlchemy is initialized in `main.py` through Flask-SQLAlchemy.
- `DATABASE_URL` can select PostgreSQL; otherwise the application defaults to the repository-local SQLite file.
- Startup calls `db.create_all()` and then runs a list of ad-hoc `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` statements.
- Flask-Migrate is attached, but `migrations/` contains only `env.py`, `alembic.ini`, `script.py.mako`, and README material. No `migrations/versions` revision files were found.
- The application imports a bundled healthcare directory and attempts an idempotent import on startup.

## Tracked SQLite inventory

The tracked file contains these 24 tables:

`admins`, `allergies`, `appointment_history`, `appointment_ratings`, `appointments`, `audit_logs`, `blood_donations`, `blood_donors`, `blood_inventory`, `blood_request_responses`, `blood_requests`, `doctor_availability`, `doctors`, `drug_database`, `emergency_services`, `hospital_departments`, `hospital_reviews`, `hospitals`, `medical_records`, `medication_logs`, `medication_schedules`, `medications`, `patients`, `specializations`, `system_owners`, `system_settings`, `users`.

## Source model inventory and schema comparison

| Source model/table group | Tables declared by current source | Present in tracked DB? | Assessment |
|---|---|---:|---|
| Identity | `users`, `user_sessions` | `users` yes; `user_sessions` no | Authentication persistence is not proven against the tracked DB |
| Patient | `patients`, `medical_records`, `allergies` | Yes | Core patient schema present |
| Admin | `system_owners`, `admins`, `system_settings`, `audit_logs` | Yes | Present, but runtime compatibility unverified |
| Doctor | `doctors`, `doctor_availability`, `specializations` | Yes | Present |
| Professional roles | `roles`, `user_roles`, `professional_role_requests`, `nurse_profiles`, `nursing_service_requests`, `nursing_request_status_history` | No | Current role/nursing workflows are schema-incomplete in the tracked file |
| Provider onboarding | `provider_registrations` | No | Provider review path is not represented in current DB |
| Appointments | `appointments`, `appointment_history`, `appointment_ratings` | Yes | Present |
| Prescriptions | `prescriptions`, `prescription_items` | No | Prescription routes cannot be assumed to work on this file |
| Medication | `medications`, `medication_schedules`, `medication_logs`, `pharmacy_orders`, `drug_database` | Partially; `pharmacy_orders` missing | Medication tracking/order split is inconsistent |
| Notifications | `notifications` | No | Notification bell persistence is unverified |
| Medical record extensions | `diseases`, `surgeries`, `vaccinations`, `lab_tests`, `radiology_scans`, `blood_gas_readings`, `ecg_records`, `medical_history` | No | Newer record pages rely on absent tables |
| Lab/radiology requests | `lab_requests`, `radiology_requests` | No | Request pages are schema-incomplete against tracked DB |
| Family health | `family_groups`, `family_members`, `family_member_health_records`, `family_health_goals` | No | Family account workflow is not represented |
| Emergency | `emergency_alerts`, `family_contacts` | No; `emergency_services` is present | Source route/model contract differs from tracked schema |
| Hospitals | `hospitals`, `hospital_departments`, `hospital_reviews`, `emergency_services` | Yes | Legacy hospital schema present |
| Blood bank | `blood_donors`, `blood_requests`, `blood_request_responses`, `blood_donations`, `blood_inventory` | Yes | Present |
| Current Egypt directory | `egypt_governorates`, `egypt_cities`, `egypt_facility_types`, `egypt_ownership_types`, `egypt_facilities`, `healthcare_directory_records` | No | Directory import/startup state is not represented in the tracked DB |

This is a source-to-file comparison, not a claim that a fresh application start cannot create tables. It demonstrates that the checked-in data file is stale relative to current source and that the repository has no versioned, repeatable upgrade path.

## Data flow and ownership observations

- Patient records generally carry `patient_id`; appointments carry patient/doctor and optional family-member references.
- Provider and professional roles are split between `User.user_type` and separate role/request models.
- Uploads are represented as filesystem paths or data columns depending on the feature. File ownership is not uniformly represented by a dedicated access-control record.
- Audit-log and notification models exist in source, but both are absent from the tracked database.
- The directory importer is intended to be incremental/idempotent, but execution against a fresh and existing database was not possible without the Python runtime dependencies.

## Migration and deployment risks

1. `db.create_all()` can create absent tables but cannot safely evolve existing columns, constraints, indexes, or data.
2. Ad-hoc startup `ALTER TABLE` statements are not a substitute for reviewed migration history and may behave differently across SQLite/PostgreSQL versions.
3. No migration revision is available for a production database to upgrade.
4. `render.yaml` does not run `flask db upgrade`.
5. The default `DATABASE_URL` behavior points to local SQLite, while the deployment definition does not declare a managed persistent database.
6. `src/database/app.db` is tracked. Any real or demo healthcare data in it is part of the repository artifact and needs a privacy/retention decision.

## Required database verification plan

1. Create a clean temporary database and run the application initialization.
2. Create a copy of the tracked database and run the same initialization.
3. Compare `inspect(db.engine).get_table_names()` and columns with SQLAlchemy metadata.
4. Run migrations from an empty database and from the current production-like schema.
5. Exercise registration, session revocation, records, appointments, prescriptions, family health, notifications, uploads, emergency, and directory routes.
6. Repeat against PostgreSQL if it is the target production engine.
7. Verify restart persistence and concurrent request behavior.

## Database verdict

**Status: BROKEN for release readiness / IMPLEMENTED BUT NOT VERIFIED for source models.** The application has extensive persistence code, but the checked-in database and migration system do not establish a trustworthy current schema.