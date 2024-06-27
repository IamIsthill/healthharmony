from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True, unique=True)
    access = models.CharField(max_length=100,default='patient')
    DOB = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=20, null=True, blank=True)
    blood_type = models.CharField(max_length=20, null=True, blank=True)
    height = models.SmallIntegerField(null=True, blank=True)
    weight = models.SmallIntegerField(null=True, blank=True)
    username = None

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]
    

    objects = UserManager()

    def __str__(self):
        return self.email
