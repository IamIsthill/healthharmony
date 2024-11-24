from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch, Q
import logging
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth import logout
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from concurrent.futures import as_completed, ThreadPoolExecutor


from healthharmony.models.treatment.models import (
    Illness,
    Category,
    DoctorDetail,
    IllnessNote,
)
from healthharmony.models.inventory.models import InventoryDetail
from healthharmony.users.models import User, Department
from healthharmony.doctor.forms import (
    UpdateIllness,
    UpdateTreatmentForIllness,
    UpdateDoctorSched,
    UpdateDoctorAvail,
    UpdateUserDetails,
    UpdateUserVital,
    CreateNotesToCase,
)
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
    UserSerializer,
    DepartmentSerializer,
    IllnessNoteSerializer,
)

from healthharmony.base.functions import check_models, train_diagnosis_predictor


logger = logging.getLogger(__name__)


# Create your views here.
@never_cache
@login_required(login_url="account_login")
def view_patient_profile(request, pk):
    if request.user.access < 2:
        return redirect(request.META.get("HTTP_REFERER", "patient-overview"))
    context = {"page": "Patient Profile"}
    update_patient_view_context(request, context, pk)

    try:
        user_cache = cache.get("user_cache", {})
        user = user_cache.get(pk)
        if not user:
            user = User.objects.get(id=int(pk))
            user_cache[pk] = user
            cache.set("user_cache", user_cache, timeout=(60 * 120))

        patient = UserSerializer(user).data

        treatments = user_cache.get(f"{pk}_treatments", [])
        illnesses = user_cache.get(f"{pk}_illnesses", [])
        if not illnesses:
            illness_query = Illness.objects.filter(patient=user)
            for illness in illness_query:
                illnesses.append(IllnessSerializer(illness).data)
                for treatment in illness.illnesstreatment_set.all():
                    treatments.append(IllnessTreatmentSerializer(treatment).data)
            if treatments:
                for treatment in treatments:
                    treatment["quantity"] = treatment["quantity"] * -1
            user_cache[f"{pk}_treatments"] = treatments
            user_cache[f"{pk}_illnesses"] = illnesses

            cache.set("user_cache", user_cache, timeout=(60 * 120))

        context.update(
            {"illnesses": illnesses, "treatments": treatments, "patient": patient}
        )
    except Exception as e:
        logger.error(f"Failed to fetched user data[id: {pk}]: {str(e)}")
        messages.error(
            request, "Failed to fetch the required data. Please reload the page"
        )

    get_department_data(request, context)
    get_related_illness_notes(request, context, user)

    return render(request, "doctor/patient.html", context)


@login_required(login_url="account_login")
def post_update_patient_illness(request, pk):
    if request.user.access < 3:
        messages.error(
            request,
            "Only doctors are allowed to add further information about this case.",
        )
        return redirect("doctor-view-patient", pk)

    if request.method == "POST":
        illness_form = UpdateIllness(request.POST)
        prescription_form = UpdateTreatmentForIllness(request.POST)

        if illness_form.is_valid():
            illness_form.save(request)

        else:
            messages.error(request, "Failed to update patient's case.")
            logger.warning("Illness form is invalid")

        if illness_form.is_valid() and prescription_form.is_valid():
            prescription_form.save(request)

        else:
            messages.error(request, "Failed to update patient's case.")
            logger.warning("Prescription form is invalid")

        cache.clear()

        return redirect("doctor-view-patient", pk)


@login_required(login_url="account_login")
def post_create_illness_note(request, pk):
    if request.user.access < 3:
        return redirect("staff-overview")

    form = CreateNotesToCase(request.POST)

    if form.is_valid():
        form.save(request)
        cache.delete("note_cache")
    else:
        messages.error(request, "The request is invalid")
        logger.warning("The request is invalid")

    return redirect("doctor-view-patient", pk)


@login_required(login_url="account_login")
def overview_view(request):
    # Check the access level of the user, return to home if not sufficient
    if request.user.access < 3:
        return redirect("staff-overview")
    train_diagnosis_predictor()

    illness_cache = cache.get("illness_cache", {})
    illness_cases = illness_cache.get("query")

    if not illness_cases:
        illness_cases = Illness.objects.all()
        illness_cache["query"] = illness_cases
        cache.set("illness_cache", illness_cache, timeout=(60 * 120))

    illness_paginator = Paginator(illness_cases, 20)
    page = request.GET.get("page")

    try:
        illness_page = illness_paginator.page(page)
    except PageNotAnInteger:
        illness_page = illness_paginator.page(1)
    except EmptyPage:
        illness_page = illness_paginator.page(illness_paginator.num_pages)

    # with ThreadPoolExecutor() as tp:
    #     futures = {
    #         tp.submit(
    #             get_sorted_illness_categories, illness_cases
    #         ): "illness_categories",
    #         tp.submit(get_departments, request): "department_names",
    #         tp.submit(get_sorted_department, request): "department_data",
    #         tp.submit(get_sorted_category, request): "sorted_illness_category",
    #         tp.submit(fetch_categories): "categories",
    #     }

    #     results = {}
    #     for future in as_completed(futures):
    #         key = futures[future]
    #         try:
    #             results[key] = future.result()
    #         except Exception as exc:
    #             logger.error(f"{key} generated an exception: {exc}")
    #             results[key] = 0

    illness_data = illness_cache.get("illness_data", [])
    if not illness_data:
        for case in illness_cases:
            data = IllnessSerializer(case).data
            illness_data.append(data)
        illness_cache["illness_data"] = illness_data
        cache.set("illness_cache", illness_cache, timeout=(120 * 60))

    # illness_categories = results["illness_categories"]
    # request, department_names = results["department_names"]
    # request, department_data = results["department_data"]
    # request, sorted_illness_category = results["sorted_illness_category"]
    # categories = results["categories"]
    illness_categories = get_sorted_illness_categories(request)
    request, department_names = get_departments(request)
    request, department_data = get_sorted_department(request)
    request, sorted_illness_category = get_sorted_category(request)
    categories = fetch_categories()

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
        "page": "Overview",
    }

    return render(request, "doctor/overview.html", context)


@login_required(login_url="account_login")
def handled_cases(request):
    if request.user.access < 3:
        return redirect("staff-overview")

    if request.method.lower() == "get":
        try:
            search = request.GET.get("search")
            illness_cases = get_illness_case(search, request)
        except Exception as e:
            logger.info(f"Failed to fetch the illness cases: {str(e)}")
            messages.error(request, "Failed to fetch required data. Please reload page")
            return redirect(request.META.get("HTTP_REFERER", "doctor-overview"))

    else:
        try:
            illness_cache = cache.get("illness_cache", {})
            illness_cases = illness_cache.get(f"{request.user.email}")
            if not illness_cases:
                illness_cases = Illness.objects.filter(
                    Q(doctor=request.user) | Q(staff=request.user)
                )
                illness_cache[f"{request.user.email}"] = illness_cases
                cache.set("illness_cache", illness_cache, timeout=(120 * 60))
        except Exception as e:
            logger.info(f"Failed to fetch the illness cases: {str(e)}")
            messages.error(request, "Failed to fetch required data. Please reload page")
            return redirect(request.META.get("HTTP_REFERER", "doctor-overview"))

    try:
        illness_cache = cache.get("illness_cache", {})
        unfiltered_illness_case = illness_cache.get(f"{request.user.email}")
        if not unfiltered_illness_case:
            unfiltered_illness_case = Illness.objects.filter(
                Q(doctor=request.user) | Q(staff=request.user)
            )
            illness_cache[f"{request.user.email}"] = unfiltered_illness_case
            cache.set("illness_cache", illness_cache, timeout=(120 * 60))

    except Exception as e:
        logger.info(f"Failed to fetch the unfiltered illness cases: {str(e)}")
        messages.error(request, "Failed to fetch required data. Please reload page")
        return redirect(request.META.get("HTTP_REFERER", "doctor-overview"))

    department_data = illness_cache.get(f"{request.user.email}_department_data")
    if not department_data:
        department_data = get_doctors_cases_per_department(unfiltered_illness_case)
        illness_cache[f"{request.user.email}_department_data"] = department_data
        cache.set("illness_cache", illness_cache, timeout=(120 * 60))

    illness_category_data = illness_cache.get(
        f"{request.user.email}_illness_category_data"
    )
    if not illness_category_data:
        illness_category_data = get_doctors_cases_per_category(unfiltered_illness_case)
        illness_cache[
            f"{request.user.email}_illness_category_data"
        ] = illness_category_data
        cache.set("illness_cache", illness_cache, timeout=(120 * 60))

    illness_page = get_illness_page(request, illness_cases)

    context = {
        "illness_page": illness_page,
        "department_data": department_data,
        "illness_category_data": illness_category_data,
        "page": "Handled Cases",
    }

    return render(request, "doctor/handled.html", context)


@login_required(login_url="account_login")
def schedule(request):
    if request.user.access < 3:
        return redirect("staff-overview")
    context = {"page": "Schedule"}

    try:
        doctor_cache = cache.get("doctor_cache", {})
        doctor_sched = doctor_cache.get(f"{request.user.email}")
        if not doctor_sched:
            doctor_sched = DoctorDetail.objects.filter(doctor=request.user).values()
            doctor_cache[f"{request.user.email}"] = doctor_sched
            cache.set("doctor_cache", doctor_cache, timeout=(120 * 60))
        context.update({"doctor_sched": doctor_sched[0]})
    except Exception as e:
        logger.info(f"{request.user.email} has no schedule: {str(e)}")

    return render(request, "doctor/sched.html", context)


@login_required(login_url="account_login")
def post_update_doctor_time(request):
    if request.method == "POST":
        form = UpdateDoctorSched(request.POST)

        if form.is_valid():
            form.save(request)
            cache.delete("doctor_cache")
    return redirect("doctor-schedule")


@login_required(login_url="account_login")
def post_update_doctor_avail(request):
    if request.method == "POST":
        form = UpdateDoctorAvail(request.POST)

        if form.is_valid():
            form.save(request)
            cache.delete("doctor_cache")
        else:
            logger.info("Form is invalid")
            messages.error(request, "Form is invalid. Please try again.")
    return redirect("doctor-schedule")


@login_required(login_url="account_login")
def post_update_user_details(request):
    patient_id = request.POST.get("patient_id")

    if request.method == "POST":
        form = UpdateUserDetails(request.POST)
        if form.is_valid():
            form.save(request)
            cache.clear()

        else:
            logger.info("Form is invalid")
            messages.error(request, "Form is invalid. Please try again.")
    return redirect("doctor-view-patient", patient_id)


@login_required(login_url="account_login")
def post_update_user_vitals(request):
    patient_id = request.POST.get("patient_id")

    if request.method == "POST":
        form = UpdateUserVital(request.POST)
        if form.is_valid():
            form.save(request)
            cache.clear()
        else:
            logger.info("Form is invalid")
            messages.error(request, "Form is invalid. Please try again.")
        
    return redirect("doctor-view-patient", patient_id)


@api_view(["GET"])
def get_predicted_diagnosis(request):
    issue = request.query_params.get("issue")

    diagnosis = predict_diagnosis(issue)
    print(diagnosis)
    return JsonResponse(diagnosis, safe=False)


@api_view(["GET"])
def get_illness_categories(request):
    category_cache = cache.get("category_cache", {})
    categories = category_cache.get("query")
    if not categories:
        categories = Category.objects.all()
        category_cache["query"] = categories
        cache.set("category_cache", category_cache, timeout=(120 * 60))
    data = category_cache.get("IllnessCategorySerializer", [])
    if not data:
        for category in categories:
            data.append(IllnessCategorySerializer(category).data)
        category_cache["IllnessCategorySerializer"] = data
        cache.set("category_cache", category_cache, timeout=(120 * 60))
    return JsonResponse(data, safe=False)


@api_view(["GET"])
def get_inventory_list(request):
    inventory_cache = cache.get("inventory_cache", {})
    inventories = inventory_cache.get("query")
    if not inventories:
        inventories = InventoryDetail.objects.all()
        inventory_cache["query"] = inventories
        cache.set("inventory_cache", inventory_cache, timeout=(120 * 60))
    data = inventory_cache.get("InventorySerializer", [])
    if not data:
        for inventory in inventories:
            data.append(InventorySerializer(inventory).data)
        inventory_cache["InventorySerializer"] = data
        cache.set("inventory_cache", inventory_cache, timeout=(120 * 60))

    return JsonResponse(data, safe=False)


def access_checker(request):
    if request.user.access < 3:
        return redirect("home")


def get_sorted_illness_categories(illness_cases):
    now = timezone.now()
    illness_cache = cache.get("illness_cache", {})
    illness_categories = illness_cache.get("doctor_overview_sorted_illness", [])

    if not illness_categories:

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
        illness_cache["doctor_overview_sorted_illness"] = illness_categories
        cache.set("illness_cache", illness_cache, timeout=(120 * 60))

    return illness_categories


def get_doctors_cases_per_department(illness_cases):
    department_data = []
    for case in illness_cases:
        # Check if there is a department associated with the user
        if case.patient.department:
            department_found = False
            # Check if there is an existing department in department data
            for department in department_data:
                # If found, add another cases count then break
                if (
                    department["department_name"]
                    and department["department_id"] == case.patient.department.id
                ):
                    department["cases_count"] += 1
                    department_found = True
                    break

            if not department_found:
                department_data.append(
                    {
                        "department_id": case.patient.department.id,
                        "department_name": case.patient.department.department,
                        "cases_count": 1,
                    }
                )

        # If patient has no department
        else:
            department_found = False
            for department in department_data:
                # Check if 'Others' was already in depaertment data, then add cases
                if (
                    department["department_name"]
                    and department["department_name"] == "Others"
                ):
                    department["cases_count"] += 1
                    department_found = True
                    break

                # if not, then create the 'others category
            if not department_found:
                department_data.append(
                    {"department_id": 0, "department_name": "Others", "cases_count": 1}
                )

    return department_data


def get_doctors_cases_per_category(illness_cases):
    illness_category_data = []
    for case in illness_cases:
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
                if category["category_name"] and category["category_name"] == "Others":
                    category["cases_count"] += 1
                    category_found = True
                    break

                # if not, then create the 'others category
            if not category_found:
                illness_category_data.append(
                    {"category_id": 0, "category_name": "Others", "cases_count": 1}
                )
    return illness_category_data


# Changed params based on the 'search'
def get_illness_case(search, request):
    if search:
        illness_cases = Illness.objects.filter(
            (Q(doctor=request.user) | Q(staff=request.user))
            & (  # Filter by doctor or staff
                Q(patient__first_name__icontains=search)
                | Q(  # Case-insensitive search on first name
                    patient__last_name__icontains=search
                )
                | Q(issue__icontains=search)
                | Q(diagnosis__icontains=search)
            )
        )

        # If search query is empty, show all illness cases for the user
    else:
        illness_cache = cache.get("illness_cache", {})

        illness_cases = illness_cache.get(f"{request.user.email}")

        if not illness_cases:
            illness_cases = Illness.objects.filter(
                Q(doctor=request.user) | Q(staff=request.user)
            )
            illness_cache[f"{request.user.email}"] = illness_cases
            cache.set("illness_cache", illness_cache, timeout=(60 * 120))

    return illness_cases


# Refactored for the handled case
def get_illness_page(request, illness_cases):
    illness_paginator = Paginator(illness_cases, 20)
    page = request.GET.get("page")
    try:
        illness_page = illness_paginator.page(page)
    except PageNotAnInteger:
        illness_page = illness_paginator.page(1)
    except EmptyPage:
        illness_page = illness_paginator.page(illness_paginator.num_pages)

    return illness_page


def get_department_data(request, context):
    try:
        department_cache = cache.get("department_cache", {})
        departments = department_cache.get("query")
        if not departments:
            departments = Department.objects.all()
            department_cache["query"] = departments
            cache.set("department_cache", department_cache, timeout=(120 * 60))

        department_data = department_cache.get("department_data", [])
        if not department_data:
            for department in departments:
                data = DepartmentSerializer(department)
                department_data.append(data.data)
            department_cache["department_data"] = department_data
            cache.set("department_cache", department_cache, timeout=(120 * 60))

        context.update({"department_data": department_data})

    except Exception as e:
        logger.info(f"{request.user.email} failed to fetch department data: {str(e)}")
        messages.error(
            request, "Failed to fetch the required data. Please reload the page"
        )


def get_related_illness_notes(request, context, user):
    try:
        note_cache = cache.get("note_cache", {})
        illness_notes_data = note_cache.get(user.id, [])
        if not illness_notes_data:
            illness_notes = IllnessNote.objects.filter(patient=user)

            if illness_notes:
                for notes in illness_notes:
                    data = IllnessNoteSerializer(notes)
                    illness_notes_data.append(data.data)
            note_cache[user.id] = illness_notes_data
            cache.set("note_cache", note_cache, timeout=(120 * 60))

        context.update({"illness_notes_data": illness_notes_data})

    except Exception as e:
        logger.info(f"{request.user.email} failed to fetch notes data: {str(e)}")
        messages.error(
            request, "Failed to fetch the required data. Please reload the page"
        )
