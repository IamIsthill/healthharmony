from django.shortcuts import render, redirect
import secrets
import string
from django.db.models import Count
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
import environ
import logging

from healthharmony.bed.models import BedStat
from healthharmony.users.models import User, Department
from healthharmony.administrator.models import Log, DataChangeLog
from healthharmony.treatment.models import Illness, Certificate, Category
from healthharmony.inventory.models import InventoryDetail, QuantityHistory
from healthharmony.base.functions import check_models
from healthharmony.staff.functions import (
    get_sorted_category,
    get_sorted_department,
    get_departments,
    get_sorted_inventory_list,
)
from healthharmony.staff.forms import PatientForm

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
        today_patient = (
            User.objects.filter(patient_illness__updated__date=now.date())
            .distinct()
            .count()
            or 0
        )
        total_patient = (
            User.objects.annotate(illness_count=Count("patient_illness"))
            .filter(illness_count__gt=0)
            .count()
            or 0
        )
        previous_patients = (
            User.objects.filter(patient_illness__updated__date=previous_day.date())
            .distinct()
            .count()
            or 0
        )
        if previous_patients == 0:
            patient_percent = 0.00
        else:
            patient_percent = today_patient / previous_patients * 100
            patient_percent = round(patient_percent, 2)
        monthly_medcert = (
            Certificate.objects.filter(
                requested__month=now.month, requested__year=now.year, released=True
            ).count()
            or 0
        )
        previous_medcert = (
            Certificate.objects.filter(
                requested__month=previous_month.month,
                requested__year=previous_month.year,
                released=True,
            ).count()
            or 0
        )

        if previous_medcert == 0:
            medcert_percent = 0.00
        else:
            medcert_percent = monthly_medcert / previous_medcert * 100
            medcert_percent = round(medcert_percent, 2)

        patients = User.objects.filter(access=1)

        categories = Category.objects.all()
        context.update(
            {
                "today_patient": today_patient,
                "monthly_medcert": monthly_medcert,
                "categories": categories,
                "total_patient": total_patient,
                "patient_percent": patient_percent,
                "medcert_percent": medcert_percent,
                "patients": patients,
            }
        )
    except Exception as e:
        logger.error(f"Error in staff/overview: {str(e)}")
        messages.error(
            request, "Facing problems connecting to server. Please reload page."
        )

    request, sorted_category = get_sorted_category(request)
    request, sorted_department = get_sorted_department(request)
    request, department_names = get_departments(request)

    department_names = [
        {"id": department.id, "department": department.department}
        for department in department_names
    ]

    context.update(
        {
            "page": "overview",
            "sorted_category": sorted_category,
            "sorted_department": sorted_department,
            "department_names": department_names,
        }
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
    now = timezone.now()
    counts = {
        "medicine_avail": 0,
        "medicine_expired": 0,
        "supply_avail": 0,
        "supply_expired": 0,
    }
    inventory = (
        InventoryDetail.objects.all()
        .annotate(total_quantity=Sum("quantities__updated_quantity"))
        .values("id", "item_name", "category", "expiration_date", "total_quantity")
    )
    inventory_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for inv in inventory:
        if inv["total_quantity"] is None:
            inv["total_quantity"] = 0
        if inv["category"] == "Medicine" and inv["expiration_date"] > now.date():
            counts["medicine_avail"] += inv["total_quantity"]
        if inv["category"] == "Medicine" and inv["expiration_date"] <= now.date():
            counts["medicine_expired"] += inv["total_quantity"]
        if (
            inv["category"] == "Supply"
            and inv["expiration_date"] > now.date()
            or inv["expiration_date"] is None
        ):
            counts["supply_avail"] += inv["total_quantity"]
        if inv["category"] == "Supply" and inv["expiration_date"] <= now.date():
            counts["supply_expired"] += inv["total_quantity"]

    start_date = (now - timedelta(days=365)).replace(day=1)
    for month_offset in range(13):
        current_month = start_date + relativedelta(months=month_offset)
        next_month = current_month + relativedelta(months=1)
        inventory_data["medicine"]["year"][current_month.strftime("%B")] = 0
        inventory_data["supply"]["year"][current_month.strftime("%B")] = 0
        inventory_data["medicine"]["detail-year"][inv["item_name"]] = 0
        inventory_data["supply"]["detail-year"][inv["item_name"]] = 0

        for inv in inventory:
            item_data = InventoryDetail.objects.get(pk=inv["id"])
            item_data_quantity = item_data.quantities.filter(
                timestamp__gte=current_month, timestamp__lt=next_month
            ).aggregate(total_quantity=Sum("updated_quantity"))
            if (
                inv["category"] == "Medicine"
                and inv["expiration_date"] >= current_month.date()
                and inv["expiration_date"] < next_month.date()
            ):
                inventory_data["medicine"]["year"][current_month.strftime("%B")] += inv[
                    "total_quantity"
                ]
            elif (
                inv["category"] == "Supply"
                and inv["expiration_date"] >= current_month.date()
                and inv["expiration_date"] < next_month.date()
            ):
                inventory_data["supply"]["year"][current_month.strftime("%B")] += inv[
                    "total_quantity"
                ]
            if inv["category"] == "Medicine":
                inventory_data["medicine"]["detail-year"][inv["item_name"]] = (
                    item_data_quantity["total_quantity"] or 0
                )
            if inv["category"] == "Supply":
                inventory_data["supply"]["detail-year"][inv["item_name"]] = (
                    item_data_quantity["total_quantity"] or 0
                )

    last30days = now - timedelta(days=30)
    for five_offset in range(6):
        current_day = last30days + timedelta(days=five_offset * 5)
        next_five = current_day + timedelta(days=5)
        inventory_data["medicine"]["month"][current_day.strftime("%B %d")] = 0
        inventory_data["supply"]["month"][current_day.strftime("%B %d")] = 0

        for inv in inventory:
            item_data = InventoryDetail.objects.get(pk=inv["id"])
            item_data_quantity = item_data.quantities.filter(
                timestamp__gte=current_day, timestamp__lt=next_five
            ).aggregate(total_quantity=Sum("updated_quantity"))
            if (
                inv["category"] == "Medicine"
                and inv["expiration_date"] >= current_day.date()
                and inv["expiration_date"] < next_five.date()
            ):
                inventory_data["medicine"]["month"][
                    current_day.strftime("%B %d")
                ] += inv["total_quantity"]
            elif (
                inv["category"] == "Supply"
                and inv["expiration_date"] >= current_day.date()
                and inv["expiration_date"] < next_five.date()
            ):
                inventory_data["supply"]["month"][current_day.strftime("%B %d")] += inv[
                    "total_quantity"
                ]
            if inv["category"] == "Medicine":
                inventory_data["medicine"]["detail-month"][inv["item_name"]] = (
                    item_data_quantity["total_quantity"] or 0
                )
            if inv["category"] == "Supply":
                inventory_data["supply"]["detail-month"][inv["item_name"]] = (
                    item_data_quantity["total_quantity"] or 0
                )

    week = now - timedelta(days=6)
    for day_offset in range(7):
        current_day = week + timedelta(days=day_offset * 1)
        start_of_day = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = current_day.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        inventory_data["medicine"]["week"][start_of_day.strftime("%B %d")] = 0
        inventory_data["supply"]["week"][start_of_day.strftime("%B %d")] = 0

        for inv in inventory:
            item_data = InventoryDetail.objects.get(pk=inv["id"])
            item_data_quantity = item_data.quantities.filter(
                timestamp__gte=start_of_day, timestamp__lt=end_of_day
            ).aggregate(total_quantity=Sum("updated_quantity"))
            if (
                inv["category"] == "Medicine"
                and inv["expiration_date"] >= start_of_day.date()
                and inv["expiration_date"] < end_of_day.date()
            ):
                inventory_data["medicine"]["week"][
                    start_of_day.strftime("%B %d")
                ] += inv["total_quantity"]
            elif (
                inv["category"] == "Supply"
                and inv["expiration_date"] >= start_of_day.date()
                and inv["expiration_date"] < end_of_day.date()
            ):
                inventory_data["supply"]["week"][current_day.strftime("%B %d")] += inv[
                    "total_quantity"
                ]
            if inv["category"] == "Medicine":
                inventory_data["medicine"]["detail-week"][inv["item_name"]] = (
                    item_data_quantity["total_quantity"] or 0
                )
            if inv["category"] == "Supply":
                inventory_data["supply"]["detail-week"][inv["item_name"]] = (
                    item_data_quantity["total_quantity"] or 0
                )

    inventory_list = list(inventory)

    request, sorted_inventory = get_sorted_inventory_list(request)

    context = {
        "page": "inventory",
        "inventory": inventory_list,
        "counts": counts,
        "inventory_data": dict(inventory_data),
        "sorted_inventory": sorted_inventory,
    }
    return render(request, "staff/inventory.html", context)


def add_inventory(request):
    if request.method == "POST":
        try:
            item = InventoryDetail.objects.create(
                item_no=request.POST.get("item_no"),
                unit=request.POST.get("unit"),
                item_name=request.POST.get("item_name"),
                category=request.POST.get("category"),
                description=request.POST.get("description"),
                expiration_date=request.POST.get("expiration_date"),
            )
            Log.objects.create(
                user=request.user, action=f"Created inventory item with id [{item.id}]"
            )
            return redirect("staff-inventory")
        except Exception:
            messages.error(request, "Failed to add the inventory item")


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
        history = Illness.objects.all().annotate(
            first_name=Coalesce(F("patient__first_name"), Value("")),
            last_name=Coalesce(F("patient__last_name"), Value("")),
        )
        context.update({"history": history})
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
