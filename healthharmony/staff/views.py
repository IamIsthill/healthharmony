from django.shortcuts import render, redirect
import secrets
import string
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
import environ
import logging
from concurrent.futures import as_completed, ThreadPoolExecutor
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.dateparse import parse_datetime

from healthharmony.bed.models import BedStat
from healthharmony.users.models import User
from healthharmony.administrator.models import Log, DataChangeLog
from healthharmony.treatment.models import Illness, IllnessTreatment
from healthharmony.inventory.models import InventoryDetail
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
)
from healthharmony.staff.forms import (
    PatientForm,
    AddInventoryForm,
    EditInventoryForm,
    DeleteInventoryForm,
)

env = environ.Env()
environ.Env.read_env(env_file="healthharmony/.env")
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
    with ThreadPoolExecutor() as tp:
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
    try:
        beds = BedStat.objects.all()
    except Exception:
        messages.error(request, "Error fetching bed data")
    context = {"beds": beds, "page": "bed"}
    return render(request, "staff/bed.html", context)


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
    return redirect("staff-bed")


def records(request):
    access_checker(request)
    email = env("EMAIL_ADD")
    context = {"page": "records", "email": email}
    try:
        history = (
            Illness.objects.all()
            .annotate(
                first_name=Coalesce(F("patient__first_name"), Value("")),
                last_name=Coalesce(F("patient__last_name"), Value("")),
                category=Coalesce(F("illness_category__category"), Value("")),
            )
            .values(
                "first_name",
                "last_name",
                "issue",
                "updated",
                "diagnosis",
                "category",
                "staff",
                "doctor",
                "id",
                "added",
                "patient",
            )
        )

        # Preparing the data for each illness
        for data in history:
            data["updated"] = data["updated"].isoformat()
            data["added"] = data["added"].isoformat()
            data["treatment"] = []

            # Get the related IllnessTreatment instances
            illness_treatments = IllnessTreatment.objects.filter(
                illness_id=data["id"]
            ).select_related("inventory_detail")

            for treatment in illness_treatments:
                data["treatment"].append(
                    {
                        "quantity": treatment.quantity or 0,
                        "medicine": treatment.inventory_detail.item_name,
                    }
                )
        paginator = Paginator(history, 10)
        page = request.GET.get("page")

        try:
            history_page = paginator.page(page)
        except PageNotAnInteger:
            history_page = paginator.page(1)
        except EmptyPage:
            history_page = paginator.page(paginator.num_pages)
        context.update({"history": history_page, "history_data": list(history)})
    except Exception:
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
            else:
                logger.info(f"User {patient.email} already exists.")

            visit = Illness.objects.create(
                patient=patient, issue=request.POST.get("issue")
            )
            logger.info(
                f"Created new illness record for patient {patient.email} with id [{visit.id}]"
            )

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
