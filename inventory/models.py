from django.db import models

# Create your models here.
class InventoryDetail(models.Model):
    item_no = models.SmallIntegerField(default=None)
    unit = models.CharField(max_length=100, null=True)
    item_name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    expiration_date= models.DateField(default=None)

    def __str__(self):
        return self.item_name
    
class QuantityHistory(models.Model):
    inventory = models.ForeignKey(InventoryDetail, on_delete=models.SET_NULL, null=True)
    less = models.PositiveIntegerField(null=False)
    timestamp = models.DateTimeField(auto_created=True)

    def __str__(self):
        view = f'{self.inventory.item_name} - {self.less}'
        return view