from django.shortcuts import render, redirect
import secrets
import string
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
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
import environ
import logging
from concurrent.futures import as_completed, ThreadPoolExecutor
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from healthharmony.models.bed.models import BedStat
from healthharmony.users.models import User, Department
from healthharmony.administrator.models import Log, DataChangeLog
from healthharmony.models.treatment.models import Illness, IllnessTreatment, Certificate
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
)
from healthharmony.staff.forms import (
    PatientForm,
    AddInventoryForm,
    EditInventoryForm,
    DeleteInventoryForm,
    DeleteDepartmentForm,
    EditDepartmentForm,
)
from healthharmony.app.settings import env

logger = logging.getLogger(__name__)


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for i in range(length))


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


def overview(request):
    check_models()
    access_checker(request)
    now = timezone.now()
    previous_day = now - relativedelta(days=1)
    previous_month = now - relativedelta(months=1)
    context = {}
    try:
        with ThreadPoolExecutor() as tp:
            futures = {
                tp.submit(fetch_today_patient, now): "today_patient",
                tp.submit(fetch_total_patient): "total_patient",
                tp.submit(fetch_previous_patients, previous_day): "previous_patients",
                tp.submit(fetch_monthly_medcert, now): "monthly_medcert",
                tp.submit(fetch_previous_medcert, previous_month): "previous_medcert",
                tp.submit(fetch_patients): "patients",
                tp.submit(fetch_categories): "categories",
                tp.submit(get_sorted_category, request): "sorted_category",
                tp.submit(get_sorted_department, request): "sorted_department",
                tp.submit(get_departments, request): "department_names",
            }
            results = {}
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as exc:
                    logger.error(f"{key} generated an exception: {exc}")
                    results[key] = 0

        today_patient = results["today_patient"]
        total_patient = results["total_patient"]
        previous_patients = results["previous_patients"]
        monthly_medcert = results["monthly_medcert"]
        previous_medcert = results["previous_medcert"]
        patients = results["patients"]
        categories = results["categories"]
        request, sorted_category = results["sorted_category"]
        request, sorted_department = results["sorted_department"]
        request, department_names = results["department_names"]

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

        beds = BedStat.objects.all()

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
            }
        )
    except Exception as e:
        logger.error(f"Error in staff/overview: {str(e)}")
        messages.error(
            request, "Facing problems connecting to server. Please reload page."
        )

    return render(request, "staff/overview.html", context)


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


def inventory(request):
    access_checker(request)
    with ThreadPoolExecutor(max_workers=2) as tp:
        futures = {
            tp.submit(fetch_inventory, InventoryDetail, Sum, request): "inventory",
            tp.submit(get_sorted_inventory_list, request): "sorted_inventory",
            tp.submit(get_counted_inventory, request): "counted_inventory",
        }
        results = {}

        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                logger.error(f"{key} generated an exception: {e}")
                results[key] = 0

    request, inventory = results["inventory"]
    request, sorted_inventory = results["sorted_inventory"]
    request, counted_inventory = results["counted_inventory"]
    # request, inventory = fetch_inventory(InventoryDetail, Sum, request)
    # request, sorted_inventory = get_sorted_inventory_list(request)
    # request, counted_inventory = get_counted_inventory(request)
    context = {
        "page": "inventory",
        "inventory": list(inventory),
        "sorted_inventory": sorted_inventory,
        "counted_inventory": counted_inventory,
    }
    return render(request, "staff/inventory.html", context)


def add_inventory(request):
    access_checker(request)
    if request.method == "POST":
        form = AddInventoryForm(request.POST)
        if form.is_valid():
            form.save(request)
    return redirect("staff-inventory")


def delete_inventory(request, pk):
    access_checker(request)
    if request.method == "POST":
        form = DeleteInventoryForm(request.POST)
        if form.is_valid():
            form.save(request, pk)
        else:
            messages.error(request, "Form is invalid. Please try again")
            logger.error("Delete inventory form is invalid")
    return redirect("staff-inventory")


def update_inventory(request, pk):
    access_checker(request)
    if request.method == "POST":
        form = EditInventoryForm(request.POST)
        if form.is_valid():
            form.save(request, pk)
        else:
            messages.error(request, "Form is invalid. Please try again.")
            logger.error("Update inventory form is invalid")
    return redirect("staff-inventory")


def bed(request):
    access_checker(request)
    if request.method == "POST":
        try:
            BedStat.objects.create()
            messages.success(request, "New bed has been added!")
        except Exception as e:
            logger.error(f"Failed to create a new bed: {str(e)}")
            messages.error(request, "Failed to add new bed.")

    return redirect("staff-overview")


def bed_handler(request, pk):
    access_checker(request)
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
        except Exception:
            messages.error(request, "Error fetching bed data")
    return redirect("staff-overview")


def records(request):
    access_checker(request)
    email = env("EMAIL_ADD")
    context = {"page": "records", "email": email}
    try:
        with ThreadPoolExecutor() as tp:
            futures = {
                tp.submit(
                    fetch_history, Illness, Coalesce, F, Value, IllnessTreatment
                ): "fetch_history",
                tp.submit(
                    fetch_certificate_chart, timezone, Certificate, relativedelta
                ): "fetch_certificate_chart",
                tp.submit(fetch_certificates, Certificate, F): "fetch_certificates",
            }
            results = {}

            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    logger.error(f"{key} generated an exception: {e}")
                    results[key] = 0
        # history = fetch_history(Illness, Coalesce, F, Value, IllnessTreatment)
        history = results["fetch_history"]
        certificate_chart = results["fetch_certificate_chart"]
        certificates = results["fetch_certificates"]
        # certificate_chart = fetch_certificate_chart(timezone, Certificate, relativedelta)

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
                "history_data": list(history),
                "certificates": list(certificates),
            }
        )

    except Exception as e:
        logger.error(f"Failed to fetch necessary data: {e}")
        messages.error(request, "Error fetching data")

    return render(request, "staff/records.html", context)


def create_patient_add_issue(request):
    access_checker(request)
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
                subject = "Welcome New User"
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


def patients_and_accounts(request):
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
            }
        )

    except Exception as e:
        logger.error(f"Failed to fetch data: {str(e)}")
        messages.error(request, "Failed to fetch necessary data. Please reload page.")
    return render(request, "staff/accounts.html", context)


def add_department(request):
    access_checker(request)
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


def delete_department(request, pk):
    access_checker(request)
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


def edit_department(request, pk):
    access_checker(request)
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
