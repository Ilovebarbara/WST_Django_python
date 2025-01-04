from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver



class Account(AbstractUser):
    ROLES = [
        ('Dentist', 'Dentist'),
        ('Nurse', 'Nurse'),
        ('Physician', 'Physician'),
        ('Patient', 'Patient'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLES, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'

    groups = models.ManyToManyField(Group, related_name='backend_account_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='backend_account_permissions', blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.username} ({self.role})"


class Staff(models.Model):
    SPECIALIZATION_CHOICES = [
        ('Dentist', 'Dentist'),
        ('Nurse', 'Nurse'),
        ('Physician', 'Physician'),
    ]

    staff_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    contact_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialization}"

    class Meta:
        verbose_name_plural = "Staff Members"
        ordering = ['specialization', 'user__last_name']


class Patient(models.Model):
    PATIENT_CLASSIFICATION_CHOICES = [
    ('Personnel', 'Personnel'),
    ('Faculty', 'Faculty'),
    ('Student', 'Student'),
    ]
   
    patient_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    patient_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.TextField()
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    campus = models.CharField(max_length=100)
    college_or_office = models.CharField(max_length=100)
    course_or_designation = models.CharField(max_length=100)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_relation = models.CharField(max_length=50)
    emergency_contact_no = models.CharField(max_length=15)
    blood_type = models.CharField(
        max_length=3,
        choices=[('A+', 'A+'), ('A-', 'A-'),
                 ('B+', 'B+'), ('B-', 'B-'),
                 ('AB+', 'AB+'), ('AB-', 'AB-'),
                 ('O+', 'O+'), ('O-', 'O-')]
    )
    allergies = models.TextField(blank=True, null=True)
    classification = models.CharField(
        max_length=20,
        choices=PATIENT_CLASSIFICATION_CHOICES,
        default='Student',  # Default value, can be adjusted
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_number})"

    def get_priority(self):
        """Return priority based on age."""
        return "Senior" if self.age >= 65 else "Regular"

    class Meta:
        verbose_name_plural = "Patients"
        ordering = ['last_name', 'first_name']
# Automatically set 'Senior Citizen' if age >= 65 when saving a Patient model
@receiver(pre_save, sender=Patient)
def set_senior_citizen_classification(sender, instance, **kwargs):
    if instance.age >= 65:
        instance.classification = 'Personnel'  # Change as per classification logic


# models.py
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
    ]

    CONSULTATION_CHOICES = [
        ('General', 'General'),
        ('Follow-up', 'Follow-up'),
        ('Emergency', 'Emergency'),
        ('Specialist', 'Specialist'),
    ]
    ROLE_CHOICES = [
        ('Senior Citizen', 'Senior Citizen'),
        ('Faculty', 'Faculty'),
        ('Personnel', 'Personnel'),
    ]

    consultation_type = models.CharField(max_length=100, choices=CONSULTATION_CHOICES, null=True)
    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    queue_id = models.IntegerField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"Queue {self.queue_id}: {self.consultation_type} - {self.status} ({self.patient})"
    
    def save(self, *args, **kwargs):

        if self.patient.age >= 65:
            self.priority = 'Senior'
        else:
            self.priority = 'Regular'
        super().save(*args, **kwargs)
    

class MedicalRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    height = models.FloatField()
    weight = models.FloatField()
    hr = models.PositiveIntegerField(verbose_name="Heart Rate")
    rr = models.PositiveIntegerField(verbose_name="Respiratory Rate")
    temperature = models.FloatField()
    bp = models.CharField(max_length=20, verbose_name="Blood Pressure")
    pain_scale = models.PositiveSmallIntegerField()
    other_symptoms = models.TextField(blank=True, null=True)
    initial_diagnosis = models.TextField()
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE, null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    
    def __str__(self):
        return f"Medical Record for {self.patient} on {self.date}"

    def archive(self):
        """Function to archive the medical record."""
        self.is_archived = True
        self.save()


class Queue(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('Regular', 'Regular'),
        ('Senior', 'Senior'),
    ]

    TRANSACTION_TYPE_CHOICES = [
        ('Consultation', 'Consultation'),
        ('Follow-Up', 'Follow-Up'),
        ('Procedure', 'Procedure'),
        ('Billing', 'Billing'),
    ]

    queue_id = models.AutoField(primary_key=True)
    queue_number = models.IntegerField()
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    window_number = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return f"Queue {self.queue_number} ({self.status})"

    def save(self, *args, **kwargs):
        # Automatically set priority based on patient's age
        if self.patient.age >= 65:
            self.priority = 'Senior'
        else:
            self.priority = 'Regular'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Queue Entries"
        ordering = ['status', 'priority', 'queue_number']

# Signal to handle archiving and deleting queue entry after consultation
@receiver(post_save, sender=MedicalRecord)
def handle_after_consultation(sender, instance, **kwargs):
    if instance.is_archived:
        # Find the related appointment and set its status to 'Completed'
        appointment = Appointment.objects.filter(patient=instance.patient, status='Pending').first()
        if appointment:
            appointment.status = 'Completed'
            appointment.save()

        # Delete the queue entry after consultation
        Queue.objects.filter(patient=instance.patient, status='In Progress').delete()