from django.shortcuts import render
from django.db.models import Prefetch
import logging

from healthharmony.treatment.models import Illness, IllnessTreatment

# from healthharmony.doctor.functions import train_diagnosis_predictor


logger = logging.getLogger(__name__)


# Create your views here.
def overview_view(request):
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
    not_illness = Illness.objects.filter(diagnosis__isnull=True).prefetch_related(
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
