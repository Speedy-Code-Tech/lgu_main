from django.db import models
from app.main.models import Barangay

class Applicants(models.Model):
    scholar_id = models.CharField(max_length=250,null=True)
    last_name = models.CharField(max_length=75)
    first_name = models.CharField(max_length=75)
    middle_name = models.CharField(max_length=75)
    name_ext = models.CharField(max_length=75,null=True)
    email = models.CharField(max_length=75)
    contact = models.CharField(max_length=75)
    grade = models.CharField(max_length=100)
    school = models.TextField()
    is_four = models.BooleanField(default=False)
    gwa = models.FloatField(default=0.0)
    province = models.CharField(max_length=250,default="Labo Camarines Norte")
    brgy = models.ForeignKey(Barangay,on_delete=models.CASCADE,null=True)
    purok = models.CharField(max_length=250,null=True)
    
    @property
    def full_name(self):
        name = [self.last_name.strip()]
        name.append(", ")
        if self.first_name:
            name.append(self.first_name.strip())
        if self.middle_name:
            name.append(self.middle_name.strip())
        
        return " ".join(name)
    
    @property
    def full_address(self):
        address = [self.purok.strip()]
        
        if self.brgy.name:
            address.append(self.brgy.name.strip())
        if self.province:
            address.append(self.province.strip())
        
        return " ".join(address)
            

class DataEntryPeriod(models.Model):
    open_date = models.DateField('open_date')
    close_date = models.DateField('close_date')
    is_active = models.BooleanField(default=True)


class Limit(models.Model):
    limit_number = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    
    