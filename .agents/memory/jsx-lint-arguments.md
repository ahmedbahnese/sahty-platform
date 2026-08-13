---
name: JSX lint arguments
description: Why this frontend's ESLint configuration ignores uppercase callback arguments.
---

Core ESLint `no-unused-vars` can report JSX component arguments such as `icon: Icon` as unused when the React ESLint plugin is not enabled, even though JSX renders the component.

**Why:** Enabling the React plugin would be a larger toolchain change for this stabilization phase; an uppercase argument ignore pattern preserves the existing stack and keeps real unused variables as errors.

**How to apply:** Keep `argsIgnorePattern: '^[A-Z_]'` scoped with the existing `no-unused-vars` rule unless the project later adopts the React ESLint plugin.