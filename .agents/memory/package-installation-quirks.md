---
name: Package installation quirks
description: Replit package installation behavior for imported Node projects
---

For imported Node projects, the managed package installer can install the
workspace manifest by targeting the local package (`.`). Supplying a manually
assembled list of version ranges is less reliable because registry availability
may differ from the versions recorded in the imported manifest.

**Why:** A fresh imported workspace may have no `node_modules`, while manually
reconstructed ranges can fail even when the checked-in lockfile is valid.

**How to apply:** Prefer the existing `package.json`/lockfile and install the
local package before diagnosing a frontend build as an application problem.