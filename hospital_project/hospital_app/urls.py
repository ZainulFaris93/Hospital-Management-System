from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('login_page', views.login_page, name='login_page'),
    path('login_function',views.login_function, name='login_function'),
    path('logout_function', views.logout_function, name='logout_function'),
    path('patient_signup', views.patient_signup, name='patient_signup'),
    path('patient_signup_function', views.patient_signup_function, name='patient_signup_function'),
    path('doctor_signup', views.doctor_signup, name='doctor_signup'),
    path('doctor_signup_function', views.doctor_signup_function, name='doctor_signup_function'),



    path('admin_home/', views.admin_home, name='admin_home'),
    path('approval-counts/', views.approval_counts, name='approval_counts'),
    path('admin_doc_approval', views.admin_doc_approval, name='admin_doc_approval'),
    path('approve/<int:id>/', views.approve, name='approve'),
    path('disapprove/<int:id>/', views.disapprove, name='disapprove'),
    path('admin_view_doc/', views.admin_view_doc, name='admin_view_doc'),
    path('admin_view_doctor_details/<int:id>/', views.admin_view_doctor_details, name='admin_view_doctor_details'),
    path('delete_doctor/<int:id>/', views.delete_doctor, name='delete_doctor'),
    path('filter_doctors/', views.filter_doctors, name='filter_doctors'),
    path('admin_view_patient/', views.admin_view_patient, name='admin_view_patient'),
    path('admin_view_patient_details/<int:id>/', views.admin_view_patient_details, name='admin_view_patient_details'),
    path('delete_patient/<int:id>/', views.delete_patient, name='delete_patient'),
    path('admin_add_doc/', views.admin_add_doc, name='admin_add_doc'),
    path('admin_add_patient', views.admin_add_patient, name='admin_add_patient'),
    path('admin_manage_dept/', views.admin_manage_dept, name='admin_manage_dept'),
    path('add_department/', views.add_department, name='add_department'),
    path('delete_department/', views.delete_department, name='delete_department'),
    path('edit_department/', views.edit_department, name='edit_department'),
    path('admin_view_appointments/', views.admin_view_appointments, name='admin_view_appointments'),
    path('filter_appointments/', views.filter_appointments, name='filter_appointments'),
    path('update_appointment_status/', views.update_appointment_status, name='update_appointment_status'),
    path('admin_appointment_history/', views.admin_appointment_history, name='admin_appointment_history'),
    path('filter_appointment_history/', views.filter_appointment_history, name='filter_appointment_history'),
    path('search_appointment_history/', views.search_appointment_history, name='search_appointment_history'),
    path('admin_reset_password/', views.admin_reset_password, name='admin_reset_password'),
    path('admin_reset_password_function/', views.reset_password_function, name='admin_reset_password_function'),
    path("admin_edit_profile/", views.admin_edit_profile, name="admin_edit_profile"),



    path('doctor_home/', views.doctor_home, name="doctor_home"),
    path('doctor_appointment_count', views.doctor_appointment_count, name='doctor_appointment_count'),
    path('doctor_appointments/', views.doctor_appointments, name="doctor_appointments"),
    path('doctor/appointment/update-status/', views.ajax_update_status, name="ajax_update_status"),
    path('doctor/appointment/<int:id>/view/', views.doctor_view_appointment, name="doctor_view_appointment"),
    path('doctor_appointment_history/', views.doctor_appointment_history, name="doctor_appointment_history"),
    path('doctor_reset_password/', views.doctor_reset_password, name= 'doctor_reset_password'),
    path('doctor_reset_password_function/', views.doctor_reset_password_function, name='doctor_reset_password_function'),
    path("doctor_edit_profile/", views.doctor_edit_profile, name="doctor_edit_profile"),


    path('patient_home/', views.patient_home, name='patient_home'),
    path('patient_book_appointment/', views.patient_book_appointment, name="patient_book_appointment"),
    path('save_appointment/', views.save_appointment, name="save_appointment"),
    path('load-doctors/<int:dep_id>/', views.load_doctors, name="load_doctors"),
    path('check-day-availability/<int:doctor_id>/<str:date>/',views.check_day_availability,name='check_day_availability'),
    path('get-booked-times/<int:doctor_id>/<str:date>/',views.get_booked_times,name='get_booked_times'),
    path('patient_appointment_history/', views.patient_appointment_history, name="patient_appointment_history"),
    path("patient_edit_profile/", views.patient_edit_profile, name="patient_edit_profile"),
    path('patient_reset_password/', views.patient_reset_password, name= 'patient_reset_password'),
    path('patient_reset_password_function/', views.patient_reset_password_function, name='patient_reset_password_function'),
]
