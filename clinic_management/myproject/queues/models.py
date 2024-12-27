from django.db import models
from patients.models import Patient
from accounts.models import User

class Queue(models.Model):
    QUEUE_STATUS = (
        ('Waiting', 'Waiting'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['Nurse', 'Physician', 'Dentist']})
    transaction_type = models.CharField(max_length=50)
    queue_number = models.IntegerField()
    queue_status = models.CharField(max_length=50, choices=QUEUE_STATUS)
    window_number = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Queue No. {self.queue_number} for {self.patient.user.username}"
