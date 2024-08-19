from django.db import models
from healthharmony.users.models import User


# Create your models here.
class InventoryDetail(models.Model):
    CATEGORY_CHOICES = [
        ("Medicine", "Medicine"),
        ("Supply", "Supply"),
    ]
    item_no = models.SmallIntegerField(default=None, blank=True, null=True)
    unit = models.CharField(max_length=50, null=True)
    item_name = models.CharField(max_length=100, null=True)
    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default="Medicine", null=True
    )
    description = models.TextField(null=True, blank=True)
    expiration_date = models.DateField(default=None, null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.item_name


class QuantityHistory(models.Model):
    inventory = models.ForeignKey(
        InventoryDetail, on_delete=models.SET_NULL, null=True, related_name="quantities"
    )
    updated_quantity = models.IntegerField(null=True, blank=False)
    timestamp = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        view = f"{self.inventory.item_name} - {self.updated_quantity}"
        return view
