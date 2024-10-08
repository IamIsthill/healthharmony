from django.db import models
from healthharmony.users.models import User


# Create your models here.
class BedStat(models.Model):
    status = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f'Bed {self.id} - Status: {"Occupied" if self.status else "Available"}'


class Ambulansya(models.Model):
    is_avail = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'Ambulance {self.id} - Status {"Available" if self.is_avail else "Occupied"}'


class WheelChair(models.Model):
    is_avail = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        status = "Available" if self.is_avail else "Not Available"
        return f"Wheelchairs - {self.quantity} {status}"

    class Meta:
        ordering = ["-updated"]
