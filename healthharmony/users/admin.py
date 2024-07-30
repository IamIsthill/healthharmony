from django.contrib import admin
from .models import User
from . import models

# Register your models here.
admin.site.register(User)
admin.site.register(models.Department)
