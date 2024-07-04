from django.shortcuts import render, redirect
from users.models import User
from .forms import PatientForm
import secrets
import string
from treatment.models import Illness
from datetime import datetime

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(generate_password())
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Specify the backend
            user.save()
            # login(request, user)
            return redirect('home')  # Redirect to the home page or another appropriate URL
    else:
        form = PatientForm()
    
    return render(request, 'staff/add-patient.html', {'form': form})

def overview(request):
    now = datetime.now()
    today_patient = Illness.objects.filter(updated__date = now.date()).count()
    context = {'today_patient' : today_patient}
    return render(request, 'staff/overview.html', context)