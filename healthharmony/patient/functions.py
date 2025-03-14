from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib import messages
import logging
from django.core.cache import cache
import requests

from healthharmony.base.functions import (
    get_season,
    pred,
    train_model,
    load_data_and_model,
)

# from allauth.socialaccount.models import SocialAccount
from healthharmony.users.models import User
from healthharmony.models.treatment.models import Illness, DoctorDetail
from healthharmony.models.bed.models import BedStat
from healthharmony.administrator.models import Log


logger = logging.getLogger(__name__)


# def get_social_picture(user):
#     """get picture from the email metadata"""
#     try:
#         social = SocialAccount.objects.get(user=user, provider="google")
#         return social.extra_data.get("picture")
#     except SocialAccount.DoesNotExist:
#         return None


def calculate_age(DOB):
    """Calculate the age from the date of birth"""
    now = timezone.now()
    if DOB:
        age = now.year - DOB.year
        if now.year > DOB.year: 
            if now.month == DOB.month and now.day > DOB.day:
                age = age - 1
            elif now.month > DOB.month:
                age = age - 1

        return age
    return None


def get_latest_blood_pressure(user):
    """Retrieve the latest blood pressure for the user."""
    latest_bp = user.blood_pressures.first()
    if latest_bp and latest_bp.blood_pressure:
        return latest_bp.blood_pressure
    return None


def update_patient_view_context(request, context, pk):
    """Update the context with the required information"""
    try:
        user_cache = cache.get("user_cache", {})
        user = user_cache.get(f"{pk}_detailed")
        if not user:
            user = User.objects.prefetch_related("blood_pressures").get(id=int(pk))
            user_cache[f"{pk}_detailed"] = user
            cache.set("user_cache", user_cache, timeout=120 * 60)

    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return

    context["user"] = user
    context["age"] = calculate_age(user.DOB)
    context["blood_pressure"] = get_latest_blood_pressure(user)

    # picture = get_social_picture(user)
    picture = None
    if picture:
        context["picture"] = picture


"""overview_view"""


def get_weather(context, env):
    """
    Fetches weather data and updates the context with weather details.

    Parameters:
    - context (dict): The context dictionary to update with weather data.
    - env (environ.Env): The environment object for reading environment variables.
    """
    try:
        df, model, le_season, le_sickness, le_weather = load_data_and_model()
        request_url = f"https://api.openweathermap.org/data/2.5/weather?appid={env.str('WEATHER')}&q=Bacolor,PH&units=metric"
        weatherData = requests.get(request_url).json()
        temp = weatherData["main"]["temp"]
        feels = weatherData["main"]["feels_like"]
        season = get_season()
        weather_info = weatherData["weather"][0]
        weather = weather_info["main"]
        icon = weather_info["icon"]
        predict = pred(season, weather, df, model, le_season, le_sickness, le_weather)

        context.update(
            {
                "temp": temp,
                "feels": feels,
                "predict": predict[0],
                "icon": icon,
            }
        )
        logger.info("Weather data fetched successfully")
    except Exception as e:
        logger.error(f"Failed to fetch weather data: {e}")
        context.update({"weather_error": f"Failed to fetch weather data: {e}"})


def fetch_overview_data(context, request):
    """
    Fetches overview data such as visits, treatments, beds, and doctors, and updates the context.

    Parameters:
    - context (dict): The context dictionary to update with overview data.
    - request (HttpRequest): The Django request object containing user information.
    """
    try:
        illness_cache = cache.get("illness_cache", {})
        visits = illness_cache.get(f"patient_page_{request.user.id}_visits")
        if not visits:
            visits = Illness.objects.filter(patient=request.user).count() or 0
            illness_cache[f"patient_page_{request.user.id}_visits"] = visits
            cache.set("illness_cache", illness_cache, timeout=(60 * 60 * 2))

        treatments = illness_cache.get(f"patient_page_{request.user.id}_treatments")
        if not treatments:
            treatments = (
                Illness.objects.filter(patient=request.user, diagnosis__gt="").count()
                or 0
            )
            illness_cache[f"patient_page_{request.user.id}_treatments"] = treatments
            cache.set("illness_cache", illness_cache, timeout=(60 * 60 * 2))

        bed_cache = cache.get("bed_cache", {})
        beds = bed_cache.get("query")
        if not beds:
            beds = BedStat.objects.all()
            bed_cache["query"] = beds
            cache.set("bed_cache", bed_cache, timeout=(60 * 60 * 2))

        doctor_cache = cache.get("doctor_cache", {})
        doctors = doctor_cache.get("doctor_detailed")
        if not doctors:
            doctors = DoctorDetail.objects.filter(doctor__access=3).select_related(
                "doctor"
            )
            doctor_cache["doctor_detailed"] = doctors
            cache.set("doctor_cache", doctor_cache, timeout=(60 * 60 * 2))

        for doc in doctors:
            now = timezone.localtime().time()
            is_avail = doc.is_avail(now)
            setattr(doc, "true_avail", is_avail)

        context.update(
            {
                "visits": visits,
                "treatments": treatments,
                "beds": beds,
                "doctors": doctors,
            }
        )
        logger.info("Overview data fetched successfully")
    except Exception as e:
        logger.error(f"Failed to fetch overview data: {e}")
        context.update({"data_error": f"Failed to fetch data: {e}"})
