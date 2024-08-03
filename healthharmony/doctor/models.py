from django.db import models


# Create your models here.
class ModelLog(models.Model):
    model_name = models.CharField(max_length=30, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model_name
