from django.db import models

# Create your models here.
class Activity(models.Model):
    title = models.TextField()
    date = models.DateField( auto_now=False, null=True)
    time = models.TimeField( auto_now=False)
    status = models.CharField(max_length=50, default='Pending')
    types = models.CharField( max_length=50)
    msg = models.TextField()