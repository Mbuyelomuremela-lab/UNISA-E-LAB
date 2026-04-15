# Sunnyside Lab Portal

A Flask-based web system for managing interns, assets, visitors, and admin oversight at campus labs. The system includes intern 2-step authentication with QR code and geolocation verification.

## Tech Stack

- Python Flask
- SQLite (with SQLAlchemy ORM)
- Flask Blueprints
- Flask-Login
- Flask-WTF / CSRF Protection
- Werkzeug password hashing
- QRCode generation
- HTML / CSS / JS
- Bootstrap 5

## Project Structure

- `app.py` — Application factory and blueprint registration
- `config.py` — Application configuration
- `models/__init__.py` — SQLAlchemy models
- `routes/auth.py` — Login, QR, location validation, logout
- `routes/intern.py` — Intern dashboard, asset and visitor CRUD
- `routes/admin.py` — Admin dashboards, users, assets, visitors, login activity
- `services/qr_service.py` — QR code generation
- `services/geolocation_service.py` — Lab radius validation
- `services/security.py` — Session timeout helper
- `templates/` — Jinja2 templates for login, intern and admin portals
- `static/css/style.css` — Custom interface styling
- `static/js/` — UI behavior and modal script logic
- `seeds.py` — Populate sample provinces, labs, and accounts

## Setup

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies for local testing:

```bash
pip install -r requirements-local.txt
```

> `requirements-local.txt` omits PostgreSQL build dependencies so Windows users can run the app locally with SQLite.

3. Copy the example environment file and update values locally:

```bash
copy .env.example .env
```

4. Seed the database locally:

```bash
python seeds.py
```

5. Run the application:

```bash
python app.py
```

6. Open the browser at:

```text
http://localhost:5000
```

## Deployment

This project is configured for production deployment using `gunicorn` and an environment-backed database.

- Local development uses SQLite by default.
- Production should use a managed database and set `DATABASE_URL`.
- `sqlite:///app.db` is fine for local testing but not recommended for deployed apps because platform disks are often ephemeral.

### Heroku deployment example

1. Create the app:

```bash
heroku create
```

2. Add a database addon:

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

3. Set required environment variables:

```bash
heroku config:set SECRET_KEY="your-secret-key" SITE_URL="https://your-app-name.herokuapp.com"
```

4. Push code to Heroku:

```bash
git push heroku main
```

5. Run database seeds on Heroku:

```bash
heroku run python seeds.py
```

6. Configure email settings if using outbound email:

```bash
heroku config:set EMAIL_HOST="smtp.example.com" EMAIL_PORT=587 EMAIL_USERNAME="user@example.com" EMAIL_PASSWORD="your-password" EMAIL_USE_TLS=True EMAIL_DEFAULT_SENDER="noreply@example.com"
```

7. Open the app:

```bash
heroku open
```

> If you want a quick local GitHub upload helper, run `push_to_github.bat` after installing Git and replacing the repo URL.

### Render deployment example

1. Push your repo to GitHub if it is not already pushed.

2. In Render, create a new Web Service and connect your GitHub repository.

3. Use the following settings:
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Branch: `main`

4. Set the required environment variables in Render:

```text
SECRET_KEY
DATABASE_URL
SITE_URL
EMAIL_HOST
EMAIL_PORT
EMAIL_USERNAME
EMAIL_PASSWORD
EMAIL_USE_TLS
EMAIL_USE_SSL
EMAIL_DEFAULT_SENDER
```

5. Deploy the service.

If you want, you can also add `render.yaml` to the repository so Render can auto-detect the service configuration.

### Environment variables

Required for deployment and local configuration:

- `SECRET_KEY`
- `DATABASE_URL`
- `SITE_URL`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USERNAME`
- `EMAIL_PASSWORD`
- `EMAIL_USE_TLS` / `EMAIL_USE_SSL`
- `EMAIL_DEFAULT_SENDER`

## Seeded Accounts

- Admin: `admin@sunnyside.edu` / `Admin@123`
- Intern: `intern@sunnyside.edu` / `Intern@123`

## Features

- Admin / Intern role separation
- Intern login with email + password and QR scan geolocation verification
- Admin dashboard with overview, user management, asset tracking, visitor history, and login activity
- Modal-based edit forms for admin users and assets
- Admin lab and province CRUD with geolocation and Google Maps links
- Visitor registration and asset management for interns
- CSRF protection and secure password hashing
- Session timeout after inactivity

## Notes

- The app uses SQLite by default but can migrate to MySQL by updating `DATABASE_URL` in `config.py`.
- The system supports later frontend migration to React by replacing templates and AJAX routes.
