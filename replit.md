# Tukutane - Social Event Management App

## Overview
A campus social event management web application built with Flask. Students can discover events, RSVP, create their own events, and manage their profiles.

## Tech Stack
- **Backend**: Python 3.12 + Flask 3.1.3
- **Database**: PostgreSQL (via `DATABASE_URL` env var) with SQLAlchemy ORM
- **Auth**: Flask-Login with password hashing (Werkzeug)
- **Forms**: Flask-WTF + WTForms
- **Migrations**: Flask-Migrate (Alembic)
- **Templates**: Jinja2 (server-side rendering)

## Project Structure
```
run.py              - App entrypoint (creates app, initializes DB, seeds data)
config.py           - Configuration class (SECRET_KEY, DATABASE_URL)
app/
  __init__.py       - Flask app factory (start_app())
  models.py         - SQLAlchemy models: User, Event, RSVP, Activity, CampusArea
  routes.py         - Flask Blueprint with all route handlers
  forms.py          - WTForms form classes
  utils.py          - populate_initial_data() seeder
  src/              - (additional source files)
templates/          - Jinja2 HTML templates
static/css/         - CSS stylesheets
migrations/         - Alembic migration files
```

## Key Features
- User signup/login with campus area and activity interests
- Event discovery dashboard with filters (by activity, campus area)
- RSVP system with capacity enforcement
- Event creation and management for organizers
- Profile editing
- Organizer dashboard to manage/edit/cancel events

## Running the App
- **Development**: `python run.py` (binds to 0.0.0.0:5000)
- **Production**: `gunicorn --bind=0.0.0.0:5000 --reuse-port run:app`

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Replit)
- `SECRET_KEY` - Flask secret key for sessions

## Dependencies
All in `requirements.txt`. Key packages: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, psycopg2-binary, gunicorn.
