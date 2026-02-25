# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

This is a Persian-language (RTL) psychology institute platform with a Django 4.2 REST API backend and a React 18 + TypeScript (Create React App) frontend. See `pedendencies/README.md` for full feature documentation.

### Services

| Service | Port | Command |
|---------|------|---------|
| Django backend | 8000 | `source venv/bin/activate && python pedendencies/manage.py runserver 0.0.0.0:8000` |
| React frontend | 3000 | `cd frontend && npm start` |

### Non-obvious caveats

- **`manage.py` lives at `pedendencies/manage.py`**, not the project root. It auto-adjusts `sys.path` and `cwd` to the project root (`/workspace`).
- **SQLite is the default dev database.** No Postgres or Redis required for basic dev; the settings fall back to SQLite and LocMemCache automatically. The SQLite DB file is at `pedendencies/db.sqlite3`.
- **Python 3.12 requires `setuptools`** installed in the venv (provides the `distutils` module needed by `django-jalali-date`). The update script handles this.
- **Node 20** is used (via nvm) because `react-scripts 5.0.1` has ESM/OpenSSL issues on Node 22+.
- **Frontend tests (`npm test`)** have a pre-existing failure: `axios` 1.x uses ESM and is not properly transformed by the jest config bundled with CRA 5. The `npm run build` command works correctly.
- **Backend tests** have one pre-existing failure in `app.appointments.tests.AppointmentModelTest.test_cancellation_fee_calculation`.
- **`populate_sample_data` management command** is not idempotent — it fails on second run due to unique constraints.
- **Superuser creation** requires `--first_name` and `--last_name` flags (custom User model uses email auth, no username field).
- **Lint/check**: Backend uses `python pedendencies/manage.py check`; frontend ESLint runs automatically during `npm start` and `npm run build`.
- **Backend tests**: `source venv/bin/activate && python pedendencies/manage.py test --no-input -v 2`
- **Frontend build**: `cd frontend && npm run build`
