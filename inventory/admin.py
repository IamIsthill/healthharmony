from django.contrib import admin
from inventory.models import InventoryDetail, QuantityHistory
# Register your models here.
admin.site.register(InventoryDetail)
admin.site.register(QuantityHistory)
