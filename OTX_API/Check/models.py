from django.db import models

# Create your models here.

class ResultModel(models.Model):
    target = models.CharField(max_length=100)
    result_type = models.CharField(max_length=100)
    result_data = models.TextField()
    created = models.DateTimeField(auto_now_add = True)