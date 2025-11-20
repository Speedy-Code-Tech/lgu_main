from django.db import models

# Create you
# r models here.
class Venues(models.Model):
    venue = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    

class Events(models.Model):
    event_name = models.CharField(max_length=200)
    from_date = models.DateTimeField(auto_now=False)
    to_date = models.DateTimeField(auto_now=False)
    status = models.CharField(max_length=200)
    coordinator = models.CharField(max_length=200)
    remarks = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    venue = models.ForeignKey(Venues,on_delete=models.CASCADE,
    null=True,
    blank=True)
    
