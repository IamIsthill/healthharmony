from django.test import TestCase
from healthharmony.users.models import Department, User
from healthharmony.treatment.models import Illness, IllnessTreatment
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import (
    OuterRef,
    Subquery,
    Value,
    Sum,
    F,
    CharField,
    DateTimeField,
    Count,
)
from datetime import datetime
from django.db.models.functions import Coalesce
import json


# Create your tests here.
class TestDepartmentModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department1 = Department.objects.create(department="CSS")
        Department.objects.create(department="CEA")

        patient = User.objects.create(
            department=cls.department1, email="sample@test.com", password="12345678"
        )
        User.objects.create(
            department=cls.department1, email="sample@test.com12", password="12345678"
        )

        staff = User.objects.create(email="sample@test.com2", password="12345678")

        User.objects.create(email="sample@test.com3", password="12345678")

        Illness.objects.create(
            patient=patient,
            issue="Sample Issue",
            staff=staff,
        )
        Illness.objects.create(
            patient=patient,
            issue="Sample Issue",
            staff=staff,
        )

    def test_department_data_count(self):
        departments = Department.objects.all()
        expected = 2
        output = departments.count()
        err_msg = "Department data fetched was not equal"
        self.assertEqual(expected, output, err_msg)

    def test_user_to_department(self):
        user = User.objects.get(pk=1)
        expected = "CSS"
        output = user.department.department
        err_msg = "Expected user department was not attached"
        self.assertEqual(expected, output, err_msg)

    def test_department_to_illness(self):
        last_visit = (
            Illness.objects.filter(patient=OuterRef("pk"))
            .exclude(added__isnull=True)
            .order_by("-added")
            .values("added")
        )

        # Annotate the departments with the last visit date of any patient in that department
        departments = (
            Department.objects.annotate(
                last_visit=Subquery(
                    User.objects.filter(department=OuterRef("pk"))
                    .annotate(
                        last_visit=Coalesce(
                            Subquery(last_visit[:1]),
                            Value(None),
                            output_field=CharField(),
                        )
                    )
                    .exclude(last_visit__isnull=True)
                    .values(
                        "last_visit"
                    )  # Only get the last visit of the first patient in the department
                ),
                count=Count("department"),
            )
            .distinct()
            .values()
        )
        # for data in departments:
        #     if data['last_visit']:
        #         data['last_visit'] = data['last_visit'].isoformat()
        print(json.dumps(list(departments), indent=4, sort_keys=True))
        expect = "CEA"
        output = departments[1]["department"]
        err_msg = "Fetch instance was incorrect"
        self.assertEqual(expect, output, err_msg)


class TestUserModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department1 = Department.objects.create(department="CSS")
        cls.department2 = Department.objects.create(department="COE")
        cls.patient1 = User.objects.create(
            email="test@example.com1",
            password="12345678",
            access=1,
            department=cls.department1,
        )
        cls.patient2 = User.objects.create(
            email="test@example.com11",
            password="12345678",
            access=1,
            department=cls.department2,
        )
        cls.staff1 = User.objects.create(
            email="test@example.com2", password="12345678", access=2
        )
        User.objects.create(email="test@example.com22", password="12345678", access=2)
        cls.doctor1 = User.objects.create(
            email="test@example.com3", password="12345678", access=3
        )
        Illness.objects.create(
            patient=cls.patient1, issue="Issue 1", staff=cls.staff1, doctor=cls.doctor1
        )
        Illness.objects.create(
            patient=cls.patient2, issue="Issue 2", staff=cls.staff1, doctor=cls.doctor1
        )

    def test_staff_illness_cases_handled(self):
        cases = (
            Illness.objects.filter(staff=OuterRef("pk"))
            .order_by("-updated")
            .values("updated")[:1]
        )
        users = (
            User.objects.filter(access__gte=2, access__lte=3)
            .annotate(
                last_case=Coalesce(
                    Subquery(cases), Value(None), output_field=DateTimeField()
                )
            )
            .values()
        )
        for user in users:
            if user["DOB"]:
                user["DOB"] = user["DOB"].isoformat()
            if user["last_case"]:
                user["last_case"] = user["last_case"].isoformat()
            if user["date_joined"]:
                user["date_joined"] = user["date_joined"].isoformat()

        # print(json.dumps(list(cases), indent=4, sort_keys=True))
        print(json.dumps(list(users), indent=4, sort_keys=True))
