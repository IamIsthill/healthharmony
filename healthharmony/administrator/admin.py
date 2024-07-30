from django.contrib import admin
from healthharmony.administrator.models import Log, DataChangeLog

# Register your models here.
admin.site.register(Log)
admin.site.register(DataChangeLog)
