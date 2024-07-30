from django.db import models
from django.contrib.auth.models import AbstractUser
from healthharmony.users.manager import UserManager
import os
from uuid import uuid4

# Create your models here.


def user_profile_path(instance, filename):
    # Generate a unique filename using uuid4
    ext = filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return os.path.join("user_profiles", f"user_{instance.id}", filename)


class Department(models.Model):
    department = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.department


class User(AbstractUser):
    first_name = models.CharField(
        max_length=200, null=True, blank=True, default="First Name"
    )
    last_name = models.CharField(
        max_length=200, null=True, blank=True, default="Last Name"
    )
    email = models.EmailField(null=True, unique=True)
    contact = models.IntegerField(null=True, blank=True)
    profile = models.ImageField(
        upload_to=user_profile_path, default="user_profiles/fallback.png", blank=True
    )
    year = models.SmallIntegerField(null=True, blank=True)
    section = models.CharField(max_length=10, null=True, blank=True)
    program = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(
        Department,
        related_name="user_department",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    access = models.IntegerField(default=1, null=True, blank=True)
    DOB = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=20, null=True, blank=True)
    blood_type = models.CharField(max_length=20, null=True, blank=True)
    height = models.SmallIntegerField(null=True, blank=True)
    weight = models.SmallIntegerField(null=True, blank=True)
    username = None
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.id} : {self.email}" or "Unnamed User"

    class Meta:
        ordering = ["-date_joined"]
