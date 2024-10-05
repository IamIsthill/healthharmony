from django.shortcuts import render
from django.contrib import messages
import requests
import environ
import logging
from concurrent.futures import as_completed, ThreadPoolExecutor
from healthharmony.base.functions import (
    get_season,
    pred,
    train_model,
    load_data_and_model,
    check_models,
    get_prediction,
    get_beds,
)

# Models
from healthharmony.models.bed.models import BedStat, Ambulansya, WheelChair
from healthharmony.models.treatment.models import DoctorDetail
from healthharmony.base.serializers import DoctorSerializer
from healthharmony.users.models import User
from healthharmony.app.settings import env


# Create your views here.
logger = logging.getLogger(__name__)


def home(request):
    context = {}
    try:
        # Fetch weather data from OpenWeatherMap API
        request_url = f"https://api.openweathermap.org/data/2.5/weather?appid={env.str('WEATHER')}&q=Bacolor,PH&units=metric"
        weatherData = requests.get(request_url).json()
        temp = weatherData["main"]["temp"]
        feels = weatherData["main"]["feels_like"]
        weather_info = weatherData["weather"][0]
        weather = weather_info["main"]
        icon = weather_info["icon"]
    except Exception as e:
        logger.error(f"Error in fetching weather data: {e}")
        messages.error(request, f"Error in fetching weather data: {e}")
        return render(
            request, "landingpage.html", {"error": "Error in fetching weather data."}
        )

    try:
        df, model, le_season, le_sickness, le_weather = load_data_and_model()
        with ThreadPoolExecutor() as tp:
            futures = {
                tp.submit(check_models): "check_models",
                tp.submit(train_model): "train_model",
                tp.submit(
                    get_prediction,
                    weather,
                    df,
                    model,
                    le_season,
                    le_sickness,
                    le_weather,
                    request,
                    messages,
                ): "get_prediction",
                tp.submit(get_beds, BedStat, messages, request): "get_beds",
                tp.submit(get_doctors_sched, request): "get_doctors_sched",
                tp.submit(get_ambulance, request): "get_ambulance",
                tp.submit(get_wheelchairs, request): "get_wheelchairs",
            }
            results = {}
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    logger.error(f"{key} generated an exception: {e}")
                    results[key] = 0
        request, predict = results["get_prediction"]
        request, beds = results["get_beds"]
        request, ambulances = results["get_ambulance"]
        request, wheelchair_quantity = results["get_wheelchairs"]
        doctor_data = results["get_doctors_sched"]
        context = {
            "temp": temp,
            "feels": feels,
            "predict": predict,
            "icon": icon,
            "beds": beds,
            "doctor_data": doctor_data,
            "ambulances": ambulances,
            "wheelchair_quantity": wheelchair_quantity,
        }
    except Exception as e:
        logger.error(f"Error in loading data and model: {e}")
        messages.error(request, f"Error in loading data and model: {e}")

    return render(request, "landingpage.html", context)


def get_doctors_sched(request):
    try:
        doctors = User.objects.filter(access=3)
        doctor_data = []
        if doctors:
            for doctor in doctors:
                data = DoctorSerializer(doctor)
                doctor_data.append(data.data)
        return doctor_data
    except Exception as e:
        logger.info(f"Failed to fetch the doctor schedule: {str(e)}")
        messages.error(request, "Failed to fetch required data. Please try again.")
        return []


def get_ambulance(request):
    try:
        ambulance = Ambulansya.objects.all()
    except Exception as e:
        logger.warning(f"Failure to fetch ambulance data: {str(e)}")
        messages.error(request, "Failed to fetch required data. Please try again.")

    if ambulance:
        return request, ambulance
    else:
        return request, None


def get_wheelchairs(request):
    try:
        wheelchairs = WheelChair.objects.filter(is_avail=True)
    except Exception as e:
        logger.warning(f"Failure to fetch wheelchair data: {str(e)}")
        messages.error(request, "Failed to fetch required data. Please try again.")

    wheelchair_quantity = 0
    if wheelchairs:
        for wheelchair in wheelchairs:
            wheelchair_quantity += wheelchair.quantity
    return request, wheelchair_quantity
