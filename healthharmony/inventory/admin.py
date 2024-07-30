from django.contrib import admin
from healthharmony.inventory.models import InventoryDetail, QuantityHistory
# Register your models here.
admin.site.register(InventoryDetail)
admin.site.register(QuantityHistory)
