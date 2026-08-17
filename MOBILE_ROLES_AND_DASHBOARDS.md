# Sahty Mobile Roles and Dashboards

The Flask backend remains the authorization source of truth. Flutter only
renders a role-aware shell after the server returns the account's active roles.
Changing a local value or sending an arbitrary role to the API must never grant
access.

| Role | Existing Backend Role | Approval Required | Active Role | Dashboard Needed | APIs Available | Status |
|---|---|---|---|---|---|---|
| Patient / normal user | `patient` in `User.user_type`; patient is added to active roles | No for patient registration | `patient` | Patient shell | Doctors, directory, appointments, records, medications, prescriptions, family, emergency, notifications, blood bank | EXISTS BUT NEEDS VERIFICATION |
| Doctor | `doctor` in `User.user_type`; professional role tables also exist | Yes/conditional in source workflow | Server-issued `doctor` | Doctor provider shell | Doctor profile/availability, appointments, prescriptions, lab/radiology workflows | PARTIAL |
| Nurse | `nurse` in `PROVIDER_ROLES` and nursing role request workflow | Yes | Server-issued `nurse` | Nurse provider shell | Nursing request endpoints | PARTIAL |
| Hospital | `hospital` in `PROVIDER_ROLES` | Provider/admin approval in source | Server-issued `hospital` | Hospital provider shell | Hospital endpoints and shared workflows | PARTIAL |
| Pharmacy | `pharmacy` in `PROVIDER_ROLES` | Provider/admin approval in source | Server-issued `pharmacy` | Pharmacy provider shell | Pharmacy orders and prescription dispensing | PARTIAL |
| Laboratory | `lab` in `PROVIDER_ROLES` | Provider/admin approval in source | Server-issued `lab` | Laboratory provider shell | Lab request/result endpoints | PARTIAL |
| Radiology center | `radiology_center` in `PROVIDER_ROLES` | Provider/admin approval in source | Server-issued `radiology_center` | Radiology provider shell | Radiology request/report/image endpoints | PARTIAL |
| Blood bank | Blood-bank route family exists; no separate value was confirmed in `PROVIDER_ROLES` | Needs backend confirmation | Needs backend confirmation | Blood-bank provider shell | Blood-bank request/donor/inventory routes | NOT VERIFIED |
| Admin | `admin` in `User.user_type` | Privileged server-side assignment | Server-issued `admin` | Admin shell | `/api/admin/*` | EXISTS BUT NEEDS VERIFICATION |
| Super admin | `super_admin` in `User.user_type` | Privileged server-side assignment | Server-issued `super_admin` | Admin shell with higher-risk actions | Admin/user operations | NOT VERIFIED |

## Active-role contract

`src/routes/auth.py` issues a JWT whose `user_type` claim is the selected active
role. The server checks the requested role against `active_roles(user)`, which
always includes `patient` and adds active `UserRole` assignments. The mobile
client will:

1. Persist only the returned token and user summary in platform secure storage.
2. Display roles returned by the backend; it will not synthesize roles.
3. Send role switches to `/api/auth/switch-role`.
4. Treat `401` as session expiry and clear the local session.
5. Leave provider/admin dashboard modules unimplemented until endpoint and
   permission tests confirm the backend contract.

## Current safety findings

- The repository has two role representations (`User.user_type` and
  `Role`/`UserRole`), so approval and active-role semantics require runtime
  verification.
- Existing audit findings identify missing role-related tables in the tracked
  database and a web dashboard that calls admin APIs for non-admin roles.
- Flutter route guards, when added, will be convenience UX only. They will not
  replace backend role or object-level checks.