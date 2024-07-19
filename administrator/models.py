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


    

class DataChangeLog(models.Model):
    ACTIONS = [
        ('Create', 'Create'),
        ('Update', 'Update'),
        ('Delete', 'Delete'),
    ]
    table = models.CharField(max_length=255)
    record_id = models.IntegerField()
    action = models.CharField(max_length=10, choices=ACTIONS)  
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Change in {self.table} - {self.action} by {self.changed_by} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']

