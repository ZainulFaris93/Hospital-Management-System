from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import auth
from django.db.models import Q
import random
from django.contrib.auth.decorators import login_required
from datetime import date
from django.http import JsonResponse
from django.template.loader import render_to_string
import datetime
from datetime import timedelta
from django.utils.dateparse import parse_date
from .access import ADMIN, DOCTOR, PATIENT, role_required, is_protected_demo_user

MAX_APPOINTMENTS_PER_DAY = 5
TIME_SLOTS = [
    '09:00 AM - 10:00 AM',
    '10:00 AM - 11:00 AM',
    '11:00 AM - 12:00 PM',
    '02:00 PM - 03:00 PM',
    '03:00 PM - 04:00 PM',
]

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def patient_signup(request):
    return render(request, 'patient_signup.html')

def patient_signup_function(request):
    if request.method=='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        uname=request.POST['uname']
        age=request.POST['age']
        phone=request.POST['phno']
        address = request.POST['address']
        mail=request.POST['mail']
        us=request.POST['patient']
        if CustomUser.objects.filter(username=uname).exists():
            messages.error(request,'Username already exists')
            return redirect('patient_signup')
        elif CustomUser.objects.filter(email=mail).exists():
            messages.error(request,'Email already exists')
            return redirect('patient_signup')
        elif Doctor.objects.filter(Phone_number = phone).exists() or Patient.objects.filter(Phone_number = phone).exists():
            messages.error(request,'Phone Number already exists')
            return redirect('patient_signup')
        else:
            pas=str(random.randint(100000,999999))
            p_id = random.randint(1000,9999)
            user=CustomUser.objects.create_user(first_name=fname,last_name=lname,username=uname,password=pas,email=mail,user_type=us)
            user.save()
            tea=Patient(p_id=p_id,age=age,Phone_number=phone,Address=address,user=user)
            tea.save()
            subject='Patient Regsitration Successful'
            message='Patient ID: '+str(p_id)+"\n"+'username: '+str(uname)+"\n"+'password: '+str(pas)+"\n"+'email: '+str(mail)
            send_mail(subject,message,settings.EMAIL_HOST_USER,{mail})
            if settings.DEMO_MODE:
                messages.success(request,f'Registration successful. Demo mode: your login is username "{uname}", password "{pas}".')
            else:
                messages.success(request,'User registration success.Please Check Your E-mail for Login Credentials..')
            return redirect('login_page')
        
def doctor_signup(request):
    d = Department.objects.all()
    return render(request, 'doctor_signup.html', {'dept':d})

def doctor_signup_function(request):
    if request.method=='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        uname=request.POST['uname']
        phone=request.POST['phno']
        address = request.POST['address']
        mail=request.POST['mail']
        d_id=request.POST['dpt']
        d=Department.objects.get(id=d_id)
        prof = request.FILES.get('profile')
        us=request.POST['doc']
        if CustomUser.objects.filter(username=uname).exists():
            messages.error(request,'Username already exists')
            return redirect('doctor_signup')
        elif CustomUser.objects.filter(email=mail).exists():
            messages.error(request,'Email already exists')
            return redirect('doctor_signup')
        elif Doctor.objects.filter(Phone_number = phone).exists() or Patient.objects.filter(Phone_number = phone).exists():
            messages.error(request,'Phone Number already exists')
            return redirect('doctor_signup')
        else:
            user=CustomUser.objects.create_user(first_name=fname,last_name=lname,username=uname,email=mail,user_type=us)
            user.save()
            tea=Doctor(Phone_number=phone,user=user,Address=address,Profile=prof,dep=d)
            tea.save()
            subject='Doctor Regsitration confirmation'
            message='Registration is success ,please wait for admin approval...'
            send_mail(subject,"Hello "+uname+' '+message,settings.EMAIL_HOST_USER,[mail])
            messages.success(request,'User registration success.Please wait for admin approval..')
            return render(request,'login_page.html')
        
def login_page(request):
    return render(request,'login_page.html')

def login_function(request):
    if request.method == 'POST':
        usname = request.POST.get('uname')
        passw = request.POST.get('pass')

        user = authenticate(username=usname, password=passw)

        if user is not None:
            login(request, user)

            if user.user_type == 1:
                return redirect('admin_home')

            elif user.user_type == 2:
                return redirect('doctor_home')

            elif user.user_type == 3:
                return redirect('patient_home')

        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login_page')

    return render(request, 'login_page.html')


def logout_function(request):
    auth.logout(request)
    return redirect('login_page')


@role_required(ADMIN)
def admin_home(request):

    doctor_count = Doctor.objects.count()
    patient_count = Patient.objects.count()
    department_count = Department.objects.count()

    today = date.today()
    today_appointments = Appointment.objects.filter(date=today).count()

    pending_doctors_count = Doctor.objects.filter(status=0).count()
    pending_appointments_count = Appointment.objects.filter(status=0).count()

    return render(request, 'admin_home.html', {
        'doctor_count': doctor_count,
        'patient_count': patient_count,
        'department_count': department_count,
        'today_appointments': today_appointments,
        'pending_doctors_count': pending_doctors_count,
        'pending_appointments_count': pending_appointments_count,
    })


@role_required(ADMIN, api=True)
def approval_counts(request):
    doctor_count = Doctor.objects.filter(status=0).count()
    appointment_count = Appointment.objects.filter(status=0).count()

    return JsonResponse({
        "doctor_count": doctor_count,
        "appointment_count": appointment_count
    })


@role_required(ADMIN)
def admin_doc_approval(request):
    doc = Doctor.objects.select_related('user').all()
    return render(request, 'admin_doc_approval.html', {'doc': doc})

@role_required(ADMIN)
def approve(request, id):
    import random
    usr = Doctor.objects.get(id=id)
    user1 = usr.user

    usr.status = 1
    usr.save()

    password = str(random.randint(100000, 999999))
    user1.set_password(password)
    user1.save()

    subject = 'Admin approved'
    message = f"Username: {user1.username}\nPassword: {password}\nEmail: {user1.email}"

    send_mail(subject, message, settings.EMAIL_HOST_USER, [user1.email])

    if settings.DEMO_MODE:
        messages.info(request, f'Doctor approved. Demo mode: login is username "{user1.username}", password "{password}".')
    else:
        messages.info(request, 'Doctor approved')
    return redirect('admin_doc_approval')

@role_required(ADMIN)
def disapprove(request, id):
    usr = Doctor.objects.get(id=id)
    usr.status = 2
    usr.save()
    subject = 'Admin Disapproved'
    message='Registration is Unsuccessful...'
    send_mail(subject,"Hello "+' '+message,settings.EMAIL_HOST_USER,{usr.user.email})
    messages.info(request, 'User Disapproved')
    return redirect('admin_doc_approval')


@role_required(ADMIN)
def admin_view_doc(request):
    docs = Doctor.objects.filter(status=1)
    departments = Department.objects.all()
    return render(request, 'admin_view_doc.html', {'docs': docs, 'departments': departments})

@role_required(ADMIN)
def admin_view_doctor_details(request, id):
    doctor = Doctor.objects.get(id=id)
    return render(request, 'admin_view_doctor_details.html', {'doctor': doctor})



@role_required(ADMIN, api=True)
def filter_doctors(request):
    dep_id = request.GET.get('department_id')

    if dep_id:
        docs = Doctor.objects.filter(dep_id=dep_id, status=1)
    else:
        docs = Doctor.objects.filter(status=1)

    table_html = render_to_string('components/doctor_table.html', {'docs': docs})
    return JsonResponse({'table_html': table_html})

@role_required(ADMIN)
def delete_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    user = doctor.user
    if is_protected_demo_user(user):
        messages.error(request, "Demo accounts can't be deleted. Add a doctor yourself and delete that one.")
        return redirect('admin_view_doc')
    doctor.delete()
    user.delete()
    messages.error(request,'Doctor Deleted Successfully')
    return redirect('admin_view_doc')

@role_required(ADMIN)
def admin_add_doc(request):
    d = Department.objects.all()
    if request.method=='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        uname=request.POST['uname']
        phone=request.POST['phno']
        address = request.POST['address']
        mail=request.POST['mail']
        d_id=request.POST['dpt']
        d=Department.objects.get(id=d_id)
        prof = request.FILES.get('profile')
        us=request.POST['doc']
        if CustomUser.objects.filter(username=uname).exists():
            messages.error(request,'Username already exists')
            return redirect('admin_add_doc')
        elif CustomUser.objects.filter(email=mail).exists():
            messages.error(request,'Email already exists')
            return redirect('admin_add_doc')
        elif Doctor.objects.filter(Phone_number = phone).exists() or Patient.objects.filter(Phone_number = phone).exists():
            messages.error(request,'Phone Number already exists')
            return redirect('admin_add_doc')
        else:
            user=CustomUser.objects.create_user(first_name=fname,last_name=lname,username=uname,email=mail,user_type=us)
            password = str(random.randint(100000, 999999))
            user.set_password(password)
            user.save()
            tea=Doctor(Phone_number=phone,user=user,Address=address,Profile=prof,dep=d, status=1)
            tea.save()

            subject = 'Admin Created Your Account(Doctor)'
            message = f"Username: {user.username}\nPassword: {password}\nEmail: {user.email}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            if settings.DEMO_MODE:
                messages.info(request, f'Doctor added. Demo mode: login is username "{uname}", password "{password}".')
            else:
                messages.info(request, 'Doctor Added Successfully')
            return redirect('admin_add_doc')
        
    return render(request, 'admin_add_doc.html', {'dept':d})



@role_required(ADMIN)
def admin_view_patient(request):
    patients = Patient.objects.all()
    return render(request, 'admin_view_patient.html', {'patients': patients})


@role_required(ADMIN)
def admin_view_patient_details(request, id):
    patient = Patient.objects.get(id=id)
    return render(request, 'admin_view_patient_details.html', {'patient': patient})



@role_required(ADMIN)
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    user = patient.user
    if is_protected_demo_user(user):
        messages.error(request, "Demo accounts can't be deleted. Add a patient yourself and delete that one.")
        return redirect('admin_view_patient')
    patient.delete()
    user.delete()
    messages.error(request,'Patient Deleted Successfully')
    return redirect('admin_view_patient')


@role_required(ADMIN)
def admin_add_patient(request):
    if request.method=='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        uname=request.POST['uname']
        age=request.POST['age']
        phone=request.POST['phno']
        address = request.POST['address']
        mail=request.POST['mail']
        us=request.POST['patient']
        if CustomUser.objects.filter(username=uname).exists():
            messages.error(request,'Username already exists')
            return redirect('admin_add_patient')
        elif CustomUser.objects.filter(email=mail).exists():
            messages.error(request,'Email already exists')
            return redirect('admin_add_patient')
        elif Doctor.objects.filter(Phone_number = phone).exists() or Patient.objects.filter(Phone_number = phone).exists():
            messages.error(request,'Phone Number already exists')
            return redirect('admin_add_patient')
        else:
            pas=str(random.randint(100000,999999))
            p_id = random.randint(1000,9999)
            user=CustomUser.objects.create_user(first_name=fname,last_name=lname,username=uname,password=pas,email=mail,user_type=us)
            user.save()
            tea=Patient(p_id=p_id,age=age,Phone_number=phone,Address=address,user=user)
            tea.save()
            subject='Patient Regsitration Successful'
            message='Patient Id: '+str(p_id)+"\n"+'username: '+str(uname)+"\n"+'password: '+str(pas)+"\n"+'email: '+str(mail)
            send_mail(subject,message,settings.EMAIL_HOST_USER,{mail})
            if settings.DEMO_MODE:
                messages.success(request,f'Patient registered. Demo mode: login is username "{uname}", password "{pas}".')
            else:
                messages.success(request,'Patient Registration Successful..')
            return redirect('admin_add_patient')
    
    return render(request, 'admin_add_patient.html')

@role_required(ADMIN)
def admin_manage_dept(request):
    departments = Department.objects.all().order_by("id")
    return render(request, "admin_manage_dept.html", {"departments": departments})

@role_required(ADMIN, api=True)
def add_department(request):
    if request.method == "POST":
        name = request.POST.get("dept_name").strip()

        if Department.objects.filter(Dept_name = name).exists():
            departments = Department.objects.all().order_by("id")
            table_html = render_to_string(
                "components/department_table.html",
                {"departments": departments},
                request=request
            )

            return JsonResponse({
                "success": True,
                "message": "Department name Already exist!",
                "table_html": table_html
            })
        
        if name.strip() != "":
            Department.objects.create(Dept_name=name)

    departments = Department.objects.all().order_by("id")
    table_html = render_to_string("components/department_table.html", {"departments": departments})
    return JsonResponse({
        "success": True,
        "message": "Department added successfully!",
        "table_html": table_html
    })


@role_required(ADMIN, api=True)
def delete_department(request):
    if request.method == "POST":
        dep_id = request.POST.get("dept_id")
        Department.objects.filter(id=dep_id).delete()

    departments = Department.objects.all().order_by("id")
    table_html = render_to_string("components/department_table.html", {"departments": departments})
    return JsonResponse({"table_html": table_html})

@role_required(ADMIN, api=True)
def edit_department(request):
    if request.method == "GET":
        dep_id = request.GET.get("id")
        dep = Department.objects.get(id=dep_id)
        data = {
            "Dept_name": dep.Dept_name
        }
        return JsonResponse(data)
    elif request.method == "POST":
        dept_id = request.POST.get("dept_id")
        name = request.POST.get("dept_name").strip()

        if Department.objects.filter(Dept_name = name).exists():
            departments = Department.objects.all().order_by("id")
            table_html = render_to_string(
                "components/department_table.html",
                {"departments": departments},
                request=request
            )

            return JsonResponse({
                "success": True,
                "message": "Department name Already exist!",
                "table_html": table_html
            })
        
        dep = Department.objects.get(id=dept_id)
        dep.Dept_name = name
        dep.save()

        departments = Department.objects.all().order_by("id")
        table_html = render_to_string(
            "components/department_table.html",
            {"departments": departments},
            request=request
        )

        return JsonResponse({
            "success": True,
            "message": "Department name updated successfully",
            "table_html": table_html
        })



@role_required(ADMIN)
def admin_view_appointments(request):
    appointments = Appointment.objects.filter(status=0).order_by('date')
    doctors = Doctor.objects.filter(status=1).select_related('user', 'dep')
    return render(request, 'admin_view_appointments.html', {
        'appointments': appointments,
        'doctors': doctors,
    })


@role_required(ADMIN, api=True)
def filter_appointments(request):
    doctor_id = request.GET.get('doctor_id')

    qs = Appointment.objects.filter(status=0).order_by('date')
    if doctor_id:
        qs = qs.filter(doctor_id=doctor_id)

    table_html = render_to_string('components/appointments_table.html', {'appointments': qs})
    return JsonResponse({'table_html': table_html})



@role_required(ADMIN, api=True)
def update_appointment_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    appointment_id = request.POST.get('appointment_id')
    action = request.POST.get('action')

    if not appointment_id or action not in ('approve', 'reject'):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    try:
        app = Appointment.objects.get(id=appointment_id, status=0) 
    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Appointment not found or not pending'}, status=404)

    if action == 'approve':
        app.status = 1
    else:
        app.status = 2

    app.save()

    
    doctor_id = request.POST.get('doctor_id')
    qs = Appointment.objects.filter(status=0).order_by('date')
    if doctor_id:
        qs = qs.filter(doctor_id=doctor_id)

    table_html = render_to_string('components/appointments_table.html', {'appointments': qs})
    return JsonResponse({'table_html': table_html})

@role_required(ADMIN)
def admin_appointment_history(request):
    appointments = Appointment.objects.filter(status__in=[1, 2, 3, 4]).order_by('-date')

    doctors = Doctor.objects.filter(status=1).select_related('user', 'dep')

    return render(request, "admin_appointment_history.html", {
        "appointments": appointments,
        "doctors": doctors,
    })

@role_required(ADMIN, api=True)
def filter_appointment_history(request):
    doctor_id = request.GET.get('doctor_id')

    qs = Appointment.objects.filter(status__in=[1, 2, 3, 4]).order_by('-date')

    if doctor_id:
        qs = qs.filter(doctor_id=doctor_id)

    table_html = render_to_string(
        "components/appointment_history_table.html",
        {"appointments": qs}
    )
    return JsonResponse({"table_html": table_html})

@role_required(ADMIN, api=True)
def search_appointment_history(request):
    pat_name = request.GET.get('pat_name')

    qs = Appointment.objects.filter(status__in=[1, 2, 3, 4]).order_by('-date')

    if pat_name:
        qs = qs.filter(
            Q(patient__user__first_name__icontains = pat_name) |
            Q(patient__user__last_name__icontains = pat_name)
        )

    table_html = render_to_string(
        "components/appointment_history_table.html",
        {"appointments": qs}
    )
    return JsonResponse({"table_html": table_html})

@role_required(ADMIN)
def admin_reset_password(request):
    return render(request, 'admin_reset_password.html')


@role_required(ADMIN)
def reset_password_function(request):
    if request.method == 'POST':
        if is_protected_demo_user(request.user):
            messages.error(request, "This is a shared demo account, so it can't be changed. Try creating your own account instead.")
            return redirect('admin_reset_password')
        current_password = request.POST['currentpass']
        pas = request.POST['newpass']
        cpas = request.POST['confirmpass']

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('admin_reset_password')

        if pas != cpas:
            messages.error(request, 'Passwords do not match.')
            return redirect('admin_reset_password')

        if (
            len(pas) < 8 or 
            not any(char.isupper() for char in pas) or
            not any(char.isdigit() for char in pas) or
            not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in pas)
        ):
            messages.error(request, 'Password must be at least 8 characters, and contain an uppercase letter, a digit, and a special character.')
            return redirect('admin_reset_password')

        user = request.user
        user.set_password(pas)
        user.save()

        messages.success(request, 'Password reset successfully.')
        return redirect('login_page')

    return render(request, 'admin_reset_password.html')

@role_required(ADMIN)
def admin_edit_profile(request):
    user = request.user
    if request.method == "POST":
        if is_protected_demo_user(request.user):
            messages.error(request, "This is a shared demo account, so it can't be changed. Try creating your own account instead.")
            return redirect("admin_edit_profile")
        email = request.POST.get("email")
        uname = request.POST.get("uname")
        for i in CustomUser.objects.exclude(id = user.id):
            if i.username == uname:
                messages.error(request, "Username already exists!")
                return redirect("admin_edit_profile")
            
            if i.email == email:
                messages.error(request, "email already exists!")
                return redirect("admin_edit_profile")
        
        user.email = email
        user.username = uname
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("admin_edit_profile")
    return render(request, 'admin_edit_profile.html', {'ad':user})

# --------------------------------------------------------------------------------------------------------------------------

@role_required(DOCTOR, api=True)
def doctor_appointment_count(request):
    doctor = Doctor.objects.get(user=request.user)

    count = Appointment.objects.filter(
        doctor=doctor,
        status=1,
        date__gte=date.today()
    ).count()

    return JsonResponse({"count": count})


@role_required(DOCTOR)
def doctor_home(request):
    doctor = Doctor.objects.get(user=request.user)

    next_appointment = Appointment.objects.filter(doctor=doctor, status=1, date__gte=date.today()).order_by('date', 'time').first()

    today_appointments = Appointment.objects.filter(doctor=doctor,date=date.today(), status__in=[1, 3, 4])

    today_count = today_appointments.count()
    completed_today = today_appointments.filter(status=3).count()
    pending_today = today_appointments.filter(status=1).count()

    monthly_appointments = Appointment.objects.filter(doctor=doctor,date__month=date.today().month,status__in=[1, 3]).count()

    cancelled_appointments = Appointment.objects.filter(doctor=doctor,status=4).count()

    total_patients = Patient.objects.filter(appointment__doctor=doctor,appointment__status__in=[1, 3, 4]).distinct().count()

    return render(request, "doctor_home.html", {
        "next_appointment": next_appointment,
        "today_count": today_count,
        "completed_today": completed_today,
        "pending_today": pending_today,
        "monthly_appointments": monthly_appointments,
        "cancelled_appointments": cancelled_appointments,
        "total_patients": total_patients,
    })


@role_required(DOCTOR)
def doctor_appointments(request):
    doctor = Doctor.objects.get(user=request.user)

    appointments = Appointment.objects.filter(
        doctor=doctor,
        status=1,
        date__gte=date.today()    
    ).order_by("date", "time")

    return render(request, "doctor_appointments.html", {
        "appointments": appointments
    })


@role_required(DOCTOR, api=True)
def ajax_update_status(request):
    if request.method == "POST":
        app_id = request.POST.get("appointment_id")
        action = request.POST.get("status")

        appointment = get_object_or_404(
            Appointment,
            id=app_id,
            doctor__user=request.user
        )

        if appointment.date < date.today():
            return JsonResponse({"error": "Past appointment"}, status=400)

        if action == "consulted":
            appointment.status = 3
        elif action == "not_consulted":
            appointment.status = 4
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)

        appointment.save(update_fields=["status"])

        return JsonResponse({
            "success": True,
            "appointment_id": appointment.id
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


@role_required(DOCTOR)
def doctor_view_appointment(request, id):
    appointment = get_object_or_404(
        Appointment,
        id=id,
        doctor__user=request.user
    )

    return render(request, "doctor_appointment_view.html", {
        "appointment": appointment
    })



@role_required(DOCTOR)
def doctor_appointment_history(request):
    doctor = Doctor.objects.get(user=request.user)

    history = Appointment.objects.filter(
        doctor=doctor,
        status__in=[3, 4]
    ).order_by('-date', '-time')

    return render(request, "doctor_appointment_history.html", {
        "history": history
    })




@role_required(DOCTOR)
def doctor_reset_password(request):
    return render(request, 'doctor_reset_password.html')



@role_required(DOCTOR)
def doctor_reset_password_function(request):
    if request.method == 'POST':
        if is_protected_demo_user(request.user):
            messages.error(request, "This is a shared demo account, so it can't be changed. Try creating your own account instead.")
            return redirect('doctor_reset_password')
        current_password = request.POST['currentpass']
        pas = request.POST['newpass']
        cpas = request.POST['confirmpass']

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('doctor_reset_password')

        if pas != cpas:
            messages.error(request, 'Passwords do not match.')
            return redirect('doctor_reset_password')

        if (
            len(pas) < 8 or 
            not any(char.isupper() for char in pas) or
            not any(char.isdigit() for char in pas) or
            not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in pas)
        ):
            messages.error(request, 
                'Password must be at least 8 characters, and contain an uppercase letter, a digit, and a special character.')
            return redirect('doctor_reset_password')

        user = request.user
        user.set_password(pas)
        user.save()


        messages.success(request, 'Password reset successfully.')
        return redirect('login_page')

    return render(request, 'doctor_reset_password.html')


@role_required(DOCTOR)
def doctor_edit_profile(request):
    doctor = Doctor.objects.get(user=request.user)
    dept = Department.objects.all()

    if request.method == "POST":
        if is_protected_demo_user(request.user):
            messages.error(request, "This is a shared demo account, so it can't be changed. Try creating your own account instead.")
            return redirect("doctor_edit_profile")
        user = request.user

        first_name = request.POST.get("fname")
        last_name = request.POST.get("lname")
        email = request.POST.get("email")
        uname = request.POST.get("uname")
        for i in CustomUser.objects.exclude(id=doctor.user.id):
            if i.username == uname:
                messages.error(request, "Username already exists!")
                return redirect("doctor_edit_profile")
            
            if i.email == email:
                messages.error(request, "email already exists!")
                return redirect("doctor_edit_profile")
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = uname
        

        Phone = request.POST.get("phone")
        for i in Doctor.objects.exclude(id=doctor.id):
            if i.Phone_number == Phone:
                messages.error(request, "Phone Number already exists!")
                return redirect("doctor_edit_profile")
        doctor.Address = request.POST.get("address")
        doctor.Phone_number = Phone
        doctor.dep_id = request.POST.get("dpt")

        if request.FILES.get("profile"):
            doctor.Profile = request.FILES["profile"]

        user.save()
        doctor.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("doctor_edit_profile")

    return render(request, "doctor_edit_profile.html", {
        "doctor": doctor,
        "dept": dept
    })


# ----------------------------------------------------------------------------------------------------------------------

@role_required(PATIENT)
def patient_home(request):
    return render(request, 'patient_home.html')

@role_required(PATIENT)
def patient_book_appointment(request):
    patient = Patient.objects.get(user=request.user)
    departments = Department.objects.all()
    return render(request, "patient_book_appointment.html", {
        "patient": patient,
        "departments": departments
    })


@role_required(PATIENT, api=True)
def load_doctors(request, dep_id):
    doctors = Doctor.objects.filter(dep_id=dep_id, status=1)
    data = [{"id": d.id, "name": d.user.first_name} for d in doctors]
    return JsonResponse({"doctors": data})

@role_required(PATIENT, api=True)
def check_day_availability(request, doctor_id, date):
    selected_date = parse_date(date)
    if selected_date is None:
        return JsonResponse({"error": "Invalid date"}, status=400)
    pat = Patient.objects.get(user=request.user)

    count = Appointment.objects.filter(
        doctor_id=doctor_id,
        date=selected_date
    ).count()

    pat_count = Appointment.objects.filter(
        doctor_id=doctor_id,
        date=selected_date,
        patient = pat
    ).count()

    if count >= MAX_APPOINTMENTS_PER_DAY:
        next_date = selected_date + timedelta(days=1)

        while Appointment.objects.filter(
            doctor_id=doctor_id,
            date=next_date
        ).count() >= MAX_APPOINTMENTS_PER_DAY:
            next_date += timedelta(days=1)

        return JsonResponse({
            "full": True,
            "next_date": next_date
        })
    
    if pat_count >= 1:
        next_date = selected_date + timedelta(days=1)

        while Appointment.objects.filter(
            doctor_id=doctor_id,
            patient = pat,
            date=next_date
        ).count() >= 1:
            next_date += timedelta(days=1)

        return JsonResponse({
            "exist": True,
            "next_date": next_date
        })
    
    return JsonResponse({"full": False, "exist": False})


@role_required(PATIENT)
def save_appointment(request):
    if request.method == "POST":
        dep_id = request.POST['department']
        doctor_id = request.POST['doctor']
        date_selected = request.POST['date']
        time_slot = request.POST['time']
        desc = request.POST['desc']

        patient = Patient.objects.get(user=request.user)
        dept = get_object_or_404(Department, id=dep_id)
        doctor = get_object_or_404(Doctor, id=doctor_id, status=1)
        date_parsed = parse_date(date_selected) if date_selected else None

        if date_parsed is None:
            messages.error(request, "Please choose a valid date.")
            return redirect('patient_book_appointment')

        if date_parsed < date.today():
            messages.error(request, "You can't book an appointment in the past.")
            return redirect('patient_book_appointment')

        if time_slot not in TIME_SLOTS:
            messages.error(request, "Please choose one of the available time slots.")
            return redirect('patient_book_appointment')

        appointment_count = Appointment.objects.filter(
            doctor=doctor,
            date=date_parsed
        ).count()

        if appointment_count >= MAX_APPOINTMENTS_PER_DAY:
            messages.error(request, "This doctor is fully booked on that date. Please choose another day.")
            return redirect('patient_book_appointment')

        if Appointment.objects.filter(doctor=doctor, date=date_parsed, patient=patient).exists():
            messages.error(request, "You already have an appointment with this doctor on that date.")
            return redirect('patient_book_appointment')

        if Appointment.objects.filter(doctor=doctor, date=date_parsed, time=time_slot).exists():
            messages.error(request, "This time slot is already booked for this doctor.")
            return redirect('patient_book_appointment')
        

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            dept=dept,
            date=date_parsed,
            time=time_slot,
            Description = desc,
            status=0
        )

        messages.success(request, "Appointment booked successfully!")
        return redirect("patient_book_appointment")

@role_required(PATIENT, api=True)
def get_booked_times(request, doctor_id, date):
    selected_date = parse_date(date)
    if selected_date is None:
        return JsonResponse({"error": "Invalid date"}, status=400)
    booked_times = Appointment.objects.filter(
        doctor_id=doctor_id,
        date=selected_date
    ).values_list('time', flat=True)

    return JsonResponse({
        "booked_times": list(booked_times)
    })

@role_required(PATIENT)
def patient_appointment_history(request):
    patient = Patient.objects.get(user=request.user)
    appointments = Appointment.objects.filter(patient=patient).order_by('-date')
    return render(request, "patient_appointment_history.html", {
        "appointments": appointments
    })


@role_required(PATIENT)
def patient_edit_profile(request):
    patient = Patient.objects.get(user=request.user)

    if request.method == "POST":
        if is_protected_demo_user(request.user):
            messages.error(request, "This is a shared demo account, so it can't be changed. Try creating your own account instead.")
            return redirect("patient_edit_profile")
        user = request.user

        # Update User model fields
        first_name = request.POST.get("fname")
        last_name = request.POST.get("lname")
        email = request.POST.get("email")
        uname = request.POST.get("uname")
        for i in CustomUser.objects.exclude(id=patient.user.id):
            if i.username == uname:
                messages.error(request, "Username already exists!")
                return redirect("patient_edit_profile")
            
            if i.email == email:
                messages.error(request, "email already exists!")
                return redirect("patient_edit_profile")
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = uname
        

        # Update Patient model fields
        Phone = request.POST.get("phone")
        for i in Patient.objects.exclude(id=patient.id):
            if i.Phone_number == Phone:
                messages.error(request, "Phone Number already exists!")
                return redirect("patient_edit_profile")
        patient.Address = request.POST.get("address")
        patient.age = request.POST.get("age")
        patient.Phone_number = Phone
        user.save()
        patient.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("patient_edit_profile")

    return render(request, "patient_edit_profile.html", {
        "patient": patient
    })


@role_required(PATIENT)
def patient_reset_password(request):
    return render(request, 'patient_reset_password.html')


@role_required(PATIENT)
def patient_reset_password_function(request):
    if request.method == 'POST':
        if is_protected_demo_user(request.user):
            messages.error(request, "This is a shared demo account, so it can't be changed. Try creating your own account instead.")
            return redirect('patient_reset_password')
        current_password = request.POST['currentpass']
        pas = request.POST['newpass']
        cpas = request.POST['confirmpass']

        # Check current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('patient_reset_password')

        # Check match
        if pas != cpas:
            messages.error(request, 'Passwords do not match.')
            return redirect('patient_reset_password')

        # Validate complexity
        if (
            len(pas) < 8 or 
            not any(char.isupper() for char in pas) or
            not any(char.isdigit() for char in pas) or
            not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in pas)
        ):
            messages.error(request, 
                'Password must be at least 8 characters, and contain an uppercase letter, a digit, and a special character.')
            return redirect('patient_reset_password')

        # Save the new password
        user = request.user
        user.set_password(pas)
        user.save()


        messages.success(request, 'Password reset successfully.')
        return redirect('login_page')

    return render(request, 'patient_reset_password.html')
