from django.db import models

class User(models.Model):
    ROLES = (
        ('Admin', 'Admin'),
        ('Nurse', 'Nurse'),
        ('Physician', 'Physician'),
        ('Dentist', 'Dentist'),
        ('Patient', 'Patient'),
    )

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50, choices=ROLES)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.username
