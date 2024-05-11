from django.db import models

# Create your models here.
class BedStat(models.Model):
    status = models.BooleanField(default=False)
