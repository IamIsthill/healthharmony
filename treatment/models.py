from django.db import models
from users.models import User

# Create your models here.
class DoctorDetail(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    avail = models.BooleanField()
