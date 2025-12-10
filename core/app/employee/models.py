from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    abbreviation = models.CharField(max_length=20, blank=True, null=True)
    


class Position(models.Model):
    title = models.CharField(max_length=200)
    salary_grade = models.PositiveSmallIntegerField(null=True, blank=True)
    salary = models.IntegerField(null=True, blank=True)
    

        
# Create your models here.
class Employee(models.Model):
    last_name = models.TextField(max_length=250)
    first_name = models.TextField(max_length=250)
    middle_name = models.TextField(max_length=200,null=True)
    name_ext = models.TextField(max_length=200,blank=True,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    mobile = models.CharField(max_length=15, null=True)
    email = models.EmailField(max_length=254)
    role = models.CharField(max_length=254,default='user')
    
    gender = models.CharField(max_length=250,choices=[
        ('M',"Male"),
        ('F',"Female")
    ])
    civil_status = models.CharField(max_length=250,choices=[
        ('Single','Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
        ('Annulled', 'Annulled'),
    ])
    
    date_of_birth = models.DateField()
    place_of_birth = models.TextField()
    
    address = models.TextField()

    tin = models.CharField(max_length=15, blank=True, null=True)
    gsis = models.CharField(max_length=20, blank=True, null=True)
    pagibig = models.CharField(max_length=20, blank=True, null=True)
    philhealth = models.CharField(max_length=20, blank=True, null=True)
    sss = models.CharField(max_length=20, blank=True, null=True)
    
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('Regular', 'Regular Permanent'),
        ('Casual', 'Casual'),
        ('Coterminous', 'Co-terminous'),
        ('Job Order', 'Job Order (JO)'),
        ('Contract of Service', 'Contract of Service (COS)'),
        ('Elective', 'Elective Official'),
        ('Temporary', 'Temporary'),
    ]
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='Casual')
    
    date_hired = models.DateField(null=True,default=None)
    date_regularized = models.DateField(null=True, default=None)
    date_separation = models.DateField(null=True, default=None)

    # Eligibility (CSC)
    has_eligibility = models.BooleanField(default=False)
    eligibility_type = models.CharField(max_length=100, blank=True, null=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,default=0.00)
    date_of_examination = models.DateField(null=True, default=None)

    # Status
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    stat = models.CharField(default="None",max_length=250)
    
    profile_picture = models.ImageField(
        upload_to='employees/profile/',   # where the image will be saved
        blank=True,
        null=True,
        help_text="Employee photo (optional)"
    )
  