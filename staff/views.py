from django.shortcuts import render, redirect
from users.models import User
from .forms import PatientForm
import secrets
import string
from treatment.models import Illness, Certificate, Category
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
import json
from collections import defaultdict
from dateutil.relativedelta import relativedelta

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        email = request.POST.get('email')
        user = User.objects.get(email = email)
        if user:
            messages.error(request, 'User already exists')
            return redirect('register')
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
    now = timezone.now()
    start_date = (now - timedelta(days=365)).replace(day=1)
    today_patient = Illness.objects.filter(updated__date = now.date()).count()
    total_patient = Illness.objects.all().count()
    monthly_medcert = Certificate.objects.filter(requested__month = now.month,requested__year = now.year, released = True).count()
    categories = Category.objects.all()
    category_data = list(categories.values('id', 'category'))
    category_counts = defaultdict(lambda: defaultdict(int))
    month_cases_count = defaultdict(lambda: defaultdict(int))
    weekly_cases_count = defaultdict(lambda: defaultdict(int))
    # category_counts = []

    for category in categories:
        month_cases = []
        for month_offset in range(13):  # 13 months to include the current month
            current_month = start_date + relativedelta(months=month_offset)
            next_month = current_month + relativedelta(months=1)
            if month_offset == 12:  
                illness_count = Illness.objects.filter(
                    illness_category=category,
                    updated__gte=current_month,
                    updated__lte=now 
                ).count()
            else:
                illness_count = Illness.objects.filter(
                    illness_category=category,
                    updated__gte=current_month,
                    updated__lt=next_month
                ).count()
            # month_cases[current_month.strftime('%B')] = illness_count
            month_cases.append((current_month.strftime('%B'), illness_count))

        five_days_count = []
        last30days = (now - timedelta(days=30))
        for five_offset in range(6):
            current_day = last30days + timedelta(days=five_offset*5)
            next_five = current_day + timedelta(days=5)
            illness_count = Illness.objects.filter(
                    illness_category=category,
                    updated__gte=current_day,
                    updated__lt=next_five 
            ).count()
            five_days_count.append((current_day.strftime('%B %d'), illness_count))
        
        weekly_count = []
        week = now - timedelta(days=6)
        for day_offset in range(7):
            current_day = week + timedelta(days = day_offset*1)
            start_of_day = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)
            illness_count = Illness.objects.filter(
                    illness_category=category,
                    updated__gte=start_of_day,
                    updated__lte=end_of_day,
            ).count()
            weekly_count.append((current_day.strftime('%A, %d'), illness_count))
            

        weekly_cases_count[category.id] = json.dumps(weekly_count)
        month_cases_count[category.id] = json.dumps(five_days_count)
        category_counts[category.id] = json.dumps(month_cases)
    

    context = {'today_patient' : today_patient, 'monthly_medcert':monthly_medcert, 'categories':categories, 'category_counts':category_counts, 'category_names':category_data, 'month_cases_count':month_cases_count, 'weekly_cases_count':weekly_cases_count, 'total_patient':total_patient}
    return render(request, 'staff/overview.html', context)

def add_issue(request):
    patients = User.objects.filter(access=1)
    if request.method == 'POST':
        patient = User.objects.get(email=request.POST.get('patient'))
        try:
            illness = Illness.objects.create(
                patient = patient,
                issue = request.POST.get('issue'),
            )
        except:
            messages.error(request, 'Unable to add issue')
    context = {'patients':patients}
    return render(request,'staff/add-issue.html', context)