from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch, Q
import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse

from healthharmony.treatment.models import Illness, IllnessTreatment
from healthharmony.doctor.forms import UpdateIllness

from healthharmony.doctor.functions import predict_diagnosis
from healthharmony.base.functions import check_models

logger = logging.getLogger(__name__)


# Create your views here.
def overview_view(request):
    check_models()
    access_checker(request)
    if "email" not in request.session:
        request.session["email"] = request.user.email
    if request.method == "POST":
        form = UpdateIllness(request.POST)
        if form.is_valid():
            try:
                form.save(request)
                messages.success(request, "Illness updated successfully!")
            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Form data is invalid.")

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
    return render(request, "doctor/overview.html", context)


def illness_to_dict(illness):
    return {
        "id": illness.id,
        "patient": illness.patient.first_name + " " + illness.patient.last_name,
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
    }


@api_view(["GET"])
def get_predicted_diagnosis(request):
    issue = request.query_params.get("issue", "")

    diagnosis = predict_diagnosis(issue)
    return JsonResponse(diagnosis, safe=False)


def access_checker(request):
    if request.user.access < 3:
        return redirect("home")
