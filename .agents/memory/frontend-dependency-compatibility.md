---
name: Frontend dependency compatibility
description: Compatibility constraint discovered while restoring the imported React frontend
---

The imported frontend should not keep unused `react-day-picker` and `date-fns` direct dependencies unless their versions are aligned with the installed React version; they caused npm resolution failures during setup.

**Why:** The project uses a broad shadcn-style dependency set, and npm attempted to resolve an unused calendar package with incompatible peer requirements.

**How to apply:** Prefer removing unused direct dependencies over forcing npm peer resolution. Re-run the production build after package changes.