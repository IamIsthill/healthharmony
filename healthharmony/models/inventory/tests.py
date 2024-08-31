from django.test import TestCase
from django.db.models import Sum
from django.core.exceptions import ValidationError

from healthharmony.models.inventory.models import InventoryDetail, QuantityHistory
from healthharmony.users.models import User


# Create your tests here.
class InventoryTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            first_name="Charles", email="bercasiocharles@gmail.com", password="1232232"
        )

        # Create an inventory item
        self.inventory_item = InventoryDetail.objects.create(
            item_no=1,
            unit="Box",
            item_name="Paracetamol",
            category="Medicine",
            description="Pain reliever",
            expiration_date="2024-12-31",
            added_by=self.user,
        )

        # Create a quantity history for the inventory item
        self.quantity_history = QuantityHistory.objects.create(
            inventory=self.inventory_item, updated_quantity=50, changed_by=self.user
        )

        self.quantity2 = QuantityHistory.objects.create(
            inventory=self.inventory_item, updated_quantity=200, changed_by=self.user
        )

    def test_inventory_detail_creation(self):
        self.assertEqual(self.inventory_item.item_name, "Paracetamol")
        self.assertEqual(self.inventory_item.category, "Medicine")
        self.assertEqual(self.inventory_item.added_by.first_name, "Charles")

    def test_quantity_history_creation(self):
        self.assertEqual(self.quantity_history.inventory.item_name, "Paracetamol")
        self.assertEqual(self.quantity_history.updated_quantity, 50)
        self.assertEqual(self.quantity_history.changed_by.first_name, "Charles")

    def test_inventory_string_representation(self):
        self.assertEqual(str(self.inventory_item), "Paracetamol")

    def test_quantity_history_string_representation(self):
        self.assertEqual(str(self.quantity_history), "Paracetamol - 50")

    def test_inventory_category_default(self):
        inventory_item = InventoryDetail.objects.create(
            item_name="Bandages", added_by=self.user
        )
        self.assertEqual(inventory_item.category, "Medicine")

    def test_quantity_history_related_name(self):
        self.assertEqual(self.inventory_item.quantities.first(), self.quantity_history)

    def test_quantity_(self):
        inventory = (
            InventoryDetail.objects.filter(id=1)
            .annotate(quantity=Sum("quantities__updated_quantity"))
            .first()
        )
        self.assertEqual(int(inventory.quantity), 250)

    def test_invalid_category(self):
        with self.assertRaises(ValidationError):
            inventory = InventoryDetail(
                item_name="Juan",
                category="Not Category",  # Invalid category
                added_by=self.user,
            )
            inventory.full_clean()  # This triggers validation
            inventory.save()

        # Create InventoryDetail with no category specified to use the default
        inventory = InventoryDetail.objects.create(item_name="Juan", added_by=self.user)
        self.assertEqual(inventory.category, "Medicine")  # Default value check
