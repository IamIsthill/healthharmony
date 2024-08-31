import os
import django
from django.test import RequestFactory
import json
from django.db.models import OuterRef, Subquery, Value, Sum, F, CharField
from django.db.models.functions import Coalesce
import logging

logger = logging.getLogger(__name__)


def main():
    # Set the Django settings module environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthharmony.app.settings")

    # Setup Django
    django.setup()

    # factory = RequestFactory()
    # request = factory.get("/dummy-url/?date-filter=yearly")

    # test_data_structure()
    # test_staff_patient_percents()
    # test_medcert_percents()
    # test_query_inventory_data_structure(request)
    # test_inventory_list_function(request)
    # test_chart_inventory_structure(request)
    # test_diagnosis_predictor()
    # count_current_stocks_expired_items()
    # test_get_visit_records(request)
    # test_certificates_chart()
    # test_certificates()
    # test_department_names()
    # test_history_structure()
    test_accounts()


def test_accounts():
    from healthharmony.users.models import User, Department
    from healthharmony.models.treatment.models import Illness

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
        )
    )
    for patient in patients:
        print(patient["last_visit"])
        if patient["date_joined"]:
            patient["date_joined"] = patient["date_joined"].isoformat()
    # print(json.dumps(list(patients), indent=4, sort_keys=True))


def test_history_structure():
    from healthharmony.models.treatment.models import Illness, IllnessTreatment
    from healthharmony.users.models import User
    from django.db.models import F
    from django.db.models.functions import Coalesce

    history = (
        Illness.objects.all()
        .select_related("staff", "doctor", "illness_category", "patient")
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

    for data in history:
        data["updated"] = data["updated"].isoformat()
        data["added"] = data["added"].isoformat()
        data["treatment"] = []

        try:
            staff = User.objects.get(id=data["staff"])
            doctor = User.objects.get(id=data["doctor"])
            data["staff"] = (
                f"{staff.first_name} {staff.last_name}"
                if staff
                else "First Name Last Name"
            )
            data["doctor"] = (
                f"{doctor.first_name} {doctor.last_name}"
                if doctor
                else "First Name Last Name"
            )
        except Exception as e:
            logger.error(f"Cannot find id: {str(e)}")
            data["staff"] = "First Name Last Name"
            data["doctor"] = "First Name Last Name"

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
    print(json.dumps(list(history), indent=4, sort_keys=True))


def test_department_names():
    from healthharmony.users.models import Department, User
    from healthharmony.models.treatment.models import Illness
    from django.db.models import Subquery, OuterRef, Exists, F

    # Subquery to check if there are any Illness instances associated with users in the department
    illness_exists_subquery = Illness.objects.filter(
        patient=OuterRef("user_department")
    ).values("id")[:1]

    departments = (
        Department.objects.annotate(
            user_id=F("user_department__id"),
            has_illness=Exists(illness_exists_subquery),
        )
        .filter(has_illness=True)
        .values("department")
    )

    print(json.dumps(list(departments), indent=4, sort_keys=True))


def test_certificates():
    from healthharmony.treatment.models import Certificate
    from django.db.models import F

    certificates = (
        Certificate.objects.all()
        .annotate(email=F("patient__email"))
        .values("patient", "purpose", "requested", "released", "email")
    )

    for cert in certificates:
        cert["requested"] = cert["requested"].isoformat()

    # print(certificates)

    print(json.dumps(list(certificates), indent=4, sort_keys=True))


def test_certificates_chart():
    from healthharmony.models.treatment.models import Certificate
    from django.utils import timezone
    from dateutil.relativedelta import relativedelta
    from healthharmony.staff.functions import (
        get_init_loop_params,
        get_changing_loop_params,
    )

    certificate_chart = {}

    cert_dates = ["yearly", "monthly", "weekly"]

    now = timezone.now()

    start = now - relativedelta(months=11)

    certificates = Certificate.objects.filter(requested__gte=start)

    for cert_date in cert_dates:
        start, max_range, date_format, date_loop = get_init_loop_params(cert_date, now)
        certificate_chart[cert_date] = []
        for offset in range(max_range):
            main_start, main_end = get_changing_loop_params(
                offset, start, date_loop, cert_date
            )
            count = 0
            for cert in certificates:
                if cert.requested >= main_start and cert.requested < main_end:
                    count = count + 1
            certificate_chart[cert_date].append(
                {f"{main_start.strftime(date_format)}": count}
            )

    print(certificate_chart)


def test_get_visit_records(request):
    from healthharmony.models.treatment.models import Illness, IllnessTreatment
    from django.db.models import Q, F, Prefetch
    from django.db.models.functions import Coalesce
    from django.utils.dateparse import parse_datetime

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

    print(json.dumps(list(history), indent=4, sort_keys=True))


def count_current_stocks_expired_items():
    from healthharmony.models.inventory.models import InventoryDetail

    try:
        inventory_data = (
            InventoryDetail.objects.all()
            .annotate(quantity=Sum("quantities__updated_quantity"))
            .values("category", "expiration_date", "quantity")
        )
        for data in inventory_data:
            if data["expiration_date"]:
                data["expiration_date"] = data["expiration_date"].isoformat()
        print_data(inventory_data)
    except Exception as e:
        logger.error(str(e))


def test_data_structure():
    from healthharmony.staff.functions import get_sorted_department

    # Initialize RequestFactory and create a dummy GET request
    factory = RequestFactory()
    request = factory.get(
        "/dummy-url/"
    )  # The URL here doesn't matter; it's just a placeholder

    # Call the function with the dummy request
    request, department_data = get_sorted_department(request)
    print(json.dumps(department_data, indent=4, sort_keys=True))


def test_staff_patient_percents():
    from django.utils import timezone
    from dateutil.relativedelta import relativedelta
    from django.db.models import Count

    from healthharmony.users.models import User

    now = timezone.now()
    previous_day = now - relativedelta(days=1)

    today_patients = (
        User.objects.filter(patient_illness__updated__date=now.date())
        .distinct()
        .count()
        or 0
    )
    previous_patients = (
        User.objects.filter(patient_illness__updated__date=previous_day.date())
        .distinct()
        .count()
        or 0
    )

    percent = today_patients / previous_patients * 100
    percent = round(percent, 2)
    print(percent)
    # print(previous_day.date())


def test_medcert_percents():
    from django.utils import timezone
    from dateutil.relativedelta import relativedelta

    from healthharmony.models.treatment.models import Certificate

    now = timezone.now()
    previous_month = now - relativedelta(months=1)
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
    print(medcert_percent)


def test_query_inventory_data_structure(request):
    from healthharmony.staff.functions import get_inventory_data
    from healthharmony.models.inventory.models import InventoryDetail

    inventory = (
        InventoryDetail.objects.all()
        .annotate(total_quantity=(Sum("quantities__updated_quantity")) or 0)
        .values("id", "total_quantity", "item_name", "category", "expiration_date")
    )

    for data in inventory:
        if data["total_quantity"] is None:
            data["total_quantity"] = 0
        data["expiration_date"] = data["expiration_date"].isoformat()
    print(json.dumps(list(inventory), indent=4, sort_keys=True))

    # print(inventory)


def test_inventory_list_function(request):
    from healthharmony.staff.functions import get_sorted_inventory_list

    request, inventory = get_sorted_inventory_list(request)
    print(json.dumps((inventory), indent=4, sort_keys=True))


def test_chart_inventory_structure(request):
    from healthharmony.models.inventory.models import InventoryDetail
    from django.contrib import messages
    from django.utils import timezone
    from datetime import timedelta
    from dateutil.relativedelta import relativedelta
    from healthharmony.staff.functions import (
        get_init_loop_params,
        get_changing_loop_params,
        get_counted_inventory,
    )

    try:
        categories = ["Medicine", "Supply"]
        filters = ["yearly", "monthly", "weekly"]

        inventory_data = {
            category: {filter: {} for filter in filters} for category in categories
        }

        now = timezone.now()

        for category in inventory_data:

            for filter in inventory_data[category]:
                start, max_range, date_format, date_loop = get_init_loop_params(
                    filter, now
                )

                for offset in range(max_range):
                    main_start, main_end = get_changing_loop_params(
                        offset, start, date_loop, filter
                    )
                    inventory = InventoryDetail.objects.filter(
                        quantities__timestamp__gte=main_start,
                        quantities__timestamp__lte=main_end,
                    ).annotate(total_quantity=Sum("quantities__updated_quantity"))
                    inventory_data[category][filter][
                        main_start.strftime(date_format)
                    ] = []
                    if inventory:

                        for data in inventory:
                            inventory_data[category][filter][
                                main_start.strftime(date_format)
                            ].append(
                                {
                                    "total_quantity": data.total_quantity or 0,
                                    "expiration_date": data.expiration_date.isoformat()
                                    if data.expiration_date
                                    else "",
                                }
                            )
        request, inventory_data = get_counted_inventory(request)

        print(json.dumps(inventory_data, indent=4, sort_keys=True))
    except Exception as e:
        logger.error(str(e))
        messages.error(request, "Failed to fetch inventory data.")


#  def get_inventory_chart_data(request):


def test_diagnosis_predictor():
    from healthharmony.models.treatment.models import Illness

    data = Illness.objects.all().values("pk", "issue", "diagnosis")
    logger.info("Illness data was successfully fetched.")
    for d in data:
        if d["issue"] is None:
            d["issue"] = ""
        if d["diagnosis"] is None:
            d["diagnosis"] = ""
    print(json.dumps((data), indent=4, sort_keys=True))


def print_data(data):
    print(json.dumps(list(data), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
