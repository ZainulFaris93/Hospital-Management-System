# StarCare: Hospital Management System

[![Tests](https://github.com/ZainulFaris93/Hospital-Management-System/actions/workflows/tests.yml/badge.svg)](https://github.com/ZainulFaris93/Hospital-Management-System/actions/workflows/tests.yml)
[![Live demo](https://img.shields.io/badge/demo-live-2ea44f)](https://starcare-hospital.onrender.com/login_page)
[![Test report](https://img.shields.io/badge/test%20report-Playwright-45ba4b)](https://zainulfaris93.github.io/Hospital-Management-System/)

A role-based hospital management web app built with **Python and Django**. Patients book appointments, doctors manage their schedules, and admins run the hospital.

**Live demo:** https://starcare-hospital.onrender.com/login_page

| Role    | Username   | Password      |
|---------|------------|---------------|
| Admin   | `admin`    | `Admin@123`   |
| Doctor  | `dr.meera` | `Doctor@123`  |
| Patient | `rahul`    | `Patient@123` |

On the login page, click a role to fill in its credentials. The demo runs on Render's free plan, so the first load after it has been idle can take up to a minute. Demo data resets automatically, and the shared demo accounts can't be deleted or have their passwords changed.

## Features

- **Three roles, three dashboards:** admin, doctor and patient, each with its own login and role-based access control
- **Appointment booking** with time-slot selection, double-booking prevention, one visit per doctor per day and a daily limit per doctor
- **Admin tools:** doctor approval, department management, add doctors and patients, filters, and searchable appointment history
- **Doctor tools:** today's schedule, mark appointments consulted or not consulted, appointment history
- **AJAX** for live counts and status updates without page reloads
- **Email notifications** for registration and approvals

## Testing

Every push runs two test suites on GitHub Actions:

| Suite | Tool | What it covers |
|-------|------|----------------|
| Unit & integration (34 tests) | Django `TestCase` | Login per role, role-based access, booking rules, appointment status workflow, registration emails, demo-mode protections |
| End-to-end (39 runs) | Playwright + TypeScript | Real browser journeys on desktop and mobile: demo login, access control, and the full appointment lifecycle across all three roles (patient books → admin approves → doctor consults → patient sees history) |

The E2E suite uses the **Page Object** pattern (`e2e/pages/`) and starts the Django server on a fresh, seeded database by itself. The latest HTML report is published at **https://zainulfaris93.github.io/Hospital-Management-System/**.

### What the tests caught

Writing the tests surfaced real defects, which were then fixed:

- **Missing authorization:** any logged-in user (and, for some URLs, anyone at all) could open admin pages, approve appointments or delete patients and doctors by visiting a URL. Every view now uses a `role_required` decorator, and the JSON endpoints return 401/403.
- **Booking rules only enforced in the browser:** the server accepted past dates, unknown time slots, unapproved doctors and repeat bookings with the same doctor on the same day. All of these are now validated server-side.
- **Silent failure:** booking a fully booked day redirected without any message. It now explains why.
- **UI bug:** the "all slots are booked" warning was hidden immediately by the next `if/else` block.
- **Timezone bug:** the earliest selectable date used UTC, so before 5:30 AM in India the picker allowed yesterday.
- **Invalid dates** in the availability API raised a server error (500). They now return 400.

## Tech stack

Python · Django 5 · Django ORM · MySQL (local) / SQLite (demo) · JavaScript · AJAX · Bootstrap · Gunicorn · WhiteNoise · Playwright · TypeScript · GitHub Actions · Render

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
