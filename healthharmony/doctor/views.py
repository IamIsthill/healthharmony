from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch, Q
import logging
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from healthharmony.models.treatment.models import Illness, Category
from healthharmony.models.inventory.models import InventoryDetail
from healthharmony.users.models import User
from healthharmony.doctor.forms import UpdateIllness, UpdateTreatmentForIllness
from healthharmony.patient.functions import update_patient_view_context

from healthharmony.doctor.functions import predict_diagnosis
from healthharmony.doctor.serializer import (
    IllnessSerializer,
    IllnessTreatmentSerializer,
    IllnessCategorySerializer,
    InventorySerializer,
)

from healthharmony.base.functions import check_models


logger = logging.getLogger(__name__)


# Create your views here.
@never_cache
@login_required(login_url="account_login")
def view_patient_profile(request, pk):
    if request.user.access < 2:
        return redirect(request.META.get("HTTP_REFERER", "doctor-overview"))
    context = {}
    update_patient_view_context(request, context, pk)

    try:
        user = User.objects.get(id=int(pk))
        illnesses = []
        treatments = []
        illness_query = Illness.objects.filter(patient=user)
        for illness in illness_query:
            illnesses.append(IllnessSerializer(illness).data)
            for treatment in illness.illnesstreatment_set.all():
                treatments.append(IllnessTreatmentSerializer(treatment).data)
        context.update({"illnesses": illnesses, "treatments": treatments})
    except Exception as e:
        logger.error(f"Failed to fetched user data[id: {pk}]: {str(e)}")
        messages.error(
            request, "Failed to fetch the required data. Please reload the page"
        )

    if request.method == "POST":
        illness_form = UpdateIllness(request.POST)
        prescription_form = UpdateTreatmentForIllness(request.POST)
        if illness_form.is_valid() and prescription_form.is_valid():
            illness_form.save(request)
            prescription_form.save(request)
        else:
            messages.error(request, "Failed to update patient's case.")

    return render(request, "doctor/patient.html", context)


@login_required(login_url="account_login")
def overview_view(request):
    #     """
    #     View to display and update illness information.

    #     This view handles both GET and POST requests. On GET requests, it fetches and organizes
    #     illness data into categories based on their diagnosis status and prepares it for rendering.
    #     On POST requests, it processes form data to update illness information.

    #     Args:
    #         request: The HTTP request object.

    #     Returns:
    #         HttpResponse: The rendered HTML page with illness information.
    #     """
    #     check_models()
    #     access_checker(request)
    context = {}

    #     # Handle POST request for updating illness
    #     if request.method == "POST":
    #         form = UpdateIllness(request.POST)
    #         if form.is_valid():
    #             try:
    #                 form.save(request)
    #                 messages.success(request, "Illness updated successfully!")
    #             except Exception as e:
    #                 logger.error("Error updating illness: %s", str(e))
    #                 messages.error(request, "An error occurred while updating the illness.")
    #         else:
    #             messages.error(request, "Form data is invalid.")

    #     # Handle GET request to fetch and prepare illness data
    #     try:
    #         all_illness = Illness.objects.all().prefetch_related(
    #             Prefetch(
    #                 "illnesstreatment_set",
    #                 queryset=IllnessTreatment.objects.select_related("inventory_detail"),
    #             )
    #         )
    #         done_illness = Illness.objects.filter(diagnosis__isnull=False).prefetch_related(
    #             Prefetch(
    #                 "illnesstreatment_set",
    #                 queryset=IllnessTreatment.objects.select_related("inventory_detail"),
    #             )
    #         )
    #         not_illness = Illness.objects.filter(
    #             Q(diagnosis__isnull=True) | Q(diagnosis="")
    #         ).prefetch_related(
    #             Prefetch(
    #                 "illnesstreatment_set",
    #                 queryset=IllnessTreatment.objects.select_related("inventory_detail"),
    #             )
    #         )

    #         illness_data = {
    #             "all": [illness_to_dict(illness) for illness in all_illness],
    #             "not": [illness_to_dict(illness) for illness in not_illness],
    #             "done": [illness_to_dict(illness) for illness in done_illness],
    #         }

    #         context = {
    #             "not_illness": not_illness,
    #             "illness_data": illness_data,
    #         }
    #     except Exception as e:
    #         logger.error("Error retrieving illness data: %s", str(e))
    #         context = {
    #             "not_illness": [],
    #             "illness_data": {
    #                 "all": [],
    #                 "not": [],
    #                 "done": [],
    #             },
    #         }
    #         messages.error(request, "An error occurred while retrieving illness data.")

    return render(request, "doctor/overview.html", context)


@api_view(["GET"])
def get_predicted_diagnosis(request):
    issue = request.query_params.get("issue")

    diagnosis = predict_diagnosis(issue)
    return JsonResponse(diagnosis, safe=False)


@api_view(["GET"])
def get_illness_categories(request):
    categories = Category.objects.all()
    data = []
    for category in categories:
        data.append(IllnessCategorySerializer(category).data)
    return JsonResponse(data, safe=False)


@api_view(["GET"])
def get_inventory_list(request):
    inventories = InventoryDetail.objects.all()
    data = []
    for inventory in inventories:
        data.append(InventorySerializer(inventory).data)
    return JsonResponse(data, safe=False)


# @api_view(["POST"])
# def update_illness(request):
#     access_checker(request)
#     form = UpdateIllness(request.POST)
#     if form.is_valid():
#         form.save(request)
#         return response(status=status.HTTP_200_OK)
#     else:
#         return response(form.errors, status=status.HTTP_400_BAD_REQUEST)


def access_checker(request):
    if request.user.access < 3:
        return redirect("home")
