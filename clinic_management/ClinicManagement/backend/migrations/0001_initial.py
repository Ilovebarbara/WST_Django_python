# Generated by Django 5.1.4 on 2024-12-28 11:18

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.CharField(blank=True, choices=[('Dentist', 'Dentist'), ('Nurse', 'Nurse'), ('Physician', 'Physician'), ('Patient', 'Patient')], max_length=20, null=True)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('groups', models.ManyToManyField(blank=True, related_name='backend_account_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='backend_account_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('patient_id', models.AutoField(primary_key=True, serialize=False)),
                ('patient_number', models.CharField(max_length=20, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('address', models.TextField()),
                ('age', models.PositiveIntegerField()),
                ('sex', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('campus', models.CharField(max_length=100)),
                ('college_or_office', models.CharField(max_length=100)),
                ('course_or_designation', models.CharField(max_length=100)),
                ('emergency_contact_name', models.CharField(max_length=100)),
                ('emergency_contact_relation', models.CharField(max_length=50)),
                ('emergency_contact_no', models.CharField(max_length=15)),
                ('blood_type', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')], max_length=3)),
                ('allergies', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='backend.account')),
            ],
            options={
                'verbose_name_plural': 'Patients',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('queue_id', models.AutoField(primary_key=True, serialize=False)),
                ('queue_number', models.IntegerField()),
                ('transaction_type', models.CharField(max_length=50)),
                ('window_number', models.PositiveSmallIntegerField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], max_length=20)),
                ('priority', models.CharField(choices=[('Regular', 'Regular'), ('High', 'High'), ('Urgent', 'Urgent')], max_length=20)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.patient')),
            ],
            options={
                'verbose_name_plural': 'Queue Entries',
                'ordering': ['status', 'priority', 'queue_number'],
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('staff_id', models.AutoField(primary_key=True, serialize=False)),
                ('specialization', models.CharField(choices=[('Dentist', 'Dentist'), ('Nurse', 'Nurse'), ('Physician', 'Physician')], max_length=20)),
                ('contact_info', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='backend.account')),
            ],
            options={
                'verbose_name_plural': 'Staff Members',
                'ordering': ['specialization', 'user__last_name'],
            },
        ),
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('record_id', models.AutoField(primary_key=True, serialize=False)),
                ('transaction_type', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('height', models.FloatField()),
                ('weight', models.FloatField()),
                ('hr', models.PositiveIntegerField(verbose_name='Heart Rate')),
                ('rr', models.PositiveIntegerField(verbose_name='Respiratory Rate')),
                ('temperature', models.FloatField()),
                ('bp', models.CharField(max_length=20, verbose_name='Blood Pressure')),
                ('pain_scale', models.PositiveSmallIntegerField()),
                ('other_symptoms', models.TextField(blank=True, null=True)),
                ('initial_diagnosis', models.TextField()),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.patient')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.staff')),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('appointment_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('duration', models.DurationField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Completed', 'Completed')], max_length=20)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.patient')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.staff')),
            ],
        ),
    ]
