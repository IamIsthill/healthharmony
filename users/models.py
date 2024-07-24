from django.db import models
from django.contrib.auth.models import AbstractUser
from users.manager import UserManager

# Create your models here.


class Department(models.Model):
    department = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.department
    
class User(AbstractUser):
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, unique=True)
    profile = models.ImageField(default="fallback.png", blank=True)
    year = models.SmallIntegerField(null=True, blank=True)
    section = models.CharField(max_length=10, null=True, blank=True)
    program = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(Department, related_name='user_department', blank=True, null=True, on_delete=models.SET_NULL)
    access = models.IntegerField(default=1, null=True, blank=True)
    DOB = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=20, null=True, blank=True)
    blood_type = models.CharField(max_length=20, null=True, blank=True)
    height = models.SmallIntegerField(null=True, blank=True)
    weight = models.SmallIntegerField(null=True, blank=True)
    username = None
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]
    

    objects = UserManager()

    def __str__(self):
        return f'{self.id} : {self.email}' or 'Unnamed User'
    
    class Meta:
        ordering = ['-date_joined']
    
