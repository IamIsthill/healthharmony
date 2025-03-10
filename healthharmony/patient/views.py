from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch
import logging
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from concurrent.futures import as_completed, ThreadPoolExecutor

from healthharmony.models.treatment.models import Illness, Certificate, IllnessNote
from healthharmony.doctor.serializer import IllnessNoteSerializer
from healthharmony.users.models import User
from healthharmony.patient.forms import UpdateProfileInfo, CreateCertificateForm
from healthharmony.patient.serializers import CertificateSerializer
from healthharmony.doctor.serializer import UserSerializer
from healthharmony.doctor.serializer import (
    IllnessSerializer,
    IllnessTreatmentSerializer,
)

from healthharmony.patient.functions import (
    update_patient_view_context,
    get_weather,
    fetch_overview_data,
)
from healthharmony.base.functions import check_models, train_diagnosis_predictor
from healthharmony.app.settings import env


logger = logging.getLogger(__name__)


# Create your views here.
@login_required(login_url="account_login")
def overview_view(request):
    if request.user.access < 1:
        return redirect("home")
    train_diagnosis_predictor()
    context = {"page": "dashboard"}
    try:
        # with ThreadPoolExecutor() as tp:
        # tp.submit(check_models)
        # tp.submit(get_weather, context, env)
        # tp.submit(fetch_overview_data, context, request)
        # tp.submit(fetch_medcert_data, request, context, request.user)
        get_weather(context, env)
        fetch_overview_data(context, request)
        fetch_medcert_data(request, context, request.user)
    except Exception as e:
        logger.warning(f"Something went wrong in patient/records: {(e)}")
        messages.error(request, "Please reload page.")

    # Check for any errors and add messages if necessary
    if "weather_error" in context:
        messages.error(request, "Please reload page.")
    if "data_error" in context:
        messages.error(request, "Please reload page.")
    context.update({"page": "dashboard"})

    return render(request, "patient/overview.html", context)


@login_required(login_url="account_login")
def records_view(request, pk):
    if request.user.access < 1:
        return redirect("home")
    if request.user.id != int(pk):
        return redirect("patient-records", request.user.id)

    context = {"page": "Health Records"}
    try:
        user_cache = cache.get("user_cache", {})
        user = user_cache.get(int(pk))
        if not user:
            user = User.objects.get(id=int(pk))
            user_cache[int(pk)] = user
            cache.set("user_cache", user_cache, timeout=(60 * 60 * 2))
    except Exception as e:
        logger.info(
            f"{request.user.email} tried to fetch a user with invalid id[{pk}] : {str(e)}"
        )
        messages.error(request, "Cannot find a user with that id. Please try again.")
        return redirect(request.META.get("HTTP_REFERER", "patient-overview"))

    try:
        illnesses = []
        treatments = []
        illness_cache = cache.get("illness_cache", {})
        illness_query = illness_cache.get(f"patient_page_{user.id}_illness")
        if not illness_query:
            illness_query = Illness.objects.filter(patient=user)
            illness_cache[f"patient_page_{user.id}_illness"] = illness_query
            cache.set("illness_cache", illness_cache, timeout=(120 * 60))

        # with ThreadPoolExecutor() as tp:
        #     tp.submit(get_illness_categories, illness_query, context)
        #     tp.submit(fetch_medcert_data, request, context, user)
        #     tp.submit(fetch_user_certificates, user, context)
        #     tp.submit(get_illness_notes, request, context, user)

        get_illness_categories(illness_query, context, user)
        fetch_medcert_data(request, context, user)
        fetch_user_certificates(user, context)
        get_illness_notes(request, context, user)
        for illness in illness_query:
            illnesses.append(IllnessSerializer(illness).data)
            for treatment in illness.illnesstreatment_set.all():
                treatments.append(IllnessTreatmentSerializer(treatment).data)
        context.update(
            {
                "illnesses": illnesses,
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
            cache.clear()
        else:
            messages.error(request, "Form is invalid. Please try again")
    return redirect("patient-records", request.user.id)


@login_required(login_url="account_login")
def patient_view(request, pk):
    if request.user.access < 1:
        return redirect("home")
    if request.user.id != int(pk):
        return redirect("patient-profile", request.user.id)
    context = {"page": "Patient Profile"}

    if request.method == "POST":
        form = UpdateProfileInfo(request.POST, files=request.FILES)
        if form.is_valid():
            try:
                user = form.save(request, pk)
                messages.success(request, "Profile updated successfully!")
                context.update({"user": user})
                cache.clear()
                return redirect("patient-profile", request.user.id)
            except ValueError as e:
                messages.error(request, str(e))

    update_patient_view_context(request, context, pk)

    try:
        user_cache = cache.get("user_cache", {})
        user = user_cache.get(pk)
        if not user:
            user = User.objects.get(id=int(pk))
            user_cache[pk] = user
            cache.set("user_cache", user_cache, timeout=(120 * 60))
        user = UserSerializer(user).data
        context.update({"user_data": user})
    except Exception as e:
        logger.info(f"Problem serializing user information: {str(e)}")
        messages.error(request, "Failed to fetch necessary data. Please try again")

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


def fetch_medcert_data(request, context, user):

    try:
        certificate_cache = cache.get("certificate_cache", {})
        certificates_data = certificate_cache.get(
            f"patient_page_{user.id}_certificate_data", {}
        )
        if not certificates_data:
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
            certificate_cache[
                f"patient_page_{user.id}_certificate_data"
            ] = certificates_data
            cache.set("certificate_cache", certificate_cache, timeout=(60 * 60 * 2))

        context.update({"certificates_data": certificates_data})

    except Exception as e:
        logger.info(
            f"No certificate request was fetched with id[{request.user.id}]: {str(e)}"
        )


def get_illness_categories(illnesses_query, context, user):
    illness_cache = cache.get("illness_cache", {})
    illness_category_data = illness_cache.get(
        f"patient_page_{user.id}_illness_category_data", []
    )
    if not illness_category_data:
        for case in illnesses_query:
            # Check if there is an illness_Category on the case
            if case.illness_category:
                category_found = False
                # Check if there is an existing department in department data
                for category in illness_category_data:
                    # If found, add another cases count then break
                    if (
                        category["category_name"]
                        and category["category_id"] == case.illness_category.id
                    ):
                        category["cases_count"] += 1
                        category_found = True
                        break

                if not category_found:
                    illness_category_data.append(
                        {
                            "category_id": case.illness_category.id,
                            "category_name": case.illness_category.category,
                            "cases_count": 1,
                        }
                    )

            # If patient has no department
            else:
                category_found = False
                for category in illness_category_data:
                    # Check if 'Others' was already in illness data, then add cases
                    if (
                        category["category_name"]
                        and category["category_name"] == "Others"
                    ):
                        category["cases_count"] += 1
                        category_found = True
                        break

                    # if not, then create the 'others category
                if not category_found:
                    illness_category_data.append(
                        {"category_id": 0, "category_name": "Others", "cases_count": 1}
                    )
            illness_cache[
                f"patient_page_{user.id}_illness_category_data"
            ] = illness_category_data
            cache.set("illness_cache", illness_cache, timeout=(120 * 60))
    context.update(
        {
            "illness_category": illness_category_data,
        }
    )


def fetch_user_certificates(user, context):
    certificate_cache = cache.get("certificate_cache", {})
    certificates = certificate_cache.get(user.id)
    if not certificates:
        certificates = Certificate.objects.filter(patient=user)
        certificate_cache[user.id] = certificates
        cache.set("certificate_cache", certificate_cache, timeout=(120 * 60))
    certificate_data = certificate_cache.get(f"{user.id}_certificate_data", [])
    if not certificate_data:
        for certificate in certificates:
            data = CertificateSerializer(certificate)
            certificate_data.append(data.data)
        certificate_cache[f"{user.id}_certificate_data"] = certificate_data
        cache.set("certificate_cache", certificate_cache, timeout=(120 * 60))

    context.update({"certificate_data": certificate_data})


def get_illness_notes(request, context, user):
    note_cache = cache.get("note_cache", {})
    notes_data = note_cache.get(user.id, [])
    if not notes_data:
        notes = IllnessNote.objects.filter(patient=user)
        if notes:
            for note in notes:
                data = IllnessNoteSerializer(note)
                notes_data.append(data.data)
        note_cache[user.id] = notes_data
        cache.set("note_cache", note_cache, timeout=(120 * 60))
    context.update({"notes_data": notes_data})
