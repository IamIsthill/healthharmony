from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch
import logging
from django.contrib.auth.decorators import login_required
from concurrent.futures import as_completed, ThreadPoolExecutor

from healthharmony.models.treatment.models import Illness, IllnessTreatment, Certificate
from healthharmony.users.models import User
from healthharmony.patient.forms import UpdateProfileInfo, CreateCertificateForm
from healthharmony.patient.serializers import CertificateSerializer

from healthharmony.patient.functions import (
    update_patient_view_context,
    get_weather,
    fetch_overview_data,
)
from healthharmony.base.functions import check_models
from healthharmony.app.settings import env


logger = logging.getLogger(__name__)


# Create your views here.
@login_required(login_url="account_login")
def overview_view(request):
    access_checker(request)
    context = {}
    try:
        with ThreadPoolExecutor() as tp:
            tp.submit(check_models)
            tp.submit(get_weather, context, env)
            tp.submit(fetch_overview_data, context, request)
            tp.submit(fetch_medcert_data, request, context)
    except Exception as e:
        logger.warning(f"Something went wrong in patient/records: {(e)}")
        messages.error(request, "Something went wrong.")

    # Check for any errors and add messages if necessary
    if "weather_error" in context:
        messages.error(request, context["weather_error"])
    if "data_error" in context:
        messages.error(request, context["data_error"])

    return render(request, "patient/overview.html", context)


@login_required(login_url="account_login")
def records_view(request, pk):
    access_checker(request)
    user = request.user
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


@login_required(login_url="account_login")
def post_create_certificate_request(request):
    access_checker(request)
    if request.method == "POST":
        form = CreateCertificateForm(request.POST)
        if form.is_valid():
            form.save(request)
        else:
            messages.error(request, "Form is invalid. Please try again")
    return redirect("patient-records", request.user.id)


@login_required(login_url="account_login")
def patient_view(request, pk):
    access_checker(request)
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


def fetch_medcert_data(request, context):
    user = request.user

    try:
        certificate_requests = Certificate.objects.filter(patient=user)
        certificates_all = certificate_requests.count or 0
        certificates_pending = 0
        certificates_completed = 0

        if certificate_requests:
            for certificate in certificate_requests:
                if certificate.released:
                    certificates_completed += 1
                else:
                    certificates_pending += 1

        certificates_data = {
            "all": certificates_all,
            "pending": certificates_pending,
            "completed": certificates_completed,
        }

        context.update({"certificates_data": certificates_data})

    except Exception as e:
        logger.info(
            f"No certificate request was fetched with id[{request.user.id}]: {str(e)}"
        )
