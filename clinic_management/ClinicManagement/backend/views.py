from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib.auth import logout
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.db.models import Count
from .models import Account, Patient, Staff, Appointment, MedicalRecord, Queue
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Max
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password

queue_counter = 1

# Role-based decorators for permissions
staff_required = [login_required, lambda u: hasattr(u, 'is_staff') and u.is_staff]
patient_required = [login_required, lambda u: hasattr(u, 'is_patient') and u.is_patient()]
    # Landing Page
def home(request):
    return render(request, 'clinic!/index.html')
    # Staff Login
def staff_login(request):
    if request.method == "POST":
        login_entry = request.POST['login_entry']  # Either username or email
        password = request.POST['password']

        try:
            # First, check if the entry is a username or an email
            if '@' in login_entry:  # It's an email
                user = Account.objects.get(email=login_entry)
            else:  # It's a username
                user = Account.objects.get(username=login_entry)

            if user.password == password:  # Assuming password is stored as plain text (not recommended)
                # Log the user in (custom logic)
                request.session['user_id'] = user.id
                return redirect('staff_dashboard')  # Redirect to the dashboard
            else:
                messages.error(request, "Invalid username/email or password.")
        except Account.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, 'clinic!/staff_login.html')
    # Staff Dashboard Contents

def staff_dashboard(request):

    return render(request, 'clinic!/staff_dashboard.html')


def staff_appointments(request):
    # Fetch all appointments, ordered by queue_id
    appointments = Appointment.objects.all().order_by('queue_id')

    # Get the consultation_type and role filters from the GET request, default to 'All'
    consultation_type_filter = request.GET.get('consultation_type', 'All')
    role_filter = request.GET.get('role', 'All')

    # Apply consultation_type filter if it is not 'All'
    if consultation_type_filter != 'All':
        appointments = appointments.filter(consultation_type=consultation_type_filter)

    # Apply role filter if it is not 'All'
    if role_filter != 'All':
        appointments = appointments.filter(role=role_filter)

    # Get the current queue from the session (default to 1)
    queue_id = request.session.get('current_queue', 1)

    # Handle the actions (Next, Previous, Reset, and Update Status)
    if request.method == 'POST':
        action = request.POST.get('action')

        # Action for going to the next appointment
        if action == 'next':
            # Get the current appointment based on the current queue_id
            current_appointment = appointments.filter(queue_id=queue_id).first()

            if current_appointment:
                # Create a medical record based on the current appointment data

                  # Delete the current appointment from the Appointment table
                current_appointment.delete()

                next_appointment = appointments.filter(queue_id__gt=queue_id).first()
                if next_appointment:
                    queue_id = next_appointment.queue_id
                else:
                    # If no more appointments, reset to the first one (optional)
                    queue_id = appointments.first().queue_id

            # Update the session with the new queue_id
            request.session['current_queue'] = queue_id

            return redirect('staff_appointments')  # Redirect to refresh the page
       

        # Action for resetting the queue and deleting all appointments
        elif action == 'reset':
            # Confirm reset action and delete all appointments
            appointments.delete()
            queue_id = 1  # Reset to the first queue
            return redirect('staff_appointments')  # Redirect to reset the state

        # Action for updating appointment status
        elif 'update_status' in request.POST:
            appointment_id = request.POST.get('appointment_id')
            new_status = request.POST.get('status')

            # Update the status of the specific appointment
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            appointment.status = new_status
            appointment.save()

        # Action for deleting an appointment
        elif 'delete_appointment' in request.POST:
            appointment_id = request.POST.get('appointment_id')
            try:
                appointment = Appointment.objects.get(appointment_id=appointment_id)
                appointment.delete()  # Delete the appointment
            except Appointment.DoesNotExist:
                # If appointment is not found, handle exception (optional)
                pass

            # Redirect to avoid resubmission of the form
            return redirect('staff_appointments')

        # Store the updated queue_id in the session
        request.session['current_queue'] = queue_id

    # Get the current appointment based on the updated queue_id
    current_appointment = appointments.filter(queue_id=queue_id).first()

    # Return the view with necessary data
    return render(request, 'clinic!/staff_dashboard_contents/queueing.html', {
        'appointments': appointments,
        'current_appointment': current_appointment,
        'consultation_type_filter': consultation_type_filter,  # Pass the consultation_type filter to the template
        'role_filter': role_filter,  # Pass the role filter to the template
    })


def complete_consultation(request, record_id):
    # Fetch the MedicalRecord and mark it as archived
    medical_record = MedicalRecord.objects.get(id=record_id)
    
    # Call the archive method to mark it as archived
    medical_record.archive()

    # Optionally, update the related appointment status to 'Completed'
    appointment = Appointment.objects.get(patient=medical_record.patient, status='Pending')
    appointment.status = 'Completed'
    appointment.save()

    return redirect('staff_appointments')  # Redirect to a different view (e.g., appointment list)


def add_patient(request):
    return render(request, 'clinic!/staff_dashboard_contents/add_patient.html')

def create_staff(request):
    return render(request, 'clinic!/admin_dashboard_contents/add_staff.html')

def register_patient(request):

    if request.method == "POST":
    # Gather data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST['username']
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
    try:
        age = int(request.POST.get('age'))  # Convert to integer
    except ValueError:
        messages.error(request, "Please enter a valid number for age.")
        return render(request, 'clinic!/staff_dashboard_contents/add_patient.html')

    sex = request.POST.get('sex')
    campus = request.POST.get('campus')
    college_or_office = request.POST.get('college_or_office')
    course_or_designation = request.POST.get('course_or_designation')
    emergency_contact_name = request.POST.get('emergency_contact_name')
    emergency_contact_relation = request.POST.get('emergency_contact_relation')
    emergency_contact_no = request.POST.get('emergency_contact_no')
    blood_type = request.POST.get('blood_type')
    allergies = request.POST.get('allergies')
    classification = request.POST.get('classification')

    # Check if a user with the email already exists
    if Account.objects.filter(email=email).exists():
        messages.error(request, "A user with this email already exists. Please use a different email or log in.")
        return render(request, 'clinic!/staff_dashboard_contents/add_patient.html')
    if Account.objects.filter(username=username).exists():
        messages.error(request, "A user with this username already exists. Please choose a different username.")
        return render(request, 'clinic!/staff_dashboard_contents/add_patient.html')

    # Create User and Patient objects
    try:
        user = Account(username=username, email=email, first_name=first_name, last_name=last_name)
        user.password = password  # Store password in plain text (not recommended)
        user.save()
        
        patient = Patient(
            user=user,
            patient_number=f"P{user.id:06d}",
            first_name=first_name,
            last_name=last_name,
            address=address,
            age=age,
            sex=sex,
            campus=campus,
            college_or_office=college_or_office,
            course_or_designation=course_or_designation,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_relation=emergency_contact_relation,
            emergency_contact_no=emergency_contact_no,
            blood_type=blood_type,
            allergies=allergies,
            classification=classification
        )
        patient.save()
        messages.success(request, "Registration successful!")
        return redirect('add_patient')
    except Exception as e:
        messages.error(request, f"Error: {e}")


    return render(request, 'clinic!/staff_dashboard_contents/add_patient.html')

def staff_medical_records(request):
    medical_records = MedicalRecord.objects.all()  # Fetch records
    return render(request, 'clinic!/staff_dashboard_contents/medical_records.html',{'medical_records': medical_records})

def staff_settings(request):
    return render(request, 'clinic!/staff_dashboard_contents/staff_settings.html')
    # Logout
def logout():
    return redirect('logout')

    # Patient Dashboard Contents
def patient_dashboard(request):
    return render(request, 'clinic!/patient_dashboard.html')

def patient_login(request):
    if request.method == "POST":
        login_entry = request.POST['login_entry']  # Either username or email
        password = request.POST['password']

        try:
            # First, check if the entry is a username or an email
            if '@' in login_entry:  # It's an email
                user = Account.objects.get(email=login_entry)
            else:  # It's a username
                user = Account.objects.get(username=login_entry)

            if user.password == password:  # Assuming password is stored as plain text (not recommended)
                # Log the user in (custom logic)
                request.session['user_id'] = user.id
                return redirect('patient_dashboard')  # Redirect to the dashboard
            else:
                messages.error(request, "Invalid username/email or password.")
        except Account.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, 'clinic!/patient_login.html')

###def patient_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        try:
            # Check if the user exists in the Accounts model
            user = Account.objects.get(username=username)
            if user.password == password:  # Assuming password is stored as plain text (not recommended)
                # Log the user in (custom logic)
                request.session['user_id'] = user.id
                return redirect('patient_dashboard')  # Redirect to the dashboard
            else:
                messages.error(request, "Invalid username or password.")
        except Account.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, 'clinic!/patient_login.html')

def patient_register(request):
    if request.method == "POST":
        # Gather data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST['username']
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        try:
            age = int(request.POST.get('age'))  # Convert to integer
        except ValueError:
            messages.error(request, "Please enter a valid number for age.")
            return render(request, 'clinic!/patient_register.html')

        sex = request.POST.get('sex')
        campus = request.POST.get('campus')
        college_or_office = request.POST.get('college_or_office')
        course_or_designation = request.POST.get('course_or_designation')
        emergency_contact_name = request.POST.get('emergency_contact_name')
        emergency_contact_relation = request.POST.get('emergency_contact_relation')
        emergency_contact_no = request.POST.get('emergency_contact_no')
        blood_type = request.POST.get('blood_type')
        allergies = request.POST.get('allergies')
        classification = request.POST.get('classification')
        
        # Check if a user with the email already exists
        if Account.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists. Please use a different email or log in.")
            return render(request, 'clinic!/patient_register.html')
        if Account.objects.filter(username=username).exists():
            messages.error(request, "A user with this username already exists. Please choose a different username.")
            return render(request, 'clinic!/patient_register.html')

        # Create User and Patient objects
        try:
            user = Account(username=username, email=email, first_name=first_name, last_name=last_name)
            user.password = password  # Store password in plain text (not recommended)
            user.save()
            
            patient = Patient(
                user=user,
                patient_number=f"P{user.id:06d}",
                first_name=first_name,
                last_name=last_name,
                address=address,
                age=age,
                sex=sex,
                campus=campus,
                college_or_office=college_or_office,
                course_or_designation=course_or_designation,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_relation=emergency_contact_relation,
                emergency_contact_no=emergency_contact_no,
                blood_type=blood_type,
                allergies=allergies,
                classification=classification
            )
            patient.save()
            messages.success(request, "Registration successful!")
            return redirect('patient_login')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    
    return render(request, 'clinic!/patient_register.html')


def patient_appointments(request):
    if request.method == 'POST':
        patient_name = request.POST.get('patient')
        staff_name = request.POST.get('staff')
        consultation_type = request.POST.get('consultation_type')
        date = request.POST.get('date')
        time = request.POST.get('time')
        status = request.POST.get('status')
        queue_id = request.POST.get('queue_id')
        role = request.POST.get('role')

        try:
            patient = Patient.objects.get(name=patient_name)
            staff = Staff.objects.get(name=staff_name)
        except Patient.DoesNotExist or Staff.DoesNotExist:
            messages.error(request, "Patient or Staff not found!")
            return redirect('patient_appointments')

        # Create the appointment
        appointment = Appointment.objects.create(
            consultation_type=consultation_type,
            patient=patient,
            staff=staff,
            date=date,
            time=time,
            status=status,
            queue_id=queue_id,
            role=role
        )

        # Success message
        messages.success(request, "Appointment booked successfully!")
        return redirect('patient_appointments')

    # Fetch patients and staff for use in the template
    patients = Patient.objects.all()
    staff = Staff.objects.all()

    return render(request, 'clinic!/patient_dashboard_contents/appointments.html', {'patients': patients, 'staff': staff})


def patient_settings(request):
    return render(request, 'clinic!/patient_dashboard_contents/patient_settings.html')
    # Logout

def logout():
    return redirect('home')

#ADMIN PART
def admin_login(request):
    if request.method == "POST":
        login_entry = request.POST['login_entry']  # Either username or email
        password = request.POST['password']

        try:
            # First, check if the entry is a username or an email
            if '@' in login_entry:  # It's an email
                user = Account.objects.get(email=login_entry)
            else:  # It's a username
                user = Account.objects.get(username=login_entry)

            if user.password == password:  # Assuming password is stored as plain text (not recommended)
                # Log the user in (custom logic)
                request.session['user_id'] = user.id
                return redirect('admin_dashboard')  # Redirect to the dashboard
            else:
                messages.error(request, "Invalid username/email or password.")
        except Account.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, 'clinic!/admin_login.html')

def staff_register(request):
    if request.method == "POST":
        # Gather data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        specialization = request.POST.get('specialization')
        contact_info = request.POST.get('contact_info')
        
        # Check if a user with the email or username already exists
        if Account.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists. Please use a different email.")
            return render(request, 'create_Staff')
        if Account.objects.filter(username=username).exists():
            messages.error(request, "A user with this username already exists. Please choose a different username.")
            return render(request, 'create_Staff')
        # Create the user and staff objects
        try:
            # Create the user without hashing the password
            user = Account(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=specialization,
                is_staff=True
            )
            user.password = password  # Store the plain text password (not secure)
            user.save()

            # Create the staff profile
            staff = Staff(
                user=user,
                specialization=specialization,
                contact_info=contact_info
            )
            staff.save()

            messages.success(request, "Staff member added successfully!")
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('add_staff')

    return render(request, 'clinic!/admin_dashboard_contents/add_staff.html')

def update_staff_password(request):
    if request.method == "POST":
        # Get current user
        user = request.user
        
        # Gather data from the form
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the current password matches the stored password
        if not check_password(current_password, user.password):
            messages.error(request, "Current password is incorrect.")
            return render(request, 'clinic!/staff_dashboard_contents/staff_settings.html')

        # Check if the new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'clinic!/staff_dashboard_contents/staff_settings.html')

        # Check if the new password is secure (optional, but recommended)
#        if len(new_password) < 8:
#           messages.error(request, "Password must be at least 8 characters long.")
#            return render(request, 'clinic!/staff_dashboard_contents/staff_settings.html')

        try:
            # Update the password securely
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password updated successfully! Please log in again.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error updating password: {e}")
            return render(request, 'clinic!/staff_dashboard_contents/staff_settings.html')

    # Render the password update form
    return render(request, 'clinic!/staff_dashboard_contents/staff_settings.html')

def patient_queue(request):
      # Fetch all appointments, ordered by queue_id
    appointments = Appointment.objects.all().order_by('queue_id')

    # Get the consultation_type and role filters from the GET request, default to 'All'
    consultation_type_filter = request.GET.get('consultation_type', 'All')
    role_filter = request.GET.get('role', 'All')

    # Apply consultation_type filter if it is not 'All'
    if consultation_type_filter != 'All':
        appointments = appointments.filter(consultation_type=consultation_type_filter)

    # Apply role filter if it is not 'All'
    if role_filter != 'All':
        appointments = appointments.filter(role=role_filter)

    # Get the current queue from the session (default to 1)
    queue_id = request.session.get('current_queue', 1)

    # Handle the actions (Next, Previous, Reset, and Update Status)
    if request.method == 'POST':
        action = request.POST.get('action')

        # Action for going to the next appointment
        if action == 'next':
            # Get the current appointment based on the current queue_id
            current_appointment = appointments.filter(queue_id=queue_id).first()

            if current_appointment:
                # Create a medical record based on the current appointment data

                  # Delete the current appointment from the Appointment table
                current_appointment.delete()

                next_appointment = appointments.filter(queue_id__gt=queue_id).first()
                if next_appointment:
                    queue_id = next_appointment.queue_id
                else:
                    # If no more appointments, reset to the first one (optional)
                    queue_id = appointments.first().queue_id

            # Update the session with the new queue_id
            request.session['current_queue'] = queue_id

            return redirect('staff_appointments')  # Redirect to refresh the page
       

        # Action for resetting the queue and deleting all appointments
        elif action == 'reset':
            # Confirm reset action and delete all appointments
            appointments.delete()
            queue_id = 1  # Reset to the first queue
            return redirect('staff_appointments')  # Redirect to reset the state

        # Action for updating appointment status
        elif 'update_status' in request.POST:
            appointment_id = request.POST.get('appointment_id')
            new_status = request.POST.get('status')

            # Update the status of the specific appointment
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            appointment.status = new_status
            appointment.save()

        # Action for deleting an appointment
        elif 'delete_appointment' in request.POST:
            appointment_id = request.POST.get('appointment_id')
            try:
                appointment = Appointment.objects.get(appointment_id=appointment_id)
                appointment.delete()  # Delete the appointment
            except Appointment.DoesNotExist:
                # If appointment is not found, handle exception (optional)
                pass

            # Redirect to avoid resubmission of the form
            return redirect('staff_appointments')

        # Store the updated queue_id in the session
        request.session['current_queue'] = queue_id

    # Get the current appointment based on the updated queue_id
    current_appointment = appointments.filter(queue_id=queue_id).first()

    # Return the view with necessary data
    return render(request, 'clinic!/patient_dashboard_contents/patient_queue.html', {
        'appointments': appointments,
        'current_appointment': current_appointment,
        'consultation_type_filter': consultation_type_filter,  # Pass the consultation_type filter to the template
        'role_filter': role_filter,  # Pass the role filter to the template
    })
 

def admin_dashboard(request):
    return render(request, 'clinic!/admin_dashboard.html')
def add_staff(request):
    return render(request, 'clinic!/admin_dashboard_contents/add_staff.html')
#ADMIN PART
#def list_accounts(request):
    accounts = Account.objects.all()
    return render(request, 'clinic!/admin_dashboard.html', {'accounts': accounts})
#ADMIN PART
###def create_account(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        new_account = Account.objects.create(username=username, email=email, password=password, role=role)
        new_account.save()
        messages.success(request, 'Account created successfully!')
        return redirect('admin_list_accounts')
    return render(request, 'clinic!/admin_dashboard.html')
#ADMIN PART
#def edit_account(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    if request.method == 'POST':
        account.username = request.POST['username']
        account.email = request.POST['email']
        account.role = request.POST['role']
        account.save()
        messages.success(request, 'Account updated successfully!')
        return redirect('admin_list_accounts')
    return render(request, 'clinic!/admin_dashboard.html', {'account': account})

#def delete_account(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    account.delete()
    messages.success(request, 'Account deleted successfully!')
    return redirect('admin_list_accounts')


def reset_queue(request):
    if request.method == 'POST':
        Appointment.objects.all().delete()
        return JsonResponse({'message': 'Queue reset successful'})
    








