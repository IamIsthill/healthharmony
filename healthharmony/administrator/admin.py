from django.contrib import admin
from .models import Log, DataChangeLog

# Register your models here.
admin.site.register(Log)
admin.site.register(DataChangeLog)
