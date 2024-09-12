from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch, Q
import logging
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from concurrent.futures import as_completed, ThreadPoolExecutor


from healthharmony.models.treatment.models import Illness, Category
from healthharmony.models.inventory.models import InventoryDetail
from healthharmony.users.models import User
from healthharmony.doctor.forms import UpdateIllness, UpdateTreatmentForIllness
from healthharmony.patient.functions import update_patient_view_context

from healthharmony.staff.functions import (
    get_departments,
    get_sorted_department,
    get_sorted_category,
    fetch_categories,
)

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
    # Check the access level of the user, return to home if not sufficient
    access_checker(request)

    illness_cases = Illness.objects.all()
    illness_data = []

    illness_paginator = Paginator(illness_cases, 20)
    page = request.GET.get("page")

    try:
        illness_page = illness_paginator.page(page)
    except PageNotAnInteger:
        illness_page = illness_paginator.page(1)
    except EmptyPage:
        illness_page = illness_paginator.page(illness_paginator.num_pages)

    with ThreadPoolExecutor() as tp:
        futures = {
            tp.submit(
                get_sorted_illness_categories, illness_cases
            ): "illness_categories",
            tp.submit(get_departments, request): "department_names",
            tp.submit(get_sorted_department, request): "department_data",
            tp.submit(get_sorted_category, request): "sorted_illness_category",
            tp.submit(fetch_categories): "categories",
        }

        results = {}
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as exc:
                logger.error(f"{key} generated an exception: {exc}")
                results[key] = 0

    for case in illness_cases:
        data = IllnessSerializer(case).data
        illness_data.append(data)

    # illness_categories = get_sorted_illness_categories(illness_cases)
    # request, department_names = get_departments(request)
    # request, department_data = get_sorted_department(request)
    # request, sorted_illness_category = get_sorted_category(request)
    # categories = fetch_categories()
    illness_categories = results["illness_categories"]
    request, department_names = results["department_names"]
    request, department_data = results["department_data"]
    request, sorted_illness_category = results["sorted_illness_category"]
    categories = results["categories"]

    department_names = [
        {"id": department.id, "department": department.department}
        for department in department_names
    ]

    context = {
        "illness_data": illness_data,
        "illness_page": illness_page,
        "illness_categories": illness_categories,
        "department_names": department_names,
        "department_data": department_data,
        "sorted_illness_category": sorted_illness_category,
        "categories": categories,
    }

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


def access_checker(request):
    if request.user.access < 3:
        return redirect("home")


def get_sorted_illness_categories(illness_cases):
    now = timezone.now()
    illness_categories = []
    for case in illness_cases:
        if case.added.month == now.month:
            if case.illness_category and case.illness_category.category:
                category_found = False
                for category in illness_categories:
                    if category["category"] == case.illness_category.category:
                        category["count"] += 1  # Increment the count
                        category_found = True
                        break

                # If the category doesn't exist, add it to the list
                if not category_found:
                    illness_categories.append(
                        {"category": case.illness_category.category, "count": 1}
                    )

    return illness_categories
