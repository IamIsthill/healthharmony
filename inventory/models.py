from django.db import models

# Create your models here.
class Inventory(models.Model):
    item_no = models.BigAutoField(primary_key=True)
    unit = models.CharField(max_length=100, blank=True, )
    item_name = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)
    expiration_date=models.DateField(default=None)
    quantity = models.PositiveIntegerField(blank=False)

    def __str__(self):
        return self.item_name