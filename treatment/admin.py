from django.contrib import admin
from .models import DoctorDetail, Illness, Category
from . import models

# Register your models here.
admin.site.register(DoctorDetail)
admin.site.register(Illness)
admin.site.register(Category)
admin.site.register(models.Certificate)
