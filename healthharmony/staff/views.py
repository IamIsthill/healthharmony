from django.shortcuts import render, redirect
import secrets
import string
from django.db import connection, DatabaseError
from django.db.models import (
    OuterRef,
    Subquery,
    Value,
    Sum,
    F,
    CharField,
    Count,
    DateTimeField,
    Q,
)
from django.core.cache import cache
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
import logging
from concurrent.futures import as_completed, ThreadPoolExecutor
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required

from healthharmony.models.bed.models import BedStat, Ambulansya, WheelChair
from healthharmony.users.models import User, Department
from healthharmony.administrator.models import Log, DataChangeLog
from healthharmony.models.treatment.models import (
    Illness,
    IllnessTreatment,
    Certificate,
    Category,
)
from healthharmony.models.inventory.models import InventoryDetail
from healthharmony.base.functions import check_models
from healthharmony.staff.functions import (
    get_sorted_category,
    get_sorted_department,
    get_departments,
    get_sorted_inventory_list,
    get_counted_inventory,
    fetch_today_patient,
    fetch_total_patient,
    fetch_previous_patients,
    fetch_monthly_medcert,
    fetch_previous_medcert,
    fetch_patients,
    fetch_categories,
    fetch_inventory,
    fetch_history,
    fetch_certificate_chart,
    fetch_certificates,
    fetch_employees,
    send_welcome_email,
)
from healthharmony.staff.forms import (
    PatientForm,
    AddInventoryForm,
    EditInventoryForm,
    DeleteInventoryForm,
    DeleteDepartmentForm,
    EditDepartmentForm,
    CreateUpdateAmbulance,
    CreateWheelChairQuantity,
)
from healthharmony.staff.serializer import IllnessSerializer, CategorySerializer
from healthharmony.app.settings import env

logger = logging.getLogger(__name__)


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for i in range(length))


@login_required(login_url="account_login")
def add_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        email = request.POST.get("email")
        user = User.objects.get(email=email)
        if user:
            messages.error(request, "User already exists")
            return redirect("register")
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(generate_password())
            user.backend = (
                "django.contrib.auth.backends.ModelBackend"  # Specify the backend
            )
            user.save()
            # login(request, user)
            return redirect(
                "home"
            )  # Redirect to the home page or another appropriate URL
    else:
        form = PatientForm()

    return render(request, "staff/add-patient.html", {"form": form})


@login_required(login_url="account_login")
def overview(request):
    check_models()
    if request.user.access < 2:
        return redirect("patient-overview")
    now = timezone.now()
    previous_day = now - relativedelta(days=1)
    previous_month = now - relativedelta(months=1)
    context = {}
    try:
        # with ThreadPoolExecutor(max_workers=10) as tp:
        #     futures = {
        #         tp.submit(fetch_today_patient, now): "today_patient",
        #         tp.submit(fetch_total_patient): "total_patient",
        #         tp.submit(fetch_previous_patients, previous_day): "previous_patients",
        #         tp.submit(fetch_monthly_medcert, now): "monthly_medcert",
        #         tp.submit(fetch_previous_medcert, previous_month): "previous_medcert",
        #         tp.submit(fetch_patients): "patients",
        #         tp.submit(fetch_categories): "categories",
        #         tp.submit(get_sorted_category, request): "sorted_category",
        #         tp.submit(get_sorted_department, request): "sorted_department",
        #         tp.submit(get_departments, request): "department_names",
        #         tp.submit(get_ambulances, request): "get_ambulances",
        #         tp.submit(get_category_data, request): "get_category_data",
        #         tp.submit(get_wheelchairs, request): "get_wheelchairs",
        #     }
        #     results = {}
        #     for future in as_completed(futures):
        #         key = futures[future]
        #         try:
        #             results[key] = future.result()
        #         except Exception as exc:
        #             logger.error(f"{key} generated an exception: {exc}")
        #             results[key] = 0

        # today_patient = results["today_patient"]
        # total_patient = results["total_patient"]
        # previous_patients = results["previous_patients"]
        # monthly_medcert = results["monthly_medcert"]
        # previous_medcert = results["previous_medcert"]
        # patients = results["patients"]
        # categories = results["categories"]
        # request, sorted_category = results["sorted_category"]
        # request, sorted_department = results["sorted_department"]
        # request, department_names = results["department_names"]
        # request, ambulances = results["get_ambulances"]
        # request, category_data = results["get_category_data"]
        # request, wheelchair_data = results["get_wheelchairs"]
        today_patient = fetch_today_patient(now)
        total_patient = fetch_total_patient()
        previous_patients = fetch_previous_patients(previous_day)
        monthly_medcert, previous_medcert = fetch_monthly_medcert(now, previous_month)
        # previous_medcert = fetch_previous_medcert(previous_month)
        patients = fetch_patients()
        categories = fetch_categories()
        request, sorted_category = get_sorted_category(request)
        request, sorted_department = get_sorted_department(request)
        request, department_names = get_departments(request)
        request, ambulances = get_ambulances(request)
        request, category_data = get_category_data(request)
        request, wheelchair_data = get_wheelchairs(request)

        # Calculate percentages
        patient_percent = (
            0.00
            if previous_patients == 0
            else round(today_patient / previous_patients * 100, 2)
        )
        medcert_percent = (
            0.00
            if previous_medcert == 0
            else round(monthly_medcert / previous_medcert * 100, 2)
        )

        department_names = [
            {"id": department.id, "department": department.department}
            for department in department_names
        ]

        bed_cache = cache.get("bed_cache", {})

        beds = bed_cache.get("query")

        if not beds:
            beds = BedStat.objects.all()
            bed_cache["query"] = beds
            cache.set("bed_cache", bed_cache, timeout=(120 * 60))

        context.update(
            {
                "today_patient": today_patient,
                "monthly_medcert": monthly_medcert,
                "categories": categories,
                "total_patient": total_patient,
                "patient_percent": patient_percent,
                "medcert_percent": medcert_percent,
                "patients": patients,
                "page": "overview",
                "sorted_category": sorted_category,
                "sorted_department": sorted_department,
                "department_names": department_names,
                "beds": beds,
                "ambulances": ambulances,
                "category_data": category_data,
                "wheelchair_data": wheelchair_data,
            }
        )
    except Exception as e:
        logger.error(f"Error in staff/overview: {str(e)}")
        messages.error(
            request, "Facing problems connecting to server. Please reload page."
        )

    return render(request, "staff/overview.html", context)


@login_required(login_url="account_login")
def add_issue(request):
    patients = User.objects.filter(access=1)
    if request.method == "POST":
        patient = User.objects.get(email=request.POST.get("patient"))
        try:
            Illness.objects.create(
                patient=patient,
                issue=request.POST.get("issue"),
            )
            Log.objects.create(user=request.user, action="Added a new illness")
        except Exception:
            messages.error(request, "Unable to add issue")
    context = {"patients": patients}
    return render(request, "staff/add-issue.html", context)


@login_required(login_url="account_login")
def inventory(request):
    if request.user.access < 2:
        return redirect("patient-overview")
    # with ThreadPoolExecutor(max_workers=2) as tp:
    #     futures = {
    #         tp.submit(fetch_inventory, InventoryDetail, Sum, request): "inventory",
    #         tp.submit(get_sorted_inventory_list, request): "sorted_inventory",
    #         tp.submit(get_counted_inventory, request): "counted_inventory",
    #     }
    #     results = {}

    #     for future in as_completed(futures):
    #         key = futures[future]
    #         try:
    #             results[key] = future.result()
    #         except Exception as e:
    #             logger.error(f"{key} generated an exception: {e}")
    #             results[key] = 0

    # request, inventory = results["inventory"]
    # request, sorted_inventory = results["sorted_inventory"]
    # request, counted_inventory = results["counted_inventory"]
    request, inventory = fetch_inventory(InventoryDetail, Sum, request)
    request, sorted_inventory = get_sorted_inventory_list(request)
    request, counted_inventory = get_counted_inventory(request)
    context = {
        "page": "inventory",
        "inventory": list(inventory),
        "sorted_inventory": sorted_inventory,
        "counted_inventory": counted_inventory,
    }
    return render(request, "staff/inventory.html", context)


@login_required(login_url="account_login")
def add_inventory(request):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method == "POST":
        form = AddInventoryForm(request.POST)
        if form.is_valid():
            form.save(request)
            # clear related cache
            cache.delete("inventory_cache")
    return redirect("staff-inventory")


@login_required(login_url="account_login")
def delete_inventory(request, pk):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method == "POST":
        form = DeleteInventoryForm(request.POST)
        if form.is_valid():
            form.save(request, pk)
            cache.delete("inventory_cache")
        else:
            messages.error(request, "Form is invalid. Please try again")
            logger.error("Delete inventory form is invalid")
    return redirect("staff-inventory")


@login_required(login_url="account_login")
def update_inventory(request, pk):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method == "POST":
        form = EditInventoryForm(request.POST)
        if form.is_valid():
            form.save(request, pk)
            cache.delete("inventory_cache")
        else:
            messages.error(request, "Form is invalid. Please try again.")
            logger.error("Update inventory form is invalid")
    return redirect("staff-inventory")


@login_required(login_url="account_login")
def bed(request):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method == "POST":
        try:
            BedStat.objects.create()
            messages.success(request, "New bed has been added!")
            cache.delete("bed_cache")
        except Exception as e:
            logger.error(f"Failed to create a new bed: {str(e)}")
            messages.error(request, "Failed to add new bed.")

    return redirect("staff-overview")


def bed_handler(request, pk):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method == "POST":
        try:
            bed = BedStat.objects.get(id=pk)
            bed.status = not bed.status
            bed.save()
            Log.objects.create(
                user=request.user,
                action=f"Updated BedStat({bed.id}) from {not bed.status} to {bed.status}",
            )
            messages.success(request, "Bed was successfully updated")
            cache.delete("bed_cache")
        except Exception:
            messages.error(request, "Error fetching bed data")
    return redirect("staff-overview")


@login_required(login_url="account_login")
def post_delete_bed(request, pk):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method.lower() == "post":
        try:
            bed = BedStat.objects.get(id=int(pk))
        except Exception as e:
            logger.info(
                f"{request.user.email} failed to fetch the corresponding bed[{int(pk)}] : {str(e)}"
            )
            messages.error(
                request, "Failed to find the corresponding bed. Please try again."
            )
            return redirect("staff-overview")

        bed.delete()
        Log.objects.create(
            user=request.user,
            action=f"{request.user.email} successfuly deleted bed instance[{bed.id}]",
        )
        cache.delete("bed_cache")

        logger.info(f"{request.user.email} successfuly deleted bed instance[{bed.id}]")
        messages.success(request, "Successfully deleted bed!")
    return redirect("staff-overview")


@login_required(login_url="account_login")
def records(request):
    if request.user.access < 2:
        return redirect("patient-overview")
    email = env("EMAIL_ADD")
    context = {"page": "records", "email": email}
    try:
        # with ThreadPoolExecutor(max_workers=5) as tp:
        #     futures = {
        #         tp.submit(fetch_history, Illness, IllnessSerializer): "fetch_history",
        #         tp.submit(
        #             fetch_certificate_chart, timezone, Certificate, relativedelta
        #         ): "fetch_certificate_chart",
        #         tp.submit(fetch_certificates, Certificate, F): "fetch_certificates",
        #         tp.submit(fetch_patient_list, request): "fetch_patient_list",
        #     }
        #     results = {}

        #     for future in as_completed(futures):
        #         key = futures[future]
        #         try:
        #             results[key] = future.result()
        #         except Exception as e:
        #             logger.error(f"{key} generated an exception: {e}")
        #             results[key] = 0

        # history, history_data = results["fetch_history"]
        # certificate_chart = results["fetch_certificate_chart"]
        # certificates = results["fetch_certificates"]
        # patient_list = results["fetch_patient_list"]
        history, history_data = fetch_history(Illness, IllnessSerializer)
        certificate_chart = fetch_certificate_chart(
            timezone, Certificate, relativedelta
        )
        certificates = fetch_certificates(Certificate, F)
        patient_list = fetch_patient_list(request)

        paginator = Paginator(history, 10)
        page = request.GET.get("page")

        try:
            history_page = paginator.page(page)
        except PageNotAnInteger:
            history_page = paginator.page(1)
        except EmptyPage:
            history_page = paginator.page(paginator.num_pages)

        cert_paginator = Paginator(certificates, 10)
        cert_page = request.GET.get("cert-page")
        try:
            certificates_page = cert_paginator.page(cert_page)
        except PageNotAnInteger:
            certificates_page = cert_paginator.page(1)
        except EmptyPage:
            certificates_page = cert_paginator.page(cert_paginator.num_pages)
        context.update(
            {
                "certificates_page": certificates_page,
                "certificate_chart": certificate_chart,
                "history": history_page,
                "history_data": history_data,
                "certificates": list(certificates),
                "patient_list": patient_list,
            }
        )

    except Exception as e:
        logger.error(f"Failed to fetch necessary data: {e}")
        messages.error(request, "Error fetching data")

    if request.method == "POST":
        certificate_id = request.POST.get("certificate_id")
        try:
            certificate = Certificate.objects.get(id=int(certificate_id))
        except Exception as e:
            logger.info(
                f"{request.user.email} failed to find certificate[id{certificate_id}]: {str(e)}"
            )
            messages.error(
                request,
                "Failed to find the certificate to be updated. Please try again",
            )
            return redirect("staff-records")

        if not certificate.is_ready:
            certificate.is_ready = True
        elif not certificate.released:
            certificate.released = True

        certificate.save()

        Log.objects.create(
            user=request.user,
            action=f"{request.user.email} updated certificate[{certificate.id}]",
        )
        logger.info(f"{request.user.email} updated certificate[{certificate.id}]")
        messages.success(request, "Successfully updated certificate request status")
        cache.delete("certificate_cache")
        return redirect("staff-records")

    return render(request, "staff/records.html", context)


def fetch_patient_list(request):
    try:
        user_cache = cache.get("user_cache", {})
        patient_list = user_cache.get("patients")
        if not patient_list:
            patient_list = User.objects.filter(access=1)
            user_cache["patients"] = patient_list
            cache.set("user_cache", user_cache, timeout=(60 * 120))
    except Exception as e:
        logger.info(f"{request.user.email} failed to fetch patient list: {str(e)}")
    finally:
        connection.close()

    return patient_list or None


@login_required(login_url="account_login")
def post_add_patient(request):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method.lower() == "post":
        try:
            patient, created = User.objects.get_or_create(
                email=request.POST.get("email")
            )
        except Exception as e:
            logger.info(f"Failed to create new patient: {str(e)}")
            messages.error(request, "Failed to add new patient")
            return redirect("staff-overview")

        if created:
            patient.access = 1
            patient.first_name = request.POST.get("first_name")
            patient.last_name = request.POST.get("last_name")
            patient.DOB = request.POST.get("DOB")
            patient.contact = request.POST.get("contact")

            password = generate_password()
            patient.set_password(password)

            patient.save()

            logger.info(f"Created new user {patient.email} with id [{patient.id}]")

            Log.objects.create(
                user=request.user,
                action=f"Created new user {patient.email} with id [{patient.id}]",
            )

            # Send an email with password to user
            send_welcome_email(patient, password)

            logger.info(f"Email was sent to: {patient.email}")
            messages.success(request, "Patient has been added to the system.")
            cache.clear()
        else:
            logger.info(f"User {patient.email} already exists.")
            messages.error(request, f"User {patient.email} already exists.")
    return redirect("staff-overview")


@login_required(login_url="account_login")
def create_patient_add_issue(request):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method == "POST":
        try:
            patient, created = User.objects.get_or_create(
                email=request.POST.get("email")
            )
            if created:
                patient.access = 1
                password = generate_password()
                patient.set_password(password)
                patient.save()
                logger.info(f"Created new user {patient.email} with id [{patient.id}]")

                Log.objects.create(
                    user=request.user,
                    action=f"Created new user {patient.email} with id [{patient.id}]",
                )
                subject = "Welcome to HealthHarmony!"
                body = (
                    f"<h1>This is your password {password}</h1><p>With HTML content</p>"
                )
                from_email = env("EMAIL_ADD")
                recipient_list = [patient.email]
                email = EmailMessage(subject, body, from_email, recipient_list)
                email.content_subtype = "html"
                email.send()
                logger.info(f"Email was sent to: {patient.email}")
                messages.success(request, "Patient has been added to the system.")
            else:
                logger.info(f"User {patient.email} already exists.")

            visit = Illness.objects.create(
                patient=patient, issue=request.POST.get("issue"), staff=request.user
            )
            logger.info(
                f"Created new illness record for patient {patient.email} with id [{visit.id}]"
            )
            messages.success(request, "A new record has been added.")

            DataChangeLog.objects.create(
                table="Illness",
                record_id=visit.id,
                action="create",
                new_value=visit.__str__(),
                changed_by=request.user,
            )
            logger.info(f"Logged data change for illness record id [{visit.id}]")

        except Exception as e:
            messages.error(request, "System faced some error")
            logger.error(f"Error occurred while creating patient or issue: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "staff-records"))


def access_checker(request):
    if request.user.access < 2:
        return redirect("home")


@login_required(login_url="account_login")
def patients_and_accounts(request):
    if request.user.access < 2:
        return redirect("patient-overview")
    context = {}
    try:
        last_visit = Illness.objects.filter(patient=OuterRef("pk")).values("added")
        patients = (
            User.objects.filter(access=1)
            .annotate(
                department_name=F("department__department"),
                last_visit=Coalesce(
                    Subquery(last_visit[:1]), Value(None), output_field=CharField()
                ),
            )
            .distinct()
            .values(
                "last_visit",
                "first_name",
                "last_name",
                "profile",
                "id",
                "date_joined",
                "department_name",
                "email",
                "department",
            )
        )
        for patient in patients:
            if patient["date_joined"]:
                patient["date_joined"] = patient["date_joined"].isoformat()
        patients_paginator = Paginator(patients, 10)

        try:
            patients_page = patients_paginator.page(request.GET.get("patients-page"))
        except PageNotAnInteger:
            patients_page = patients_paginator.page(1)
            logger.error("Page set was not integer")
        except EmptyPage:
            patients_page = patients_paginator.page(patients_paginator.num_pages)
            logger.error("No page was set")

        last_department_visit = (
            Illness.objects.filter(patient=OuterRef("pk"))
            .exclude(added__isnull=True)
            .order_by("-added")
            .values("added")
        )

        # Annotate the departments with the last visit date of any patient in that department
        departments = (
            Department.objects.annotate(
                last_department_visit=Subquery(
                    User.objects.filter(department=OuterRef("pk"), access=1)
                    .annotate(
                        last_department_visit=Coalesce(
                            Subquery(last_department_visit[:1]),
                            Value(None),
                            output_field=CharField(),
                        )
                    )
                    .exclude(last_department_visit__isnull=True)
                    .values(
                        "last_department_visit"
                    )  # Only get the last visit of the first patient in the department
                ),
                count=Count("user_department"),
            )
            .distinct()
            .values()
        )
        employees = fetch_employees(
            OuterRef, Coalesce, Subquery, Value, DateTimeField, messages, request
        )

        context.update(
            {
                "patients": list(patients),
                "patients_page": patients_page,
                "departments": departments,
                "departmentData": list(departments),
                "employees": employees,
                "employeeData": list(employees),
                "page": "accounts",
            }
        )

    except Exception as e:
        logger.error(f"Failed to fetch data: {str(e)}")
        messages.error(request, "Failed to fetch necessary data. Please reload page.")
    finally:
        connection.close()
    return render(request, "staff/accounts.html", context)


@login_required(login_url="account_login")
def add_department(request):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method == "POST":
        department_name = request.POST.get("department_name")
        try:
            department, created = Department.objects.get_or_create(
                department=department_name
            )

            if created:
                messages.success(request, "Success! A new department has been added.")
                Log.objects.create(
                    user=request.user,
                    action=f"New department instance has been created[id:{department.id}]",
                )

            else:
                messages.error(
                    request,
                    "Department already exists. Please add a new department name",
                )
                logger.error(
                    f"Failed to create a new department as it already exists[id: {department.id}]"
                )

        except Exception as e:
            messages.error(request, "Failed to create a new department")
            logger.error(f"Failed to create a new department: {str(e)}")
    return redirect("staff-accounts")


@login_required(login_url="account_login")
def delete_department(request, pk):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method == "POST":
        form = DeleteDepartmentForm(request.POST)
        if form.is_valid():
            form.save(request, pk)
        else:
            messages.error(request, "Form is invalid. Please try again.")
            logger.info(
                f"{request.user.email} has passed an invalid Delete Department Form"
            )
    return redirect("staff-accounts")


@login_required(login_url="account_login")
def edit_department(request, pk):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method == "POST":
        form = EditDepartmentForm(request.POST)
        if form.is_valid():
            form.save(request, pk)
        else:
            messages.error(request, "Form is invalid. Please try again.")
            logger.info(
                f"{request.user.email} has passed an invalid Edit Department Form"
            )
    return redirect("staff-accounts")


@login_required(login_url="account_login")
def post_create_update_ambulance(request):
    if request.user.access < 2:
        return redirect("patient-overview")
    if request.method.lower() == "post":
        print(request.POST)
        form = CreateUpdateAmbulance(request.POST)
        if form.is_valid():
            form.save(request)
        else:
            logger.info("CreateUpdateAmbulance is invalid")
            messages.error(request, "Submitted data is invalid. Please try again")
    return redirect("staff-overview")


@login_required(login_url="account_login")
def post_create_wheelchair(request):
    if request.user.access < 2:
        return redirect("patient-overview")

    if request.method.lower() == "post":
        form = CreateWheelChairQuantity(request.POST)
        logger.info(request.POST)

        if form.is_valid():
            form.save(request)
        else:
            logger.info("CreateWheelChairQuantity is invalid")
            messages.error(request, "Submitted data is invalid. Please try again")
    return redirect("staff-overview")


def get_ambulances(request):
    ambulances = None
    try:
        ambulances = cache.get("ambulances")
        if not ambulances:
            ambulances = Ambulansya.objects.all()
            cache.set("ambulances", ambulances, timeout=(60 * 60))
    except Exception as e:
        logger.warning(f"Failed to fetch the ambulances: {str(e)}")
        messages.error(request, "Failed to fetch necessary data. Please reload page.")
    finally:
        connection.close()
    return request, ambulances


def get_category_data(request):
    category_data = []
    try:
        category_cache = cache.get("category_cache", {})

        category_data = category_cache.get("category_data")
        categories = category_cache.get("query")

        if not categories:
            categories = Category.objects.all()
            category_cache["query"] = categories
            cache.set("category_cache", category_cache, timeout=(60 * 120))

        if not category_data:
            category_data = []
            if categories:
                for category in categories:
                    data = CategorySerializer(category)
                    category_data.append(data.data)
            category_cache["category_data"] = category_data
            cache.set("category_cache", category_cache, timeout=(60 * 120))

    except Exception as e:
        messages.error(request, "Failed to fetch necessary data. Please reload page.")
        logger.warning(f"Failed to fetch the category data: {str(e)}")
    finally:
        connection.close()
    return request, category_data


def get_wheelchairs(request):
    wheelchair_data = {}
    try:
        avail_wheelchairs = cache.get("avail_wheelchairs")
        if not avail_wheelchairs:
            avail_wheelchairs = WheelChair.objects.filter(is_avail=True)[:1]
            cache.set("avail_wheelchairs", avail_wheelchairs, timeout=(60 * 60))
        unavail_wheelchairs = cache.get("unavail_wheelchairs")
        if not unavail_wheelchairs:
            unavail_wheelchairs = WheelChair.objects.filter(is_avail=False)[:1]
            cache.set("unavail_wheelchairs", unavail_wheelchairs, timeout=(60 * 60))
        for wheel in avail_wheelchairs:
            wheelchair_data.update(
                {
                    "avail": wheel.quantity or 0,
                }
            )
        for wheel in unavail_wheelchairs:
            wheelchair_data.update({"unavail": wheel.quantity or 0})
    except Exception as e:
        logger.warning(f"Failed to fetch wheelchair data: {str(e)}")
        messages.error(request, "Failed to fetch necessary data. Please reload page.")
    finally:
        connection.close()

    return request, wheelchair_data
