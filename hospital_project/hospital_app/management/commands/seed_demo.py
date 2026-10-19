"""Create demo data so visitors can try every role right away.

Usage: python manage.py seed_demo
Safe to run more than once: existing demo records are reused.
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from hospital_app.models import Appointment, CustomUser, Department, Doctor, Patient

SLOTS = [
    '09:00 AM - 10:00 AM',
    '10:00 AM - 11:00 AM',
    '11:00 AM - 12:00 PM',
    '02:00 PM - 03:00 PM',
    '03:00 PM - 04:00 PM',
]


def make_user(username, password, user_type, first, last, email, superuser=False):
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults=dict(first_name=first, last_name=last, email=email, user_type=user_type),
    )
    if created:
        user.set_password(password)
        if superuser:
            user.is_staff = True
            user.is_superuser = True
        user.save()
    return user


class Command(BaseCommand):
    help = 'Seed the database with demo departments, doctors, patients and appointments.'

    def handle(self, *args, **options):
        make_user('admin', 'Admin@123', 1, 'Demo', 'Admin', 'admin@demo.starcare', superuser=True)

        depts = {}
        for name in ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Dermatology']:
            depts[name], _ = Department.objects.get_or_create(Dept_name=name)

        doctors = []
        for uname, first, last, dept, phone in [
            ('dr.meera', 'Meera', 'Nair', 'Cardiology', '9000000001'),
            ('dr.arjun', 'Arjun', 'Menon', 'Neurology', '9000000002'),
            ('dr.fathima', 'Fathima', 'Rahman', 'Pediatrics', '9000000003'),
            ('dr.joseph', 'Joseph', 'Thomas', 'Orthopedics', '9000000004'),
        ]:
            user = make_user(uname, 'Doctor@123', 2, first, last, f'{uname}@demo.starcare')
            doc, _ = Doctor.objects.get_or_create(
                user=user,
                defaults=dict(dep=depts[dept], Phone_number=phone, Address='Kozhikode, Kerala', status=1),
            )
            doctors.append(doc)

        # One doctor waiting for admin approval, so the approval flow can be tried
        pending = make_user('dr.anil', 'Doctor@123', 2, 'Anil', 'Kumar', 'dr.anil@demo.starcare')
        Doctor.objects.get_or_create(
            user=pending,
            defaults=dict(dep=depts['Dermatology'], Phone_number='9000000005', Address='Kochi, Kerala', status=0),
        )

        patients = []
        for uname, first, last, age, phone, pid in [
            ('rahul', 'Rahul', 'Das', 29, '9100000001', 4101),
            ('ananya', 'Ananya', 'Pillai', 34, '9100000002', 4102),
            ('kiran', 'Kiran', 'Varghese', 52, '9100000003', 4103),
        ]:
            user = make_user(uname, 'Patient@123', 3, first, last, f'{uname}@demo.starcare')
            pat, _ = Patient.objects.get_or_create(
                user=user,
                defaults=dict(p_id=pid, age=age, Phone_number=phone, Address='Kerala, India'),
            )
            patients.append(pat)

        if not Appointment.objects.exists():
            today = date.today()
            plan = [
                # (patient, doctor, day offset, slot, status, reason)
                (0, 0, 0, 0, 1, 'Chest pain follow-up'),
                (1, 0, 0, 1, 1, 'Routine BP check'),
                (2, 0, 1, 3, 0, 'ECG review'),
                (0, 1, 2, 2, 0, 'Recurring headaches'),
                (1, 2, 1, 0, 0, 'Child vaccination'),
                (2, 3, -3, 1, 3, 'Knee pain'),
                (0, 0, -7, 0, 3, 'Initial consultation'),
                (1, 1, -5, 4, 4, 'Migraine review'),
                (2, 0, -2, 2, 2, 'Second opinion'),
            ]
            for p, d, offset, slot, status, reason in plan:
                doc = doctors[d]
                Appointment.objects.create(
                    patient=patients[p], doctor=doc, dept=doc.dep,
                    date=today + timedelta(days=offset), time=SLOTS[slot],
                    Description=reason, status=status,
                )

        self.stdout.write(self.style.SUCCESS('Demo data ready: admin/Admin@123, dr.meera/Doctor@123, rahul/Patient@123'))
