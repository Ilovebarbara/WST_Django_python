from django.contrib import admin
from .models import Account, Staff, Patient, Appointment, MedicalRecord, Queue

class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_patient')
    list_filter = ('role', 'is_staff', 'is_patient')
    search_fields = ('username', 'email')

class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'contact_info')
    search_fields = ('user__username', 'specialization')

class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'patient_number', 'first_name', 'last_name')
    search_fields = ('user__username', 'patient_number')

# Register models with corresponding Admin classes
admin.site.register(Account, AccountAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(Queue)
