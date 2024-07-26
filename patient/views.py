from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import environ
from base.functions import get_season, pred, train_model, load_data_and_model
from django.utils import timezone
import json
from collections import defaultdict
from django.db.models import Prefetch
from django.db import connection

from treatment.models import Illness, DoctorDetail, IllnessTreatment
from bed.models import BedStat
from users.models import User

# Create your views here.
def overview_view(request):
    # set session data
    if 'email' not in request.session:
        request.session['email'] = request.user.email
    env = environ.Env()
    environ.Env.read_env(env_file='.env')

    train_model()
    df, model, le_season, le_sickness, le_weather = load_data_and_model()
    request_url = f"https://api.openweathermap.org/data/2.5/weather?appid={env.str('WEATHER')}&q=Bacolor,PH&units=metric"
    weatherData = requests.get(request_url).json()
    temp = weatherData['main']['temp']
    feels = weatherData['main']['feels_like']
    season = get_season()
    weather_info = weatherData['weather'][0]
    weather = weather_info['main']
    icon = weather_info['icon']
    predict = pred(season, weather, df, model, le_season, le_sickness, le_weather)

    context = {
        'temp': temp,
        'feels': feels,
        'predict': predict[0],
        'icon': icon,      
    }

    try:
        visits = Illness.objects.filter(patient = request.user).count() or 0
        treatments = Illness.objects.filter(patient = request.user, diagnosis__gt = '').count() or 0
        beds = BedStat.objects.all()
        doctors = DoctorDetail.objects.select_related('doctor')

        for doc in doctors:
            now = timezone.localtime().time()
            is_avail = doc.is_avail(now)
            setattr(doc, 'true_avail', is_avail)  

        context.update({
            'visits':visits,
            'treatments':treatments,  
            'beds': beds,
            'doctors': doctors,                 
        })
    except Exception as e:
        messages.error(request, f'Failed to fetch data: {e}')

    return render(request, 'patient/overview.html', context)

def records_view(request):
    if 'email' not in request.session:
        request.session['email'] = request.user.email
    context = {}
    try:
        treatments = Illness.objects.filter(patient=request.user).prefetch_related( 
            Prefetch(
                'illnesstreatment_set', queryset=IllnessTreatment.objects.select_related('inventory_detail')
                )
        )

        for illness in treatments:
            for treatment in illness.illnesstreatment_set.all():
                treatment.quantity = treatment.quantity or 0

        context.update({
            'treatments':treatments,
        })
        
    except Exception as e:
        messages.error(request, f'Failed to fetch data, please reload page : {e}')

    return render(request, 'patient/records.html', context)

def patient_view(request, pk):
    if request.user.id != pk:
        return redirect('home')
    if 'email' not in request.session:
        request.session['email'] = request.user.email
    context = {}
    now = timezone.now()

    if request.method == 'POST':
        try:
            user = request.user

            contact = request.POST.get('contact')
            year = request.POST.get('year')
            section = request.POST.get('section')
            program = request.POST.get('program')
            sex = request.POST.get('sex')
            
            # Update user fields
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            if contact:
                user.contact = contact
            if year:
                user.year = year
            if section:
                user.section = section
            if program:
                user.program = program
            if sex:
                user.sex = sex
            
            # Handle profile image upload
            if 'profile' in request.FILES:
                user.profile = request.FILES['profile']
            
            # Save the updated user
            user.save()

            messages.success(request, 'Profile updated successfully!')


            context.update({
                'user':user
            })

            return redirect('patient-profile', user.id)
        except TypeError as e:
            messages.error(request, f'{e}')
        except Exception as e:
            messages.error(request, f'{e}')

    try:
        user = User.objects.prefetch_related('blood_pressures').get(email= request.user.email)
        if user.DOB is not None:
            age = now.year - user.DOB.year
            context.update({
                'age':age
            })

        if user.blood_pressures.first():
            latest_bp = user.blood_pressures.first()
            if latest_bp.blood_pressure is not None:
                blood_pressure = latest_bp.blood_pressure
                context.update({
                    'blood_pressure':blood_pressure
                })

        context.update({
            'user':user
        })

    except Exception as e:
        messages.error(request, f'Error: {e} \nPlease reload page')

    return render(request, 'patient/patient.html', context)