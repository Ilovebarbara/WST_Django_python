from django.urls import path
from . import views

urlpatterns = [
    # Landing Page and Login
    path('', views.home, name='home'),
    path('staff-login/', views.staff_login, name='staff_login'),
    path('patient-login/', views.patient_login, name='patient_login'),
    path('patient-register/', views.patient_register, name='patient_register'),
    path('admin-login/', views.admin_login, name='admin_login'),
    # Staff Dashboard Contents
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff-appointments/', views.staff_appointments, name='staff_appointments'),
    path('staff-medical-records/', views.staff_medical_records, name='staff_medical_records'),
    path('add-patient/', views.add_patient, name='add_patient'),

    path('staff-settings/', views.staff_settings, name='staff_settings'),
    # Patient Dashboard Contents
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient-settings/', views.patient_settings, name='patient_settings'),
    #Logout
    path('logout', views.logout, name='logout'),
    path('update-password/', views.update_staff_password, name='update_staff_password'),
    
    path('patient-queue/', views.patient_queue, name='patient_queue'),

    # Admin Dashboard Contents
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    #path('admin-dashboard/lists', views.list_accounts, name='admin_list_accounts'),
    path('admin-dashboard/staff_register', views.staff_register, name='staff_register'),

]

