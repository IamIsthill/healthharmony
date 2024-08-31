from django.db import models


class Models(models.Model):
    model_file = models.BinaryField()
    time_added = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.model_name}"


class ModelLog(models.Model):
    model_name = models.ForeignKey(Models, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model_name

    class Meta:
        ordering = ["-update_time"]
