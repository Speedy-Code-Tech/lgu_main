from django.db import models
from app.employee.models import Employee,Department
# Create your models here.
class type_of_good(models.Model):
    name = models.CharField( max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)
        
class Mode(models.Model):
    name = models.CharField( max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)
        
class Procurement(models.Model):
    person_responsible = models.ForeignKey(Employee,on_delete=models.CASCADE,null=True)
    purchase_no = models.CharField(max_length=250,null=True)
    date_of_purchase = models.DateField(null=True,auto_now=False)
    end_user = models.ForeignKey(Department,on_delete=models.CASCADE,null=True)
    type_of_good = models.ForeignKey(type_of_good,on_delete=models.CASCADE,null=True) 
    approved_budget = models.BigIntegerField(null=True)
    charging = models.TextField(null=True)
    mode_of_procurement = models.ForeignKey(Mode, on_delete=models.CASCADE,null=True)
    min_of_meeting = models.TextField(null=True)
    bac_resolution = models.CharField(max_length=250,null=True)
    proof_of_service = models.TextField(null=True)
    rfqs = models.CharField(max_length=250,null=True)
    winning_supplier = models.CharField(max_length=250,null=True)
    recommending_award = models.TextField(null=True)
    philgeps = models.TextField(null=True)
    po_number = models.CharField(max_length=250,null=True)
    posting_of_award = models.DateField(auto_now=False,null=True)
    philgeps_reg_no = models.CharField(max_length=250,null=True)
    mayors_no = models.CharField(max_length=250,null=True)
    date_delivery = models.DateField(auto_now=False,null=True)
    date_received = models.DateField(auto_now=False,null=True)
    date_check = models.DateField(auto_now=False,null=True)
    checks = models.CharField(max_length=250,null=True)
    remarks = models.TextField(null=True)
    is_deleted = models.BooleanField(blank=True,default=0)
    
          
    
