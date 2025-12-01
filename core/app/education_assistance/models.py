from django.db import models


class Applicants(models.Model):
    last_name = models.CharField(max_length=75)
    first_name = models.CharField(max_length=75)
    middle_name = models.CharField(max_length=75)
    email = models.CharField(max_length=75)
    contact = models.CharField(max_length=75)
    grade = models.CharField(max_length=100)
    school = models.TextField()
    address = models.TextField()
    is_four = models.BooleanField(default=False)
    gwa = models.FloatField(default=0.0)
    

class DataEntryPeriod(models.Model):
    open_date = models.DateField('open_date')
    close_date = models.DateField('close_date')
    is_active = models.BooleanField(default=True)


class Limit(models.Model):
    limit_number = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)