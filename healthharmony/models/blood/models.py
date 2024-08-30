from django.db import models
from healthharmony.users.models import User

# Create your models here.


class BloodPressure(models.Model):
    patient = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="blood_pressures"
    )
    blood_pressure = models.SmallIntegerField(null=True)
    added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.patient.email if self.patient else "Unknown"} - {self.blood_pressure}'

    class Meta:
        ordering = ["-added"]
