# StarCare: Hospital Management System

A role-based hospital management web app built with **Python and Django**. Patients book appointments, doctors manage their schedules, and admins run the hospital.

**Live demo:** https://starcare-hospital.onrender.com/login_page

| Role    | Username   | Password    |
|---------|------------|-------------|
| Admin   | `admin`    | `Admin@123` |
| Doctor  | `dr.meera` | `Doctor@123`|
| Patient | `rahul`    | `Patient@123` |

On the login page, click a role to fill in its credentials. The demo runs on Render's free plan, so the first load after it has been idle can take up to a minute. Demo data resets automatically.

## Features

- **Three roles, three dashboards:** admin, doctor and patient, each with its own login and permissions
- **Appointment booking** with time-slot selection, double-booking prevention and a daily limit per doctor
- **Admin tools:** doctor approval, department management, add doctors and patients, filters, and searchable appointment history
- **Doctor tools:** today's schedule, approve or complete appointments, appointment history
- **AJAX** for live counts and status updates without page reloads
- **Email notifications** for registration and approvals

## Tech stack

Python · Django 5 · Django ORM · MySQL (local) / SQLite (demo) · JavaScript · AJAX · Bootstrap · Gunicorn · WhiteNoise · Render

## Run locally

```bash
cd hospital_project
pip install -r requirements.txt
USE_SQLITE=True DEMO_MODE=True python manage.py migrate
USE_SQLITE=True DEMO_MODE=True python manage.py seed_demo
USE_SQLITE=True DEMO_MODE=True python manage.py runserver
```

To use MySQL instead, create a `hospital_db` database, run `pip install mysqlclient`, and leave out `USE_SQLITE=True`.

## Deployment

`render.yaml` defines the Render service. Each start runs the migrations, loads the demo data (`python manage.py seed_demo`) and launches Gunicorn. Every push to `master` redeploys automatically.

---
Built by [Zainul Faris V K](https://zainulfaris93.github.io)
