from django import forms
from .models import Appointment, MedicalRecord
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Appointment, MedicalRecord, Queue, Account

class PatientRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'consultation_type']

class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']


# MedicalRecord form
class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            'patient', 'staff', 'transaction_type', 'date', 'time', 
            'height', 'weight', 'hr', 'rr', 'temperature', 
            'bp', 'pain_scale', 'other_symptoms', 'initial_diagnosis'
        ]
        # 'record_type', 'document_type' excluded in the fields 
        
    # Optional: custom widgets for better input, e.g., date picker, time picker, etc.
    date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, 2100)))
    time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))


# MedicalRecord filter form for searching records
class MedicalRecordFilterForm(forms.Form):
    record_type = forms.ChoiceField(
        choices=[('', 'All'), ('Dental', 'Dental'), ('Medical', 'Medical')],
        required=False,
        label="Filter by Record Type"
    )
    document_type = forms.ChoiceField(
        choices=[('', 'All'), ('Consultation Certificate', 'Consultation Certificate'), 
                 ('Medical Report', 'Medical Report'), ('Prescription', 'Prescription')],
        required=False,
        label="Filter by Document Type"
    )
    start_date = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(2000, 2100)), label="Start Date")
    end_date = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(2000, 2100)), label="End Date")

class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        fields = ['patient', 'status']

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['username', 'email', 'role', 'is_active']
