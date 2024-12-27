from django.db import models
from patients.models import Patient
from accounts.models import User

class Appointment(models.Model):
    APPOINTMENT_TYPES = (
        ('Consultation', 'Consultation'),
        ('Certificate', 'Certificate'),
        ('Other', 'Other'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['Nurse', 'Physician', 'Dentist']})
    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPES)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')])

    def __str__(self):
        return f"Appointment for {self.patient.user.username} on {self.appointment_date}"
