from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch, Q
import logging
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from healthharmony.treatment.models import Illness, IllnessTreatment
from healthharmony.users.models import User
from healthharmony.doctor.forms import UpdateIllness
from healthharmony.patient.functions import update_patient_view_context

from healthharmony.doctor.functions import predict_diagnosis
from healthharmony.base.functions import check_models


logger = logging.getLogger(__name__)


# Create your views here.
@login_required(login_url="account_login")
def view_patient_profile(request, pk):
    access_checker(request)
    context = {}
    update_patient_view_context(request, context)
    try:
        user = User.objects.get(id=int(pk))
        illness_all = Illness.objects.filter(patient=user).prefetch_related(
            Prefetch(
                "illnesstreatment_set",
                queryset=IllnessTreatment.objects.select_related("inventory_detail"),
            )
        )

        for illness in illness_all:
            for treatment in illness.illnesstreatment_set.all():
                treatment.quantity = treatment.quantity or 0

        done_illness = Illness.objects.filter(
            diagnosis__isnull=False, patient=user
        ).prefetch_related(
            Prefetch(
                "illnesstreatment_set",
                queryset=IllnessTreatment.objects.select_related("inventory_detail"),
            )
        )
        not_illness = Illness.objects.filter(
            Q(patient=user) & Q(diagnosis__isnull=True) | Q(diagnosis="")
        ).prefetch_related(
            Prefetch(
                "illnesstreatment_set",
                queryset=IllnessTreatment.objects.select_related("inventory_detail"),
            )
        )
        illness_data = {
            "all": [illness_to_dict(illness) for illness in illness_all],
            "not": [illness_to_dict(illness) for illness in not_illness],
            "done": [illness_to_dict(illness) for illness in done_illness],
        }

        context.update(
            {
                "user": user,
                "illness_all": illness_all,
                "illness_data": illness_data,
            }
        )

    except Exception as e:
        logger.info(f"Failed to fetch data: {str(e)}")

    return render(request, "doctor/patient.html", context)


@login_required(login_url="account_login")
def overview_view(request):
    """
    View to display and update illness information.

    This view handles both GET and POST requests. On GET requests, it fetches and organizes
    illness data into categories based on their diagnosis status and prepares it for rendering.
    On POST requests, it processes form data to update illness information.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML page with illness information.
    """
    check_models()
    access_checker(request)

    # Ensure user email is in session
    if "email" not in request.session:
        request.session["email"] = request.user.email

    # Handle POST request for updating illness
    if request.method == "POST":
        form = UpdateIllness(request.POST)
        if form.is_valid():
            try:
                form.save(request)
                messages.success(request, "Illness updated successfully!")
            except Exception as e:
                logger.error("Error updating illness: %s", str(e))
                messages.error(request, "An error occurred while updating the illness.")
        else:
            messages.error(request, "Form data is invalid.")

    # Handle GET request to fetch and prepare illness data
    try:
        all_illness = Illness.objects.all().prefetch_related(
            Prefetch(
                "illnesstreatment_set",
                queryset=IllnessTreatment.objects.select_related("inventory_detail"),
            )
        )
        done_illness = Illness.objects.filter(diagnosis__isnull=False).prefetch_related(
            Prefetch(
                "illnesstreatment_set",
                queryset=IllnessTreatment.objects.select_related("inventory_detail"),
            )
        )
        not_illness = Illness.objects.filter(
            Q(diagnosis__isnull=True) | Q(diagnosis="")
        ).prefetch_related(
            Prefetch(
                "illnesstreatment_set",
                queryset=IllnessTreatment.objects.select_related("inventory_detail"),
            )
        )

        illness_data = {
            "all": [illness_to_dict(illness) for illness in all_illness],
            "not": [illness_to_dict(illness) for illness in not_illness],
            "done": [illness_to_dict(illness) for illness in done_illness],
        }

        context = {
            "not_illness": not_illness,
            "illness_data": illness_data,
        }
    except Exception as e:
        logger.error("Error retrieving illness data: %s", str(e))
        context = {
            "not_illness": [],
            "illness_data": {
                "all": [],
                "not": [],
                "done": [],
            },
        }
        messages.error(request, "An error occurred while retrieving illness data.")

    return render(request, "doctor/overview.html", context)


def illness_to_dict(illness):
    return {
        "id": illness.id,
        "patient": illness.patient.first_name + " " + illness.patient.last_name,
        "patient_id": illness.patient.id,
        "issue": illness.issue,
        "diagnosis": illness.diagnosis,
        "category": illness.illness_category.category,
        "staff": illness.staff.id,
        "doctor": illness.doctor.id,
        "added": illness.added,
        "updated": illness.updated,
        "treatments": [
            treatment_to_dict(treatment)
            for treatment in illness.illnesstreatment_set.all()
        ],
    }


def treatment_to_dict(treatment):
    return {
        "treatmentId": treatment.id,
        "medicine": treatment.inventory_detail.item_name,
        "quantity": treatment.quantity or 0,
        "unit": treatment.inventory_detail.unit,
        "category": treatment.inventory_detail.category,
    }


@api_view(["GET"])
def get_predicted_diagnosis(request):
    issue = request.query_params.get("issue", "")

    diagnosis = predict_diagnosis(issue)
    return JsonResponse(diagnosis, safe=False)


def access_checker(request):
    if request.user.access < 3:
        return redirect("home")
