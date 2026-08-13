---
name: Migration startup order
description: Flask-Migrate imports the application before running a database command
---

Application imports used by Flask-Migrate must not perform database queries or
seed writes before the migration command runs.

**Why:** The CLI imports the Flask application to discover the migration
extension. Startup schema/data side effects then run against an unupgraded
database and can fail before Alembic gets control.

**How to apply:** Keep schema changes in revisions and invoke optional
reference-data seeding only after the explicit upgrade step.