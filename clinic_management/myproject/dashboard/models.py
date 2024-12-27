from django.db import models
from accounts.models import User

class Dashboard(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    total_patients_served = models.IntegerField(default=0)
    patients_pending = models.IntegerField(default=0)
    patients_completed = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dashboard for {self.staff.username} on {self.date}"
