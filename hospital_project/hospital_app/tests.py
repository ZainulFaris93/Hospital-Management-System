"""Unit and integration tests for the hospital app.

Run with:  USE_SQLITE=True python manage.py test hospital_app
"""
from datetime import date, timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Appointment, CustomUser, Department, Doctor, Patient

SLOT_1 = '09:00 AM - 10:00 AM'
SLOTS = [
    '09:00 AM - 10:00 AM',
    '10:00 AM - 11:00 AM',
    '11:00 AM - 12:00 PM',
    '02:00 PM - 03:00 PM',
    '03:00 PM - 04:00 PM',
]
PASSWORD = 'Test@1234'


class HospitalTestCase(TestCase):
    """Creates one admin, two approved doctors and two patients."""

    @classmethod
    def setUpTestData(cls):
        cls.cardio = Department.objects.create(Dept_name='Cardiology')
        cls.neuro = Department.objects.create(Dept_name='Neurology')

        cls.admin_user = cls.make_user('boss', 1)
        cls.doc_user = cls.make_user('drhouse', 2)
        cls.doctor = Doctor.objects.create(user=cls.doc_user, dep=cls.cardio, Phone_number='9000000001', status=1)
        cls.doc2_user = cls.make_user('drwho', 2)
        cls.doctor2 = Doctor.objects.create(user=cls.doc2_user, dep=cls.neuro, Phone_number='9000000002', status=1)

        cls.pat_user = cls.make_user('alice', 3)
        cls.patient = Patient.objects.create(user=cls.pat_user, p_id=1001, age=30, Phone_number='9100000001')
        cls.pat2_user = cls.make_user('bob', 3)
        cls.patient2 = Patient.objects.create(user=cls.pat2_user, p_id=1002, age=40, Phone_number='9100000002')

    @staticmethod
    def make_user(username, user_type):
        return CustomUser.objects.create_user(
            username=username, password=PASSWORD, email=f'{username}@example.com',
            first_name=username.title(), user_type=user_type,
        )

    def login(self, user):
        self.client.force_login(user)

    def book(self, day=None, slot=SLOT_1, doctor=None, dept=None):
        return self.client.post(reverse('save_appointment'), {
            'department': (dept or self.cardio).id,
            'doctor': (doctor or self.doctor).id,
            'date': (day or date.today() + timedelta(days=1)).isoformat(),
            'time': slot,
            'desc': 'Checkup',
        }, follow=True)


class LoginTests(HospitalTestCase):
    def test_each_role_lands_on_its_own_dashboard(self):
        for username, home in [('boss', 'admin_home'), ('drhouse', 'doctor_home'), ('alice', 'patient_home')]:
            with self.subTest(username=username):
                response = self.client.post(reverse('login_function'), {'uname': username, 'pass': PASSWORD})
                self.assertRedirects(response, reverse(home), fetch_redirect_response=False)
                self.client.logout()

    def test_wrong_password_shows_error(self):
        response = self.client.post(reverse('login_function'), {'uname': 'alice', 'pass': 'nope'}, follow=True)
        self.assertContains(response, 'Invalid username or password')

    def test_logout_ends_session(self):
        self.login(self.pat_user)
        self.client.get(reverse('logout_function'))
        response = self.client.get(reverse('patient_home'))
        self.assertRedirects(response, reverse('login_page'), fetch_redirect_response=False)


class AccessControlTests(HospitalTestCase):
    def test_anonymous_users_are_sent_to_login(self):
        for name in ['admin_home', 'doctor_home', 'patient_home', 'admin_view_patient']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertRedirects(response, reverse('login_page'), fetch_redirect_response=False)

    def test_patient_cannot_open_admin_or_doctor_pages(self):
        self.login(self.pat_user)
        for name in ['admin_home', 'admin_view_patient', 'doctor_home', 'doctor_appointments']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertRedirects(response, reverse('patient_home'), fetch_redirect_response=False)

    def test_doctor_cannot_open_admin_pages(self):
        self.login(self.doc_user)
        response = self.client.get(reverse('admin_home'))
        self.assertRedirects(response, reverse('doctor_home'), fetch_redirect_response=False)

    def test_patient_cannot_delete_other_patients(self):
        """Regression: delete_patient used to work for anyone, even logged-out visitors."""
        self.login(self.pat_user)
        self.client.get(reverse('delete_patient', args=[self.patient2.id]))
        self.assertTrue(Patient.objects.filter(id=self.patient2.id).exists())

    def test_anonymous_cannot_delete_doctors(self):
        self.client.get(reverse('delete_doctor', args=[self.doctor2.id]))
        self.assertTrue(Doctor.objects.filter(id=self.doctor2.id).exists())

    def test_api_endpoints_return_json_errors(self):
        response = self.client.get(reverse('approval_counts'))
        self.assertEqual(response.status_code, 401)
        self.login(self.pat_user)
        response = self.client.get(reverse('approval_counts'))
        self.assertEqual(response.status_code, 403)

    def test_patient_cannot_approve_appointments(self):
        appt = Appointment.objects.create(patient=self.patient, doctor=self.doctor, dept=self.cardio,
                                          date=date.today() + timedelta(days=1), time=SLOT_1)
        self.login(self.pat_user)
        response = self.client.post(reverse('update_appointment_status'), {'appointment_id': appt.id, 'action': 'approve'})
        self.assertEqual(response.status_code, 403)
        appt.refresh_from_db()
        self.assertEqual(appt.status, 0)


class BookingTests(HospitalTestCase):
    def setUp(self):
        self.login(self.pat_user)

    def test_patient_can_book_an_appointment(self):
        response = self.book()
        self.assertContains(response, 'Appointment booked successfully')
        appt = Appointment.objects.get()
        self.assertEqual((appt.patient, appt.doctor, appt.time, appt.status), (self.patient, self.doctor, SLOT_1, 0))

    def test_same_slot_cannot_be_double_booked(self):
        self.book()
        self.client.force_login(self.pat2_user)
        response = self.book()
        self.assertContains(response, 'already booked')
        self.assertEqual(Appointment.objects.count(), 1)

    def test_patient_cannot_book_same_doctor_twice_on_one_day(self):
        self.book(slot=SLOTS[0])
        response = self.book(slot=SLOTS[1])
        self.assertContains(response, 'already have an appointment')
        self.assertEqual(Appointment.objects.count(), 1)

    def test_doctor_is_capped_at_five_appointments_per_day(self):
        day = date.today() + timedelta(days=2)
        for i, slot in enumerate(SLOTS):
            p = Patient.objects.create(user=self.make_user(f'p{i}', 3), p_id=2000 + i, age=20, Phone_number=f'92000000{i:02}')
            Appointment.objects.create(patient=p, doctor=self.doctor, dept=self.cardio, date=day, time=slot)
        response = self.book(day=day, slot=SLOTS[0])
        self.assertContains(response, 'fully booked')
        self.assertEqual(Appointment.objects.filter(date=day).count(), 5)

    def test_cannot_book_in_the_past(self):
        response = self.book(day=date.today() - timedelta(days=1))
        self.assertContains(response, "can&#x27;t book an appointment in the past")
        self.assertFalse(Appointment.objects.exists())

    def test_rejects_unknown_time_slot(self):
        response = self.book(slot='11:59 PM - 12:00 AM')
        self.assertContains(response, 'available time slots')
        self.assertFalse(Appointment.objects.exists())

    def test_cannot_book_unapproved_doctor(self):
        pending = Doctor.objects.create(user=self.make_user('drnew', 2), dep=self.cardio, Phone_number='9000000009', status=0)
        response = self.book(doctor=pending)
        self.assertEqual(response.status_code, 404)

    def test_booked_times_endpoint_lists_taken_slots(self):
        day = date.today() + timedelta(days=3)
        Appointment.objects.create(patient=self.patient2, doctor=self.doctor, dept=self.cardio, date=day, time=SLOTS[2])
        response = self.client.get(reverse('get_booked_times', args=[self.doctor.id, day.isoformat()]))
        self.assertEqual(response.json(), {'booked_times': [SLOTS[2]]})

    def test_availability_suggests_next_free_day_when_full(self):
        day = date.today() + timedelta(days=4)
        for i, slot in enumerate(SLOTS):
            p = Patient.objects.create(user=self.make_user(f'q{i}', 3), p_id=3000 + i, age=20, Phone_number=f'93000000{i:02}')
            Appointment.objects.create(patient=p, doctor=self.doctor, dept=self.cardio, date=day, time=slot)
        data = self.client.get(reverse('check_day_availability', args=[self.doctor.id, day.isoformat()])).json()
        self.assertTrue(data['full'])
        self.assertEqual(data['next_date'], (day + timedelta(days=1)).isoformat())

    def test_invalid_date_returns_400(self):
        response = self.client.get(reverse('check_day_availability', args=[self.doctor.id, 'not-a-date']))
        self.assertEqual(response.status_code, 400)

    def test_load_doctors_only_returns_approved_doctors_in_department(self):
        Doctor.objects.create(user=self.make_user('drpending', 2), dep=self.cardio, Phone_number='9000000010', status=0)
        data = self.client.get(reverse('load_doctors', args=[self.cardio.id])).json()
        self.assertEqual([d['id'] for d in data['doctors']], [self.doctor.id])


class AppointmentWorkflowTests(HospitalTestCase):
    def setUp(self):
        self.appt = Appointment.objects.create(patient=self.patient, doctor=self.doctor, dept=self.cardio,
                                               date=date.today(), time=SLOT_1)

    def test_admin_approves_then_doctor_marks_consulted(self):
        self.login(self.admin_user)
        response = self.client.post(reverse('update_appointment_status'), {'appointment_id': self.appt.id, 'action': 'approve'})
        self.assertEqual(response.status_code, 200)
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, 1)

        self.login(self.doc_user)
        response = self.client.post(reverse('ajax_update_status'), {'appointment_id': self.appt.id, 'status': 'consulted'})
        self.assertEqual(response.json()['success'], True)
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, 3)

    def test_admin_rejects_appointment(self):
        self.login(self.admin_user)
        self.client.post(reverse('update_appointment_status'), {'appointment_id': self.appt.id, 'action': 'reject'})
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, 2)

    def test_admin_invalid_action_is_rejected(self):
        self.login(self.admin_user)
        response = self.client.post(reverse('update_appointment_status'), {'appointment_id': self.appt.id, 'action': 'delete'})
        self.assertEqual(response.status_code, 400)

    def test_doctor_cannot_update_another_doctors_appointment(self):
        self.appt.status = 1
        self.appt.save()
        self.login(self.doc2_user)
        response = self.client.post(reverse('ajax_update_status'), {'appointment_id': self.appt.id, 'status': 'consulted'})
        self.assertEqual(response.status_code, 404)

    def test_doctor_cannot_change_past_appointments(self):
        self.appt.date = date.today() - timedelta(days=1)
        self.appt.status = 1
        self.appt.save()
        self.login(self.doc_user)
        response = self.client.post(reverse('ajax_update_status'), {'appointment_id': self.appt.id, 'status': 'consulted'})
        self.assertEqual(response.status_code, 400)


class RegistrationTests(HospitalTestCase):
    def test_patient_signup_creates_account_and_emails_credentials(self):
        response = self.client.post(reverse('patient_signup_function'), {
            'fname': 'New', 'lname': 'Patient', 'uname': 'newpat', 'age': 25, 'phno': '9555555555',
            'address': 'Kochi', 'mail': 'newpat@example.com', 'patient': 3,
        })
        self.assertRedirects(response, reverse('login_page'), fetch_redirect_response=False)
        self.assertTrue(Patient.objects.filter(user__username='newpat').exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('newpat', mail.outbox[0].body)

    def test_signup_rejects_duplicate_username(self):
        response = self.client.post(reverse('patient_signup_function'), {
            'fname': 'A', 'lname': 'B', 'uname': 'alice', 'age': 25, 'phno': '9555555556',
            'address': 'x', 'mail': 'other@example.com', 'patient': 3,
        }, follow=True)
        self.assertContains(response, 'Username already exists')
        self.assertEqual(CustomUser.objects.filter(username='alice').count(), 1)

    def test_admin_approving_doctor_sends_login_details(self):
        pending = Doctor.objects.create(user=self.make_user('drpend', 2), dep=self.cardio, Phone_number='9000000011', status=0)
        self.login(self.admin_user)
        self.client.get(reverse('approve', args=[pending.id]))
        pending.refresh_from_db()
        self.assertEqual(pending.status, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password:', mail.outbox[0].body)


class DepartmentTests(HospitalTestCase):
    def test_admin_adds_department_and_duplicates_are_refused(self):
        self.login(self.admin_user)
        self.client.post(reverse('add_department'), {'dept_name': 'Oncology'})
        self.assertTrue(Department.objects.filter(Dept_name='Oncology').exists())
        response = self.client.post(reverse('add_department'), {'dept_name': 'Oncology'})
        self.assertIn('Already exist', response.json()['message'])
        self.assertEqual(Department.objects.filter(Dept_name='Oncology').count(), 1)


@override_settings(DEMO_MODE=True)
class DemoModeTests(HospitalTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.demo_patient_user = cls.make_user('rahul', 3)
        cls.demo_patient = Patient.objects.create(user=cls.demo_patient_user, p_id=4101, age=29, Phone_number='9100000099')

    def test_demo_account_password_cannot_be_changed(self):
        self.login(self.demo_patient_user)
        self.client.post(reverse('patient_reset_password_function'), {
            'currentpass': PASSWORD, 'newpass': 'Changed@123', 'confirmpass': 'Changed@123'})
        self.demo_patient_user.refresh_from_db()
        self.assertTrue(self.demo_patient_user.check_password(PASSWORD))

    def test_demo_account_cannot_be_deleted(self):
        self.login(self.admin_user)
        self.client.get(reverse('delete_patient', args=[self.demo_patient.id]))
        self.assertTrue(Patient.objects.filter(id=self.demo_patient.id).exists())

    def test_regular_accounts_can_still_be_deleted(self):
        self.login(self.admin_user)
        self.client.get(reverse('delete_patient', args=[self.patient2.id]))
        self.assertFalse(Patient.objects.filter(id=self.patient2.id).exists())

    def test_signup_shows_generated_password_on_screen(self):
        response = self.client.post(reverse('patient_signup_function'), {
            'fname': 'Demo', 'lname': 'User', 'uname': 'visitor1', 'age': 25, 'phno': '9666666666',
            'address': 'x', 'mail': 'visitor1@example.com', 'patient': 3,
        }, follow=True)
        self.assertContains(response, 'Demo mode: your login is username')
