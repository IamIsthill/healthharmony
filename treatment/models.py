from django.db import models
from users.models import User

# Create your models here.
class DoctorDetail(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    avail = models.BooleanField()

class Category(models.Model):
    category = models.CharField(max_length=20, null=True, blank=True)
    added = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category


class Illness(models.Model):
    patient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="patient_illness")
    issue = models.TextField()
    illness_category = models.ForeignKey(Category, related_name="illness_category", on_delete=models.SET_NULL, blank=True, null=True)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="staff_illness", blank=True)
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="doctor_illness", blank=True)
    added = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'{self.patient} - {self.issue[0:30]}'
    
class Certificate(models.Model):
    patient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    purpose = models.TextField()
    requested = models.DateTimeField(auto_now=True)
    released = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.patient} on {self.requested}'
    
