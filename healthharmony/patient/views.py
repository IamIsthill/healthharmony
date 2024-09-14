from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch
import threading
import logging
from django.http import HttpResponseRedirect


from healthharmony.models.treatment.models import Illness, IllnessTreatment
from healthharmony.users.models import User
from healthharmony.patient.forms import UpdateProfileInfo

from healthharmony.patient.functions import (
    update_patient_view_context,
    get_weather,
    fetch_overview_data,
)
from healthharmony.base.functions import check_models
from healthharmony.app.settings import env


logger = logging.getLogger(__name__)


# Create your views here.
def overview_view(request):
    check_models()
    access_checker(request)

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


def records_view(request, pk):
    access_checker(request)
    user = get_user(request, pk)
    if isinstance(user, HttpResponseRedirect):
        return user
    if "email" not in request.session:
        request.session["email"] = request.user.email
    context = {}
    try:
        treatments = Illness.objects.filter(patient=user).prefetch_related(
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
        logger.error(f"Failure in fetching required data: {e}")
        messages.error(request, "Failed to fetch data, please reload page")

    return render(request, "patient/records.html", context)


def patient_view(request, pk):
    access_checker(request)
    if (request.user.access < 1) or (request.user.id == int(pk)):
        return redirect(request.META.get("HTTP_REFERER", "home"))
    if "email" not in request.session:
        request.session["email"] = request.user.email
    context = {}

    if request.method.lower == "post":
        form = UpdateProfileInfo(request.POST, files=request.FILES)
        if form.is_valid():
            try:
                user = form.save(request, pk)
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


def get_user(request, pk):
    if request.user.access > 1 or request.user.id == int(pk):
        try:
            user = User.objects.get(id=int(pk))
        except User.DoesNotExist:
            logger.info("Failed to fetch user: User does not exist")
            messages.error(request, "User does not exist")
            return redirect(request.META.get("HTTP_REFERER", "home"))
        except Exception as e:
            logger.info(f"Failed to fetch user: {e}")
            messages.error(request, "An error occurred while fetching the user")
            return redirect(request.META.get("HTTP_REFERER", "home"))
        return user
    else:
        return redirect(request.META.get("HTTP_REFERER", "home"))
