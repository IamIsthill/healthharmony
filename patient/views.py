from django.shortcuts import render
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
