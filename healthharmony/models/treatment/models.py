from django.db import models
from healthharmony.users.models import User
from healthharmony.models.inventory.models import InventoryDetail


# Create your models here.
class DoctorDetail(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    time_avail_start = models.TimeField(null=True)
    time_avail_end = models.TimeField(null=True)
    avail = models.BooleanField(default=True)

    def is_avail(self, check_time):
        if self.avail and self.time_avail_start <= check_time <= self.time_avail_end:
            return True
        return False

    def __str__(self):
        return f"Doctor: {self.doctor.email}, Available: {self.avail}"


class Category(models.Model):
    category = models.TextField(max_length=50, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    added = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category


class Illness(models.Model):
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="patient_illness"
    )
    issue = models.TextField()
    illness_category = models.ForeignKey(
        Category,
        related_name="illness_category",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="staff_illness",
        blank=True,
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="doctor_illness",
        blank=True,
    )
    added = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    diagnosis = models.TextField(blank=True, null=True)
    treatment = models.ManyToManyField(InventoryDetail, through="IllnessTreatment")

    def __str__(self):
        return f"{self.patient} - {self.issue[0:30]}"

    class Meta:
        ordering = ["-added"]


class IllnessTreatment(models.Model):
    illness = models.ForeignKey(Illness, on_delete=models.CASCADE)
    inventory_detail = models.ForeignKey(InventoryDetail, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.illness} - {self.inventory_detail} - {self.quantity}"


class Certificate(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    purpose = models.TextField()
    requested = models.DateTimeField(auto_now_add=True)
    is_ready = models.BooleanField(default=False)
    released = models.BooleanField(default=False)

    class Meta:
        ordering = ["-requested"]

    def __str__(self):
        return f"{self.patient} on {self.requested}"


class IllnessNote(models.Model):
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="illness_notes"
    )
    attached_to = models.ForeignKey(Illness, on_delete=models.SET_NULL, null=True)
    notes = models.TextField()
    noted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.notes} by {self.noted_by.email}"
