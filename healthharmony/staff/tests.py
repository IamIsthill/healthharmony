import os
import django
from django.test import RequestFactory
import json


def main():
    # Set the Django settings module environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthharmony.app.settings")

    # Setup Django
    django.setup()

    # factory = RequestFactory()
    # request = factory.get("/dummy-url/")

    # test_data_structure()
    # test_staff_patient_percents()
    test_medcert_percents()


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


if __name__ == "__main__":
    main()
