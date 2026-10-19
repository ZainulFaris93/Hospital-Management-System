# StarCare: Hospital Management System

[![Tests](https://github.com/ZainulFaris93/Hospital-Management-System/actions/workflows/tests.yml/badge.svg)](https://github.com/ZainulFaris93/Hospital-Management-System/actions/workflows/tests.yml)
[![Live demo](https://img.shields.io/badge/demo-live-2ea44f)](https://starcare-hospital.onrender.com/login_page)

A role-based hospital management web app built with **Python and Django**. Patients book appointments, doctors manage their schedules, and admins run the hospital.

**Live demo:** https://starcare-hospital.onrender.com/login_page

> The automated tests, CI and deployment setup were added with help from an AI assistant. See [Automated tests](#automated-tests-added-with-ai-assistance) below.

| Role    | Username   | Password      |
|---------|------------|---------------|
| Admin   | `admin`    | `Admin@123`   |
| Doctor  | `dr.meera` | `Doctor@123`  |
| Patient | `rahul`    | `Patient@123` |

On the login page, click a role to fill in its credentials. The demo runs on Render's free plan, so the first load after it has been idle can take up to a minute. Demo data resets automatically, and the shared demo accounts can't be deleted or have their passwords changed.

## Features

- **Three roles, three dashboards:** admin, doctor and patient, each with its own login
- **Appointment booking** with time-slot selection, double-booking prevention, one visit per doctor per day and a daily limit per doctor
- **Admin tools:** doctor approval, department management, add doctors and patients, filters, and searchable appointment history
- **Doctor tools:** today's schedule, mark appointments consulted or not consulted, appointment history
- **AJAX** for live counts and status updates without page reloads
- **Email notifications** for registration and approvals

## Automated tests (added with AI assistance)

> **Transparency note:** I built the application itself. The automated test suites, the GitHub Actions CI pipeline, the demo data and deployment setup, and the fixes listed below were added with help from an AI assistant (Claude). I'm a manual tester by profession and I'm using these tests to learn test automation.

Every push runs two test suites on GitHub Actions:

| Suite | Tool | What it covers |
|-------|------|----------------|
| Unit & integration (34 tests) | Django `TestCase` | Login per role, role-based access, booking rules, appointment status workflow, registration emails, demo-mode protections |
| End-to-end (39 runs) | Playwright + TypeScript | Browser journeys on desktop and mobile: demo login, access control, and the full appointment lifecycle across all three roles |

The latest Playwright report is published at https://zainulfaris93.github.io/Hospital-Management-System/.

### Issues found and fixed during that review

- **Missing authorization:** some admin URLs (including delete patient/doctor) could be opened without the right role. Every view now checks the user's role, and the JSON endpoints return 401/403.
- **Booking rules checked only in the browser:** the server now also rejects past dates, unknown time slots, unapproved doctors and repeat bookings with the same doctor on the same day.
- **Silent failure** when booking a fully booked day. It now shows a message.
- **"Fully booked" warning** was hidden immediately by the next `if/else` block.
- **Timezone bug:** the earliest selectable date used UTC instead of local time.
- **Invalid dates** in the availability API caused a 500 error. They now return 400.

## Tech stack

Python · Django 5 · Django ORM · MySQL (local) / SQLite (demo) · JavaScript · AJAX · Bootstrap

## Run locally

```bash
cd hospital_project
pip install -r requirements.txt
export USE_SQLITE=True DEMO_MODE=True    # Windows PowerShell: $env:USE_SQLITE="True"; $env:DEMO_MODE="True"
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

To use MySQL instead, create a `hospital_db` database, run `pip install mysqlclient`, and leave out `USE_SQLITE`.

### Run the tests

```bash
# Django tests
cd hospital_project
USE_SQLITE=True python manage.py test hospital_app

# Playwright tests (they start the server themselves)
cd ../e2e
npm install
npx playwright install chromium
npx playwright test
npx playwright show-report
```

## Deployment

`render.yaml` defines the Render service. Each start runs the migrations, loads the demo data (`python manage.py seed_demo`) and launches Gunicorn. Every push to `master` redeploys automatically.

---
Built by [Zainul Faris V K](https://zainulfaris93.github.io)
