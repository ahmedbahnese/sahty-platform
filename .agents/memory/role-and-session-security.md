---
name: Role and session security
description: Security boundary for role assignment and persisted session invalidation
---

Role-protected user administration must enforce role assignment on the server, not only restrict which endpoints a role can call. A regular administrator must never be able to create or promote a super-admin account.

**Why:** Allowing an administrator to assign the highest role creates a privilege-escalation path that defeats deletion and administration boundaries.

**How to apply:** Keep super-admin role assignment restricted to an existing super-admin and validate requested roles against an explicit allowlist.

Session revocation must be committed independently from audit logging.

**Why:** An audit-log failure must not leave a supposedly logged-out token usable.

**How to apply:** persist the revoked state first, then write audit data as best effort with its own rollback boundary.