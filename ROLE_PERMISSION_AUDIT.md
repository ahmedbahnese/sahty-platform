# Sahty Role and Permission Audit

**Audit date:** 2026-08-12  
**Scope:** registration, JWT claims, frontend route guards, backend decorators, object ownership, and current role tables.

## Role sources

There are two role concepts:

1. `User.user_type` in `src/models/user.py`, with values used throughout the app such as `patient`, `doctor`, `admin`, `super_admin`, `pharmacy`, `lab`, `radiology_center`, `hospital`, and `nurse`.
2. `Role`, `UserRole`, and `ProfessionalRoleRequest` in `src/models/professional.py`.

`src/routes/auth.py` also computes active roles and supports role switching. This split is a design risk: a JWT/user display role, an approved professional role, and a requested role must not be treated as interchangeable.

## Role matrix

| Role | Frontend route access observed | Backend access observed | Current assessment |
|---|---|---|---|
| Anonymous | Home, public directories, doctors, hospitals, emergency/AI pages, login/register | Public list/detail/auth routes; compatible donors appear public | Public surface is broad; AI policy and donor privacy need correction |
| Patient | Dashboard, medical record, family, appointments, prescriptions, medication, vaccination, orders, nursing page | Patient-owned records/appointments/medication/family routes; some patient-only hospital review paths | Core role exists, but ownership and schema are unverified |
| Doctor | General dashboard, appointments, prescriptions, lab/radiology, nursing page due route list | Doctor profile/availability and mixed clinical routes | General dashboard calls admin APIs; server-side role matrix needs full testing |
| Nurse | General dashboard and nursing page | Nursing role request/request lifecycle routes | Nursing tables absent; route allows patients to see nursing page |
| Pharmacy | General dashboard and shared workflows | Pharmacy order/prescription operations in source | Provider approval and object-level permissions need testing |
| Lab | General dashboard and lab request page | Lab request/result routes in source | Current tables absent; dashboard mismatch |
| Radiology center | General dashboard and radiology page | Radiology request/report/share routes in source | Current tables absent; upload/share authorization needs testing |
| Hospital | General dashboard and shared pages | Hospital admin/provider operations in source | Provider ownership and admin boundary need testing |
| Admin | Admin dashboard only via `RoleRoute` | Admin route decorators and explicit admin checks | Source controls exist; bootstrap/privilege paths need runtime verification |
| Super admin | Admin dashboard | Admin and super-admin checks, bootstrap path | High-impact role; self-creation must be impossible |

## Findings

### R-001 — Public registration can request a role

The registration API accepts a `user_type` field. Public registration should not be allowed to create an admin or super-admin, and professional roles should normally enter an approval workflow. The current code path requires a targeted negative test for each privileged value.

### R-002 — Frontend guards are not authorization

`RoleRoute` prevents some navigation based on `user.user_type`, but every sensitive backend endpoint must independently enforce both role and object ownership. A user can bypass React routes by calling the API directly.

### R-003 — General dashboard role mapping is incorrect

`/dashboard` is allowed for patient and all listed professional roles, but `DashboardPage.jsx` fetches `/api/admin/stats`, `/api/admin/providers`, and `/api/admin/users`. Those endpoints are admin-only in source. This is a confirmed source-level workflow mismatch.

### R-004 — Nursing page route includes patients

`/nursing` is listed for patient and nurse roles in `src/App.jsx`. If the page exposes provider actions or request acceptance, the API must reject patient mutations and the UI should not present provider controls to patients.

### R-005 — Role model/database drift

The tracked DB lacks `roles`, `user_roles`, `professional_role_requests`, and nursing tables. Current activation/approval behavior cannot be trusted until a current schema is created and tested.

### R-006 — Active-role and selected-role semantics need a security contract

The auth code adds patient to active roles and supports switch-role. The audit must verify that a selected role is derived from an approved server-side assignment, not merely accepted from a token/request or displayed role.

### R-007 — Object-level ownership requires a matrix

The following cross-user cases must be tested explicitly:

- patient A reading/updating patient B’s records, medications, family members, appointments, prescriptions, notifications, and uploads;
- doctor A reading doctor B’s profile/private availability or another patient’s clinical data;
- provider A approving/dispensing another provider’s orders;
- nurse A accepting/completing another nurse’s request;
- admin versus super-admin changes to roles, users, settings, and audit logs;
- anonymous access to blood donors, public record tokens, and emergency data.

## Required permission policy before implementation

1. Public registration creates only a patient or an explicitly pending professional request.
2. Privileged roles are created/activated only by an authorized administrator.
3. The server derives effective permissions from database-backed approved roles.
4. Every record/file endpoint enforces patient/provider relationship and minimum necessary access.
5. Frontend route guards mirror the backend policy but are never the sole enforcement layer.
6. All deny cases return stable status codes and do not leak whether another user’s record exists.
7. Role changes revoke or rotate active sessions where required.

## Permission verdict

**Status: BROKEN / NOT SAFE TO ASSUME.** There are meaningful authorization controls, but the split role model, registration input, dashboard mismatch, missing role tables, and unverified object ownership prevent a release-ready permission conclusion.