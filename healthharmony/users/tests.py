from django.test import TestCase
from healthharmony.users.models import Department, User
from healthharmony.treatment.models import Illness, IllnessTreatment
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import OuterRef, Subquery, Value, Sum, F, CharField, DateTimeField
from datetime import datetime
from django.db.models.functions import Coalesce
import json


# Create your tests here.
class TestDepartmentModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        department1 = Department.objects.create(department="CSS")
        Department.objects.create(department="CEA")

        patient = User.objects.create(
            department=department1, email="sample@test.com", password="12345678"
        )
        User.objects.create(
            department=department1, email="sample@test.com12", password="12345678"
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

    # def test_user_to_illness(self):
    #     now = timezone.now()
    #     last_visit = Illness.objects.filter(patient=OuterRef('pk')).order_by('-added').values('added')
    #     user = User.objects.filter(pk=1).annotate(
    #         last_visit = Coalesce (
    #             Subquery(last_visit[:1]), Value(None), output_field = DateTimeField()
    #         )
    #     ).values(
    #         'last_visit'
    #     )
    #     visits = []
    #     for data in user:
    #         data['last_visit'] = data['last_visit'].isoformat()
    #         visits.append(data['last_visit'])
    #     print(json.dumps(list(user), indent=4, sort_keys=True))
    #     user = list(user)
    #     expected = [now.isoformat()]
    #     output = visits
    #     err_msg = 'Expected user department was not attached'
    #     self.assertEqual(expected, output, err_msg)

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
                count=Sum("user_department"),
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
