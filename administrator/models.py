from django.db import models
from users.models import User

# Create your models here.
class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL , null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.action}'
    
    class Meta:
        ordering = ['-timestamp']
