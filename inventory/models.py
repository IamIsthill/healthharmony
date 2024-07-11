from django.db import models

# Create your models here.
class InventoryDetail(models.Model):
    CATEGORY_CHOICES = [
        ('Medicine', 'Medicine'),
        ('Supply', 'Supply'),
    ]
    item_no = models.SmallIntegerField(default=None)
    unit = models.CharField(max_length=50, null=True)
    item_name = models.CharField(max_length=100, null=False)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Medicine')
    description = models.TextField(null=False)
    expiration_date= models.DateField(default=None)

    def __str__(self):
        return self.item_name
    
class QuantityHistory(models.Model):
    inventory = models.ForeignKey(InventoryDetail, on_delete=models.SET_NULL, null=True)
    updated_quantity = models.IntegerField(null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        view = f'{self.inventory.item_name} - {self.updated_quantity}'
        return view