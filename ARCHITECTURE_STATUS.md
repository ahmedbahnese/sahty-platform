# Architecture implementation status

| Layer | Target architecture | Current implementation | Status |
|---|---|---|---|
| Web Client | React/Vite → REST API | React/Vite pages use HTTP `fetch` against `/api/...`; no direct DB client was found | WORKING |
| Mobile Client | Flutter → REST API | Flutter API client uses `API_BASE_URL` from `--dart-define`; default emulator URL is documented for development | WORKING / NOT VERIFIED on native toolchain |
| REST API | Flask Backend | Flask Blueprints expose authentication, directory, medical, appointment, prescription, emergency, notification, and role-specific routes | WORKING on SQLite test runtime |
| Database | PostgreSQL production; SQLite test/dev | Flask config rejects SQLite in `FLASK_ENV=production`; PostgreSQL production connection was not available for this verification | PARTIAL |
| Storage | External/S3-compatible medical file storage | Current upload routes save files under local `static/uploads`; an external production storage backend is not yet verified | PARTIAL |
| External APIs | Server-side integrations only | AI service reads server-side OpenAI environment variables; Google Maps links are generated as public links; no client-side secret was found | PARTIAL |
| Security boundary | Clients never hold DB credentials or server Secrets | No database URI or server Secret appears in Web/Mobile client code; authentication is through Flask sessions/JWT | WORKING |

## Required production follow-up

Before production acceptance, configure a managed PostgreSQL `DATABASE_URL`, configure an external persistent Storage provider for medical files, and test the full upload/download authorization path on Replit. Keep all integration keys in Replit Secrets and expose only public configuration such as `API_BASE_URL` to Flutter.
