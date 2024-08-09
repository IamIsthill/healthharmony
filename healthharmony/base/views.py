from django.shortcuts import render
from django.contrib import messages
import requests
import environ
import logging
from healthharmony.base.functions import (
    get_season,
    pred,
    train_model,
    load_data_and_model,
    check_models,
)

# Models
from healthharmony.bed.models import BedStat

env = environ.Env()
environ.Env.read_env(env_file="healthharmony/.env")


# Create your views here.
logger = logging.getLogger(__name__)


def home(request):
    """
    Home view function to display the landing page with weather data, bed statistics,
    and model predictions.

    Fetches weather data from OpenWeatherMap API, loads the prediction model and related data,
    makes predictions, and retrieves bed statistics from the database.
    """
    try:
        # Check and train models if necessary
        check_models()
        train_model()
        df, model, le_season, le_sickness, le_weather = load_data_and_model()
    except Exception as e:
        logger.error(f"Error in loading data and model: {e}")
        messages.error(request, f"Error in loading data and model: {e}")
        return render(
            request, "landingpage.html", {"error": "Error in loading data and model."}
        )

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
        # Determine the current season
        season = get_season()
        predict = pred(season, weather, df, model, le_season, le_sickness, le_weather)
    except Exception as e:
        logger.error(f"Error in making prediction: {e}")
        messages.error(request, f"Error in making prediction: {e}")
        return render(
            request, "landingpage.html", {"error": "Error in making prediction."}
        )

    context = {}

    try:
        # Retrieve bed statistics from the database
        beds = BedStat.objects.all()
        context.update({"beds": beds})
    except Exception as e:
        logger.error(f"Error in retrieving bed statistics: {e}")
        messages.error(request, f"Error in retrieving bed statistics: {e}")

    context.update(
        {
            "temp": temp,
            "feels": feels,
            "predict": predict[0],
            "icon": icon,
        }
    )

    return render(request, "landingpage.html", context)
