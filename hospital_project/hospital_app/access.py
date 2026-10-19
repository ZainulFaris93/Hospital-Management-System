"""Role-based access control for hospital_app views.

Every user has a user_type: 1 = admin, 2 = doctor, 3 = patient.
Decorate a view with @role_required(ADMIN) (or DOCTOR / PATIENT) so only
that role can reach it. JSON endpoints use api=True so they answer with
401/403 JSON instead of redirecting.
"""
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

ADMIN, DOCTOR, PATIENT = 1, 2, 3
HOME_FOR = {ADMIN: 'admin_home', DOCTOR: 'doctor_home', PATIENT: 'patient_home'}

# Accounts created by `python manage.py seed_demo`. In demo mode they can't be
# deleted, renamed or have their password changed, so every visitor can log in.
DEMO_USERNAMES = {'admin', 'dr.meera', 'dr.arjun', 'dr.fathima', 'dr.joseph', 'dr.anil',
                  'rahul', 'ananya', 'kiran'}


def role_required(role, api=False):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                if api:
                    return JsonResponse({'error': 'Login required'}, status=401)
                return redirect('login_page')
            if user.user_type != role:
                if api:
                    return JsonResponse({'error': 'Forbidden'}, status=403)
                messages.error(request, "You don't have access to that page.")
                return redirect(HOME_FOR.get(user.user_type, 'login_page'))
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def is_protected_demo_user(user):
    return getattr(settings, 'DEMO_MODE', False) and user is not None and user.username in DEMO_USERNAMES
