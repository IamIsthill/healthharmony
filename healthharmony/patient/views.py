from django.shortcuts import render, redirect
from django.contrib import messages
import environ
from django.db.models import Prefetch
import threading

from healthharmony.treatment.models import Illness, IllnessTreatment
from healthharmony.patient.forms import UpdateProfileInfo

from healthharmony.patient.functions import (
    update_patient_view_context,
    get_weather,
    fetch_overview_data,
)
from healthharmony.base.functions import check_models


# Create your views here.
def overview_view(request):
    check_models()
    access_checker(request)

    # set session data
    if "email" not in request.session:
        request.session["email"] = request.user.email

    env = environ.Env()
    environ.Env.read_env(env_file="healthharmony/.env")

    context = {}

    # Start the weather thread
    weather_thread = threading.Thread(target=get_weather, args=(context, env))
    weather_thread.start()

    # Start the data fetching thread
    data_thread = threading.Thread(target=fetch_overview_data, args=(context, request))
    data_thread.start()

    # Wait for both threads to complete
    weather_thread.join()
    data_thread.join()

    # Check for any errors and add messages if necessary
    if "weather_error" in context:
        messages.error(request, context["weather_error"])
    if "data_error" in context:
        messages.error(request, context["data_error"])

    return render(request, "patient/overview.html", context)


def records_view(request):
    access_checker(request)
    if "email" not in request.session:
        request.session["email"] = request.user.email
    context = {}
    try:
        treatments = Illness.objects.filter(patient=request.user).prefetch_related(
            Prefetch(
                "illnesstreatment_set",
                queryset=IllnessTreatment.objects.select_related("inventory_detail"),
            )
        )

        for illness in treatments:
            for treatment in illness.illnesstreatment_set.all():
                treatment.quantity = treatment.quantity or 0

        context.update(
            {
                "treatments": treatments,
            }
        )

    except Exception as e:
        messages.error(request, f"Failed to fetch data, please reload page : {e}")

    return render(request, "patient/records.html", context)


def patient_view(request, pk):
    access_checker(request)
    if request.user.access < 2:
        return redirect("home")
    if "email" not in request.session:
        request.session["email"] = request.user.email
    context = {}

    if request.method == "POST":
        if request.user.id != int(pk):
            return redirect("patient-profile", pk)
        form = UpdateProfileInfo(request.POST, files=request.FILES)
        if form.is_valid():
            try:
                user = form.save(request)
                messages.success(request, "Profile updated successfully!")
                context.update({"user": user})
                return redirect("patient-profile", request.user.id)
            except ValueError as e:
                messages.error(request, str(e))

    update_patient_view_context(request, context, pk)

    return render(request, "patient/patient.html", context)


def access_checker(request):
    if request.user.access < 1:
        return redirect("home")
