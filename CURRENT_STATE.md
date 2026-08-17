# Sehaty Platform — Current State

**Inventory date:** 2026-08-17
**Repository:** https://github.com/ahmedbahnese/sahty-platform
**Baseline branch:** `main`
**Baseline commit:** `a88bcfe` (`fix: use public npm registry in lockfile`)

## Executive summary

Sehaty is an existing Arabic healthcare platform with a React/Vite frontend, Flask/SQLAlchemy backend, SQLite development database, migrations directory, automated backend tests, and a Flutter foundation under `/mobile`. The repository is functional enough to build the frontend and pass the existing backend test suite, but it is not yet release-ready: several workflows are partial, some directory pages still render local sample data, professional dashboards are not fully separated, and the migration/deployment/database state requires further hardening.

## Verified baseline

| Area | Status | Evidence |
|---|---|---|
| Git baseline | WORKING | `main` matches `origin/main` at `a88bcfe`; `origin/replit-agent` remains separate and was not modified. |
| Frontend install | WORKING | `npm ci` succeeds after the public-registry lockfile correction. |
| Frontend lint | PARTIAL | `npm run lint` exits successfully with React Hooks/Fast Refresh warnings. |
| Production web build | WORKING | `npm run build` succeeds. |
| Python syntax | WORKING | `python3 -m compileall -q .` succeeds. |
| Backend tests | WORKING | Existing suite passes: 101 tests. |
| Flutter production build | NOT VERIFIED | The repository contains a Flutter foundation, but Android/iOS release builds were not verified in this environment. |
| iOS build | NOT VERIFIED | macOS/Xcode/signing are unavailable in this Linux environment. |

## Architecture inventory

The backend is organized into SQLAlchemy models, Flask blueprints, authentication/authorization helpers, AI services, and database seed/import utilities. The frontend contains role-aware routing, patient and professional pages, healthcare directory pages, medical records, medications, prescriptions, vaccinations, family health, emergency, AI, and request workflows. The mobile directory currently contains Flutter project metadata, dependency lockfiles, and foundation documentation.

The database model inventory includes users, sessions, roles, professional applications, providers, patients, doctors, hospitals, appointments, medical records, medications, prescriptions, vaccinations, family health, notifications, laboratory/radiology requests, blood bank, emergency, and healthcare directory entities. The repository also contains migration scaffolding, but the migration history must be reviewed against the current model set before production use.

## Known gaps to address

The existing audit files identify the following high-impact gaps: database schema/migration drift; production deployment without a tested frontend build pipeline and durable database default; shared provider dashboard behavior; static sample data in labs/pharmacies/radiology directory pages; inconsistent public/protected AI policy; raw AI service error handling; upload authorization; donor privacy; role registration and role switching; JWT storage in browser localStorage; incomplete service-worker behavior; and incomplete frontend/mobile/production smoke coverage.

The present implementation does contain improvements over the earlier audit baseline, including server-side checks in several file-access paths and public-role handling in registration. Each claim must continue to be verified against current code and tests rather than copied from historical audit documents.

## Release decision at baseline

**Classification: PARTIAL / NOT VERIFIED for production release.** The existing automated backend suite and web build are healthy, but healthcare-data security, migration integrity, production persistence, role-specific workflows, and mobile release verification require additional work. This document is a baseline and must be updated after each completed logical phase.
