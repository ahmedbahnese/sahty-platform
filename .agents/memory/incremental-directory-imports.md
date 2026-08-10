---
name: Incremental directory imports
description: The imported healthcare directory can gain new category files after initial seeding.
---

Import each source category independently instead of treating any existing row as proof that the whole archive was imported.

**Why:** The initial seed contained four categories, while a later archive revision added blood banks. A table-level “already has rows” guard silently skipped the new category.

**How to apply:** Use a natural category key for the idempotency check, and preserve existing categories while importing only missing categories.