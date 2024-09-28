from django.db import models


# Create your models here.
class BedStat(models.Model):
    status = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f'Bed {self.id} - Status: {"Occupied" if self.status else "Available"}'


class Ambulansya(models.Model):
    is_avail = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'Ambulance {self.id} - Status {"Available" if self.is_avail else "Occupied"}'
