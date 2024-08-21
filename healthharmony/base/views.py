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
        context = {
            "temp": temp,
            "feels": feels,
            "predict": predict[0],
            "icon": icon,
            "beds": beds,
        }
    except Exception as e:
        logger.error(f"Error in loading data and model: {e}")
        messages.error(request, f"Error in loading data and model: {e}")

    return render(request, "landingpage.html", context)
