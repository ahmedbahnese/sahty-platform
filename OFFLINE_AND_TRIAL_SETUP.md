# Offline and trial setup

## Trial environment

The login page shows role shortcuts only when `VITE_ENABLE_DEMO_ACCOUNTS=true`. The shortcuts are for doctor, nurse, hospital, laboratory, pharmacy, radiology center, and blood bank. They fill the email and password from `VITE_DEMO_PASSWORD`; the value is not stored in the repository.

For the backend, set the Replit Secret `SEHATY_BOOTSTRAP_PASSWORD` and run migrations followed by:

```bash
python scripts/seed_demo_accounts.py
```

The seed script creates or updates missing role profiles without printing or storing the password. The API must be running with the same PostgreSQL database used by the web client for login and medical workflows to work.

## Offline and weak connectivity

The production web shell registers `public/sw.js` over HTTPS. The worker caches the shell and `offline.html`, uses a network-first strategy for navigation, and caches successful JavaScript, CSS, image, and font requests. If a route cannot be loaded while offline, the cached shell or the Arabic offline page is returned.

The React app also displays a temporary connection banner when the browser reports offline or online. Offline mode preserves previously loaded public pages and the visual shell; authenticated API actions, video rooms, chat sending, uploads, appointments, and other writes require a live API connection and must be retried after reconnection.

## Production safety

Remove `VITE_ENABLE_DEMO_ACCOUNTS` and `VITE_DEMO_PASSWORD` from the production frontend environment. Change the initial passwords and delete or disable all trial accounts before accepting real patients. Never commit `.env.local`, Replit Secrets, or passwords to GitHub.
