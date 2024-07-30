from django.test import TestCase, override_settings
from django.urls import reverse
from django.db.models import Q, Count, Prefetch
from datetime import time
from django.utils import timezone
from collections import defaultdict
from django.db import connection

from users.models import User, Department
from treatment.models import Illness, Category, IllnessTreatment, DoctorDetail
from inventory.models import InventoryDetail, QuantityHistory
from blood.models import BloodPressure


# Create your tests here.
@override_settings(DEBUG=True)
class DashboardTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department1 = Department.objects.create(department="CCS")
        cls.department2 = Department.objects.create(department="Clinic")

        cls.user = User.objects.create(
            first_name="Charles",
            last_name="Bercasio",
            email="bercasiocharles@gmail.com",
            year=4,
            section="A",
            program="Bachelor of Science Major in Information Technology",
            department=cls.department1,
        )

        cls.staff = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="johndoe@gmail.com",
            department=cls.department2,
        )

        cls.doctor = User.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="janesmith@gmail.com",
            department=cls.department2,
        )

        cls.inventory = InventoryDetail.objects.create(
            item_no=1001,
            unit="pcs.",
            item_name="Paracetamol",
            description="Para sa sakit ng ulo",
            added_by=cls.staff,
        )

        cls.quantity1 = QuantityHistory.objects.create(
            inventory=cls.inventory, updated_quantity=100, changed_by=cls.staff
        )

        cls.category1 = Category.objects.create(category="Flu")

        cls.category2 = Category.objects.create(category="Hika")

        cls.illness1 = Illness.objects.create(
            patient=cls.user,
            issue="Marami",
            illness_category=cls.category1,
            staff=cls.staff,
        )

        cls.illness2 = Illness.objects.create(
            patient=cls.user,
            issue="Maraming marami",
            illness_category=cls.category1,
            staff=cls.staff,
            doctor=cls.doctor,
            diagnosis="May sakit",
        )

        cls.illness3 = Illness.objects.create(
            patient=cls.user,
            issue="Maraming marami",
            illness_category=cls.category2,
            staff=cls.staff,
            doctor=cls.doctor,
            diagnosis="May sakit",
        )

        cls.treatment2 = IllnessTreatment.objects.create(
            illness=cls.illness2, inventory_detail=cls.inventory, quantity=10
        )

        cls.quantity2 = QuantityHistory.objects.create(
            inventory=cls.treatment2.inventory_detail,
            updated_quantity=-10,
            changed_by=cls.treatment2.illness.doctor,
        )

        cls.availability1 = DoctorDetail.objects.create(doctor=cls.doctor, avail=False)

        cls.availability2 = DoctorDetail.objects.create(
            doctor=cls.user,
            time_avail_start=time(9, 30),
            time_avail_end=time(23, 0),
            avail=True,
        )

        cls.blood1 = BloodPressure.objects.create(patient=cls.user, blood_pressure=100)

    # def test_dashboard_status_code(self):
    #     response = self.client.get('/patient/')
    #     self.assertEqual(response.status_code, 200)

    # def test_dashboard_url_name(self):
    #     response = self.client.get(reverse('patient-home'))
    #     self.assertEqual(response.status_code, 200)

    # def test_template(self):
    #     response = self.client.get(reverse('patient-home'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'patient/overview.html')

    def test_number_of_users(self):
        users = User.objects.all().count() or 0
        self.assertEqual(users, 3)

    def test_user_illness_all(self):
        user_illness = Illness.objects.filter(patient=self.user).count() or 0
        self.assertEqual(user_illness, 3)

    def test_user_illness_no_diagnosis(self):
        user_illness = (
            Illness.objects.filter(patient=self.user, diagnosis="").count() or 0
        )
        self.assertEqual(user_illness, 1)

    def test_user_illness_has_diagnosis(self):
        user_illness = (
            Illness.objects.filter(patient=self.user, diagnosis__gt="").count() or 0
        )
        self.assertEqual(user_illness, 2)

    def test_illness_not_existing_user(self):
        user_illness = (
            Illness.objects.filter(patient=self.doctor, diagnosis__gt="").count() or 0
        )
        self.assertEqual(user_illness, 0)

    def test_initial_quantity(self):
        quantity = QuantityHistory.objects.filter(inventory_id=1)
        count = 0
        for quan in quantity:
            count += quan.updated_quantity
        self.assertEqual(count, 90)

    def test_update_diagnosis_check_quantity(self):
        illness = Illness.objects.get(id=self.illness1.id)
        illness.diagnosis = "May ubo ka"
        illness.save()

        treatment = IllnessTreatment.objects.create(
            illness=illness, inventory_detail=self.inventory, quantity=10
        )

        quantity = QuantityHistory.objects.create(
            inventory=treatment.inventory_detail,
            updated_quantity=-treatment.quantity,
            changed_by=self.doctor,
        )

        quantities = QuantityHistory.objects.filter(inventory=quantity.inventory)

        count = 0
        for quan in quantities:
            count += quan.updated_quantity

        self.assertEqual(count, 80)

    def test_doctor_is_avail(self):
        doctor = DoctorDetail.objects.select_related("doctor")
        for doc in doctor:
            now = timezone.localtime().time()
            is_avail = doc.is_avail(now)
            setattr(doc, "true_avail", is_avail)
        self.assertFalse(doctor[0].true_avail)
        self.assertTrue(doctor[1].true_avail)

    def test_user_illness_count_per_category(self):
        email = "bercasiocharles@gmail.com"
        user = User.objects.get(email=email)

        illness_count = defaultdict(int)

        categories = Category.objects.annotate(
            illness_count=Count(
                "illness_category",
                filter=Q(
                    illness_category__patient=user,
                ),
            )
        ).filter(illness_count__gt=0)

        for category in categories:
            illness_count[category.category] = category.illness_count or 0

        expected = {"Flu": 2, "Hika": 1}

        self.assertDictEqual(dict(illness_count), expected)

    def test_illness_to_illness_treatment_to_inventory(self):
        connection.queries.clear()
        treatment = Illness.objects.prefetch_related(
            Prefetch(
                "illnesstreatment_set",
                queryset=IllnessTreatment.objects.select_related("inventory_detail"),
            )
        )

        # Force evaluation of the queryset
        treatments_list = list(treatment)

        # Print the QuerySet
        # print("QuerySet:", treatments_list)

        # Print the SQL query of the treatment queryset
        # print("Query (treatment.query):", str(treatment.query))

        for t in treatment:
            print(t.patient)
            for detail in t.illnesstreatment_set.all():
                print(detail.inventory_detail)
                print(detail.quantity)

        print(connection.queries)

        self.assertIsNotNone(treatment)

    def test_user_to_blood_pressure(self):
        user = User.objects.prefetch_related("blood_pressures").get(
            email="bercasiocharles@gmail.com"
        )

        blood_pressure = user.blood_pressures.first()
        expected = 100

        self.assertEqual(blood_pressure.blood_pressure, expected)
