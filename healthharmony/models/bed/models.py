from django.db import models


# Create your models here.
class BedStat(models.Model):
    status = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f'Bed {self.id} - Status: {"Occupied" if self.status else "Available"}'
