import os
import django
from django.test import RequestFactory
import json
from django.db.models import Sum


def main():
    # Set the Django settings module environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthharmony.app.settings")

    # Setup Django
    django.setup()

    factory = RequestFactory()
    request = factory.get("/dummy-url/")

    # test_data_structure()
    # test_staff_patient_percents()
    # test_medcert_percents()
    # test_query_inventory_data_structure(request)
    test_inventory_list_function(request)


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

    from healthharmony.treatment.models import Certificate

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
    from healthharmony.inventory.models import InventoryDetail

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


if __name__ == "__main__":
    main()
