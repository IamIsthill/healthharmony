from django.db import models

# Create your models here.
class BedStat(models.Model):
    status = models.BooleanField(default=False, blank=True)

    def __str__(self):
        bed = f'Bed {self.id}'
        return bed
