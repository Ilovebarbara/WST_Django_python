# Generated by Django 5.1.4 on 2025-01-01 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_remove_appointment_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='appointment_id',
        ),
        migrations.AddField(
            model_name='appointment',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]
