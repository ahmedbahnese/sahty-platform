---
name: Security regression verification
description: How to validate privacy and authorization claims in imported applications
---

Imported project summaries can describe a security fix that is not present in the current source. Treat every privacy claim as unverified until an endpoint-level regression test checks both the response shape and a cross-owner access attempt.

**Why:** A stale summary may report that sensitive fields or ownership checks were removed while the running route still exposes or mutates them.

**How to apply:** Add focused tests for role activation, cross-patient reads/writes, protected files, and public response fields before declaring a security stabilization task complete.