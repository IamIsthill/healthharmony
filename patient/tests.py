from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.db.models import Q

from bed.models import BedStat
from users.models import User, Department
from treatment.models import Illness, Category, IllnessTreatment
from inventory.models import InventoryDetail, QuantityHistory


# Create your tests here.
class DashboardTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.department1 = Department.objects.create(
            department = 'CCS'
        )
        cls.department2 = Department.objects.create(
            department = 'Clinic'
        )

        cls.user = User.objects.create(
            first_name = 'Charles',
            last_name = 'Bercasio',
            email = 'bercasiocharles@gmail.com',
            year = 4,
            section = 'A',
            program = 'Bachelor of Science Major in Information Technology',
            department = cls.department1
        )

        cls.staff = User.objects.create(
            first_name='John',
            last_name='Doe',
            email='johndoe@gmail.com',
            department=cls.department2
        )

        cls.doctor = User.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='janesmith@gmail.com',
            department=cls.department2
        )


        cls.inventory = InventoryDetail.objects.create(
            item_no = 1001,
            unit = 'pcs.',
            item_name = 'Paracetamol',
            description = 'Para sa sakit ng ulo',
            added_by = cls.staff
        )

        cls.quantity1 = QuantityHistory.objects.create(
            inventory = cls.inventory,
            updated_quantity = 100,
            changed_by = cls.staff
        )

        cls.category = Category.objects.create(
            category='Flu'
        )

        cls.illness1 = Illness.objects.create(
            patient = cls.user,
            issue = 'Marami',
            illness_category = cls.category,
            staff = cls.staff
        )

        cls.illness2 = Illness.objects.create(
            patient = cls.user,
            issue = 'Maraming marami',
            illness_category = cls.category,
            staff = cls.staff,
            doctor = cls.doctor,
            diagnosis = 'May sakit'
        )

        cls.treatment2 = IllnessTreatment.objects.create(
            illness = cls.illness2,
            inventory_detail = cls.inventory,
            quantity = 10
        )

        cls.quantity2 = QuantityHistory.objects.create(
            inventory = cls.treatment2.inventory_detail,
            updated_quantity = -10,
            changed_by = cls.treatment2.illness.doctor
        )

    def test_dashboard_status_code(self):
        response = self.client.get('/patient/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_url_name(self):
        response = self.client.get(reverse('patient-home'))
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get(reverse('patient-home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patient/overview.html')

    def test_number_of_users(self):
        users = User.objects.all().count() or 0
        self.assertEqual(users, 3)

    def test_user_illness_all(self):
        user_illness = Illness.objects.filter(patient = self.user).count() or 0
        self.assertEqual(user_illness, 2)

    def test_user_illness_no_diagnosis(self):
        user_illness = Illness.objects.filter(patient = self.user, diagnosis = '').count() or 0
        self.assertEqual(user_illness, 1)

    def test_user_illness_has_diagnosis(self):
        user_illness = Illness.objects.filter(patient = self.user, diagnosis__gt = '').count() or 0
        self.assertEqual(user_illness, 1)

    def test_illness_not_existing_user(self):
        user_illness = Illness.objects.filter(patient = self.doctor, diagnosis__gt = '').count() or 0
        self.assertEqual(user_illness, 0)
    
    def test_initial_quantity(self):
        quantity = QuantityHistory.objects.filter(inventory_id = 1)
        count = 0
        for quan in quantity:
            count += quan.updated_quantity
        self.assertEqual(count, 90)

    def test_update_diagnosis_check_quantity(self):
        illness = Illness.objects.get(id=self.illness1.id)
        illness.diagnosis = 'May ubo ka'
        illness.save()

        treatment = IllnessTreatment.objects.create(
            illness = illness,
            inventory_detail = self.inventory,
            quantity = 10
        )

        quantity = QuantityHistory.objects.create(
            inventory = treatment.inventory_detail,
            updated_quantity = -treatment.quantity,
            changed_by = self.doctor
        )

        quantities = QuantityHistory.objects.filter(inventory = quantity.inventory)

        count = 0
        for quan in quantities:
            count += quan.updated_quantity

        self.assertEqual(count, 80)