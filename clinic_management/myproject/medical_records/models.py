from django.db import models
from patients.models import Patient
from accounts.models import User

class MedicalRecord(models.Model):
    TRANSACTION_TYPES = (
        ('Consultation', 'Consultation'),
        ('Dental', 'Dental'),
        ('Other', 'Other'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['Nurse', 'Physician', 'Dentist']})
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    date_time = models.DateTimeField(auto_now_add=True)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    assessment = models.TextField()
    HR = models.CharField(max_length=10)
    RR = models.CharField(max_length=10)
    temp = models.DecimalField(max_digits=5, decimal_places=2)
    bp = models.CharField(max_length=20)
    pain_scale = models.IntegerField()
    symptoms = models.TextField(null=True, blank=True)
    initial_diagnosis = models.CharField(max_length=100)

    def __str__(self):
        return f"Medical Record for {self.patient.user.username} - {self.transaction_type}"
