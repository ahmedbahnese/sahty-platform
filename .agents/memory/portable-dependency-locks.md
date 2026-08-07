---
name: Portable dependency locks
description: Making imported Node projects installable outside their original workspace
---

Imported Node lockfiles may preserve private workspace registry URLs even when `package.json` has no platform-specific dependency.

**Why:** A lockfile that points to an inaccessible private registry makes clean installs fail outside the originating workspace.

**How to apply:** Before publishing or handing off an imported project, inspect lockfile `resolved` URLs and replace workspace-only registries with the package manager's public registry when the package sources are public.