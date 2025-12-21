
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from .models import Applicants, DataEntryPeriod,Limit
from app.main.models import Barangay
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages 
from app.employee.models import Employee
# Create your views here.

def is_hrmo(user):
    # print(user.id)
    if user.is_superuser:
        return True
    
    role = Employee.objects.select_related("department").get(user_id = user.id)
    
    if role.department.abbreviation == 'MHRMO':
        return True
    
   
    return False

@login_required
@user_passes_test(is_hrmo,login_url='/')

def view(request):
    applicant = Applicants.objects.all()      
    return render(request,'view_admin.html',{"active":'education',"applicants":applicant})


@login_required
@user_passes_test(is_hrmo,login_url='/')
def store(request):
    brgys = Barangay.objects.all()      
      # **ALWAYS FRESH CHECKS - RUN EVERY TIME**
    total_apps = Applicants.objects.count()
    current_date = timezone.now().date()
    brgy = Barangay.objects.all()
    # Get active period
    try:
        active_period = DataEntryPeriod.objects.get(is_active=True)
    except DataEntryPeriod.DoesNotExist:
        active_period = None

    # **1. DATE CHECK**
    if not active_period or not (active_period.open_date <= current_date <= active_period.close_date):
        return render(request, "applicant/create_applicant.html", {"display": "closed","brgys":brgy})


    # **3. FORM HANDLING**
    if request.method == 'POST':
        return _handle_post1(request, active_period)
    else:
        return render(request,'applicant/create_applicant.html',{"active":'education',"brgys":brgys})



def create(request):
    # **ALWAYS FRESH CHECKS - RUN EVERY TIME**
    total_apps = Applicants.objects.count()
    current_date = timezone.now().date()
    brgy = Barangay.objects.all()
    # Get active period
    try:
        active_period = DataEntryPeriod.objects.get(is_active=True)
    except DataEntryPeriod.DoesNotExist:
        active_period = None

    # **1. DATE CHECK**
    if not active_period or not (active_period.open_date <= current_date <= active_period.close_date):
        return render(request, "applicant/applicant.html", {"display": "closed","brgys":brgy})

    # **2. APPLICATION LIMIT CHECK (ALWAYS FRESH)**
    max_applicant = Limit.objects.get(id=1).limit_number
        # **CRITICAL: CHECK IF SLOTS FULL NOW**

    # **3. FORM HANDLING**
    if request.method == 'POST':
        return _handle_post(request, active_period)
    else:
        return render(request, "applicant/applicant.html", {
            "display": "open", 
            "count": total_apps,"brgys":brgy
        })


def _handle_post(request, active_period):
    """Handle POST - Always check slots FRESH"""
    
    # **FRESH SLOT CHECK - CRITICAL!**
    total_apps = Applicants.objects.count()
    max_applicant = Limit.objects.get(id=1).limit_number
        # **CRITICAL: CHECK IF SLOTS FULL NOW**
    brgy = Barangay.objects.all()

    # Extract form data
    form_data = {
        'fName': request.POST.get("fname", "").strip(),
        'mName': request.POST.get("mname", "").strip(),
        'lName': request.POST.get("lname", "").strip(),
        'email': request.POST.get("email", "").strip().lower(),
        'contact': request.POST.get("contact", "").strip(),
        'grade': request.POST.get("grade", "").strip(),
        'school': request.POST.get("school", "").strip(),
        'province': request.POST.get("province", "").strip(),
        'name_ext': request.POST.get("name_ext", "").strip(),
        'brgy': request.POST.get("brgy", "").strip(),
        'purok': request.POST.get("purok", "").strip(),
        'is_four': request.POST.get("is_four", "").strip(),
    }
    
    # Validation
    errors = _validate_form(form_data)
    
    # Duplicate check
    if not errors:
        errors = _check_duplicates(form_data)
    
    # Errors
    if errors:
        return render(request, "applicant/applicant.html", {
            "display": "open",
            "count": total_apps,
            **form_data,
            "errors": errors,"brgys":brgy
        })
    
    # **SUCCESS - SAVE & CHECK SLOTS AGAIN**
    return _save_and_check_slots(request, form_data, active_period)

def _handle_post1(request, active_period):
    """Handle POST - Always check slots FRESH"""
    
    # **FRESH SLOT CHECK - CRITICAL!**
    total_apps = Applicants.objects.count()
    max_applicant = Limit.objects.get(id=1).limit_number
        # **CRITICAL: CHECK IF SLOTS FULL NOW**
    brgy = Barangay.objects.all()

    # Extract form data
    form_data = {
        'fName': request.POST.get("fname", "").strip(),
        'mName': request.POST.get("mname", "").strip(),
        'lName': request.POST.get("lname", "").strip(),
        'email': request.POST.get("email", "").strip().lower(),
        'contact': request.POST.get("contact", "").strip(),
        'grade': request.POST.get("grade", "").strip(),
        'school': request.POST.get("school", "").strip(),
        'province': request.POST.get("province", "").strip(),
        'name_ext': request.POST.get("name_ext", "").strip(),
        'brgy': request.POST.get("brgy", "").strip(),
        'purok': request.POST.get("purok", "").strip(),
        'is_four': request.POST.get("is_four", "").strip(),
    }
    
    # Validation
    errors = _validate_form(form_data)
    
    # Duplicate check
    if not errors:
        errors = _check_duplicates(form_data)
    
    # Errors
    if errors:
        return render(request, "applicant/create_applicant.html", {
            "display": "open",
            "count": total_apps,
            **form_data,
            "errors": errors,"brgys":brgy
        })
    
    # **SUCCESS - SAVE & CHECK SLOTS AGAIN**
    return _save_and_check_slots1(request, form_data, active_period)


def _validate_form(form_data):
    """Validation logic"""
    errors = {}
    
    if not form_data['fName']: errors["fName"] = "First Name is Required."
    if not form_data['lName']: errors["lName"] = "Last Name is Required."
    if not form_data['email']: 
        errors["email"] = "Email is Required."
    elif Applicants.objects.filter(email=form_data['email']).exists():
        errors["email"] = "The email must be unique."
    if not form_data['contact']: 
        errors["contact"] = "Contact Number is Required."
    elif not form_data['contact'].isdigit():
        errors["contact"] = "Contact Number must be a valid number (only digits)."
    if not form_data['grade']: errors["grade"] = "Grade/Level is Required."
    if not form_data['school']: errors["school"] = "School Name is Required."
    
    if not form_data['province']: errors["province"] = "Province is Required."
    if not form_data['brgy']: errors["brgy"] = "Barangay is Required."
    if not form_data['purok']: errors["purok"] = "Purok is Required."
    if not form_data['is_four']: errors["is_four"] = "Please Select a Value."
    
    return errors


def _check_duplicates(form_data):
    """Duplicate check"""
    errors = {}
    
    if form_data['mName']:
        applicant = Applicants.objects.filter(
            first_name__iexact=form_data['fName'],
            middle_name__icontains=form_data['mName'],
            last_name__iexact=form_data['lName']
        ).first()
    else:
        applicant = Applicants.objects.filter(
            first_name__iexact=form_data['fName'],
            last_name__iexact=form_data['lName']
        ).first()
    
    if applicant:
        errors["datas"] = "Sorry! Your Data is already in the System!"
    
    return errors


def _save_and_check_slots(request, form_data, active_period):
    """SAVE + IMMEDIATE SLOT CHECK"""
    try:
        with transaction.atomic():
            # CREATE APPLICANT
            school_id = Applicants.objects.count()
            year = timezone.now().year
            school = f"{year}00{school_id+1}"
            applicant = Applicants.objects.create(
                first_name=form_data['fName'],
                middle_name=form_data['mName'],
                last_name=form_data['lName'],
                name_ext=form_data['name_ext'],
                email=form_data['email'],
                contact=form_data['contact'],
                grade=form_data['grade'],
                school=form_data['school'],
                province=form_data['province'],
                brgy_id=form_data['brgy'],
                purok=form_data['purok'],
                is_four = form_data['is_four'],
                scholar_id = school 
            )
        
        # **FRESH COUNT AFTER SAVE**
        total_apps = Applicants.objects.count()
        max_applicant = Limit.objects.get(id=1).limit_number
        brgy = Barangay.objects.all()
        # **SUCCESS - SHOW SUCCESS IN SAME PAGE**
        context = {
            'display': 'open',
            'success': True,
            'applicant_id': applicant.id,  # ✅ FIXED: REAL ID
            'full_name': f"{form_data['fName']} {form_data['mName']} {form_data['lName']}".strip(),
            'email': form_data['email'],
            'total_apps': total_apps,
            'count': total_apps,
            'open_date': active_period.open_date,
            'close_date': active_period.close_date,
            "first_name":"",
            "middle_name":"",
            "last_name":"",
            "email":"",
            "contact":"",
            "grade":"",
            "school":"",
            "province": "",
            "name_ext": "",
            "brgy": "",
            "purok":"",
            "is_four":""
        }
        return redirect("education:receipt",id=school)
        
    except Exception as e:
        print(f"Error: {e}")
        total_apps = Applicants.objects.count()
        errors = {"general": "An error occurred. Please try again."}
        return render(request, "applicant/applicant.html", {
            "display": "open",
            "count": total_apps,
            **form_data,
            "errors": errors,
            "brgys":brgy
        })



def _save_and_check_slots1(request, form_data, active_period):
    """SAVE + IMMEDIATE SLOT CHECK"""
    try:
        with transaction.atomic():
            # CREATE APPLICANT
            school_id = Applicants.objects.count()
            year = timezone.now().year
            school = f"{year}00{school_id+1}"
            applicant = Applicants.objects.create(
                first_name=form_data['fName'],
                middle_name=form_data['mName'],
                last_name=form_data['lName'],
                name_ext=form_data['name_ext'],
                email=form_data['email'],
                contact=form_data['contact'],
                grade=form_data['grade'],
                school=form_data['school'],
                province=form_data['province'],
                brgy_id=form_data['brgy'],
                purok=form_data['purok'],
                is_four = form_data['is_four'],
                scholar_id = school 
            )
        
        # **FRESH COUNT AFTER SAVE**
        total_apps = Applicants.objects.count()
        max_applicant = Limit.objects.get(id=1).limit_number
        brgy = Barangay.objects.all()
        # **SUCCESS - SHOW SUCCESS IN SAME PAGE**
        context = {
            'display': 'open',
            'success': True,
            'applicant_id': applicant.id,  # ✅ FIXED: REAL ID
            'full_name': f"{form_data['fName']} {form_data['mName']} {form_data['lName']}".strip(),
            'email': form_data['email'],
            'total_apps': total_apps,
            'count': total_apps,
            'open_date': active_period.open_date,
            'close_date': active_period.close_date,
            "first_name":"",
            "middle_name":"",
            "last_name":"",
            "email":"",
            "contact":"",
            "grade":"",
            "school":"",
            "province": "",
            "name_ext": "",
            "brgy": "",
            "purok":"",
            "is_four":""
        }
        messages.success(request,"Scholar Applicant Created Successfully!")
        return redirect("education:view")
        
    except Exception as e:
        print(f"Error: {e}")
        total_apps = Applicants.objects.count()
        errors = {"general": "An error occurred. Please try again."}
        return render(request, "applicant/create_applicant.html", {
            "display": "open",
            "count": total_apps,
            **form_data,
            "errors": errors,
            "brgys":brgy
        })



def receipt(request,id):
    app = Applicants.objects.get(scholar_id=id)
    context = {
        "data":app
    }
    return render(request,"applicant/receipt.html",context)