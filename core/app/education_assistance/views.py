
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from .models import Applicants, DataEntryPeriod,Limit
from app.main.models import Barangay
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages 
from app.employee.models import Employee
from datetime import date
# Create your views here.

def is_hrmo(user):
    if user.is_superuser:
        return True
    
    role = Employee.objects.select_related("department").get(user_id = user.id)
    
    if role.department.abbreviation == 'MHRMO':
        return True
    
   
    return False

@login_required
@user_passes_test(is_hrmo,login_url='/')

def view(request):
    applicant = Applicants.objects.exclude(status='deleted')
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

  

    # **3. FORM HANDLING**
    if request.method == 'POST':
        return _handle_post1(request)
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
    brgy_value = request.POST.get("brgy")
    if brgy_value and brgy_value.isdigit():
        brgy_id = int(brgy_value)
    else:
        brgy_id = None

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
        'level': request.POST.get("level", "").strip(),
        'brgy': brgy_id,
        'purok': request.POST.get("purok", "").strip(),
        'is_four': request.POST.get("is_four", "").strip(),
        'guardian_fName': request.POST.get("guardian_fname", "").strip(),
        'guardian_mName': request.POST.get("guardian_mname", "").strip(),
        'guardian_lName': request.POST.get("guardian_lname", "").strip(),
        'guardian_name_ext': request.POST.get("guardian_name_ext", "").strip(),
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

def _handle_post1(request):
    """Handle POST - Always check slots FRESH"""
    
    # **FRESH SLOT CHECK - CRITICAL!**
    total_apps = Applicants.objects.count()
    max_applicant = Limit.objects.get(id=1).limit_number
        # **CRITICAL: CHECK IF SLOTS FULL NOW**
    brgy = Barangay.objects.all()
    brgy_value = request.POST.get("brgy")
    if brgy_value and brgy_value.isdigit():
        brgy_id = int(brgy_value)
    else:
        brgy_id = None
   
    # Extract form data
    form_data = {
        'fName': request.POST.get("fname", "").strip(),
        'mName': request.POST.get("mname", "").strip(),
        'lName': request.POST.get("lname", "").strip(),
        'email': request.POST.get("email", "").strip().lower(),
        'contact': request.POST.get("contact", "").strip(),
        'level': request.POST.get("level", "").strip(),
        'grade': request.POST.get("grade", "").strip(),
        'school': request.POST.get("school", "").strip(),
        'province': request.POST.get("province", "").strip(),
        'name_ext': request.POST.get("name_ext", "").strip(),
        'brgy': brgy_id,
        'purok': request.POST.get("purok", "").strip(),
        'is_four': request.POST.get("is_four", "").strip(),
        'guardian_fName': request.POST.get("guardian_fname", "").strip(),
        'guardian_mName': request.POST.get("guardian_mname", "").strip(),
        'guardian_lName': request.POST.get("guardian_lname", "").strip(),
        'guardian_name_ext': request.POST.get("guardian_name_ext", "").strip(),
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
    return _save_and_check_slots1(request, form_data)


def _validate_form(form_data):
    """Validation logic"""
    errors = {}
    
    if not form_data['fName']: errors["fName"] = "First Name is Required."
    if not form_data['lName']: errors["lName"] = "Last Name is Required."

    if not form_data['guardian_fName']: errors["guardian_fName"] = "Guardian First Name is Required."
    if not form_data['guardian_lName']: errors["guardian_lName"] = "Guardian Last Name is Required."
  
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
    if not form_data['level']: errors["level"] = "Level is Required."
  
    return errors


# def _check_duplicates(form_data):
#     """Duplicate check"""
#     errors = {}
    
#     now = timezone.now()
#     today = now.date()
#     current_year = now.year
#     if now.month >= 6:
#         sy_start = date(current_year, 6, 1)
#         sy_end = date(current_year + 1, 5, 31)
#         current_semester_start = date(current_year, 6, 1)
#         current_semester_end = date(current_year, 12, 31)
#     else:
#         sy_start = date(current_year - 1, 6, 1)
#         sy_end = date(current_year, 5, 31)
#         current_semester_start = date(current_year, 1, 1)
#         current_semester_end = date(current_year, 5, 31)

#     # 2. FETCH EXISTING APPLICANTS
#     # We fetch ALL records for this person within the School Year range
#     query_params = {
#         'first_name__iexact': form_data['fName'],
#         'last_name__iexact': form_data['lName'],
#         'date_created__date__range': (sy_start, sy_end)
#     }
#     if form_data.get('mName'):
#         query_params['middle_name__icontains'] = form_data['mName']
        
#     applicants_in_sy = Applicants.objects.filter(**query_params)

#     if applicants_in_sy.exists():
#         # Check if ANY of their applications this year were approved
#         has_approval_this_year = applicants_in_sy.filter(status="approved").exists()
        
#         if has_approval_this_year:
#             # Rule: Only one registration per school year if approved
#             errors["datas"] = "You can only register once per school year because you have an approved application."
#             return errors

#         # Check if they already have an application (pending/rejected) in the CURRENT semester
#         has_entry_this_semester = applicants_in_sy.filter(
#             date_created__date__range=(current_semester_start, current_semester_end)
#         ).exists()

#         if has_entry_this_semester:
#             errors["datas"] = "You already have a registration record for this semester."
#             return errors

#     return None # No duplicates found


# UPDATED
# def _check_duplicates(form_data):
#     """
#     Combined Logic:
#     1. Student Check: 1 per year if 'Approved', otherwise 1 per semester.
#     2. Guardian Check: Strictly 1 registration per SCHOOL YEAR based on Guardian Name.
#     """
#     errors = {}
#     now = timezone.now()
#     current_year = now.year

#     # --- PART 1: PREPARE DATE BOUNDARIES ---
#     # School Year (SY) spans from June 1st to May 31st of the following year
#     if now.month >= 6:
#         # 1st Sem (June - Dec) -> SY is [Current Year] to [Next Year]
#         sy_start, sy_end = date(current_year, 6, 1), date(current_year + 1, 5, 31)
#         cs_start, cs_end = date(current_year, 6, 1), date(current_year, 12, 31)
#     else:
#         # 2nd Sem (Jan - May) -> SY is [Previous Year] to [Current Year]
#         sy_start, sy_end = date(current_year - 1, 6, 1), date(current_year, 5, 31)
#         cs_start, cs_end = date(current_year, 1, 1), date(current_year, 5, 31)

#     # --- PART 2: GUARDIAN CHECK (STRICT SCHOOL YEARLY) ---
#     guardian_Fname = form_data.get('guardian_fName')
#     guardian_lName = form_data.get('guardian_lName')
#     guardian_Mname = form_data.get('guardian_mName')
#     guardian_name_ext = form_data.get('guardian_name_ext')

#     guardian_filters = {
#         'guardian_first_name__iexact': guardian_Fname,
#         'guardian_last_name__iexact': guardian_lName,
#     }

#     if guardian_Mname:
#         guardian_filters['guardian_middle_name__iexact'] = guardian_Mname
#     if guardian_name_ext:
#         guardian_filters['guardian_name_ext__iexact'] = guardian_name_ext

#     # Updated: Checking if guardian exists within the calculated School Year (sy_start to sy_end)
#     guardian_match = Applicants.objects.filter(
#         **guardian_filters, 
#         date_created__range=(sy_start, sy_end)
#     ).first()

#     if guardian_match:
#         msg = "Sorry! A guardian with this name is already registered for this school year!"
#         errors["guardian_fName"] = msg
#         errors["guardian_lName"] = msg
#         errors["guardian"] = msg
#         if guardian_Mname:
#             errors["guardian_mName"] = msg
#         if guardian_name_ext:
#             errors["guardian_name_ext"] = msg

#     # --- PART 3: STUDENT CHECK (SEMESTER/YEAR LOGIC) ---
#     student_filters = {
#         'first_name__iexact': form_data.get('fName'),
#         'last_name__iexact': form_data.get('lName'),
#     }
    
#     mName = form_data.get('mName')
#     if mName:
#         student_filters['middle_name__icontains'] = mName

#     # A. Check for any 'Approved' application in the current School Year
#     has_approval_in_sy = Applicants.objects.filter(
#         **student_filters,
#         status="approved",
#         date_created__range=(sy_start, sy_end)
#     ).exists()

#     if has_approval_in_sy:
#         errors["datas"] = "You can only register once per school year if approved. An approved application already exists."
    
#     # B. If not already flagged by approval, check if they already applied this semester
#     elif "datas" not in errors:
#         has_entry_this_semester = Applicants.objects.filter(
#             **student_filters,
#             date_created__range=(cs_start, cs_end)
#         ).exists()

#         if has_entry_this_semester:
#             errors["datas"] = "An application for this semester is already on file for this student."

def _check_duplicates(form_data):
    """
    Duplicate Check Logic (Updated):

    1. Guardian Check: Strictly 1 registration per SCHOOL YEAR based on Guardian Name.
       (School Year: June 1 to May 31 of the next year)

    2. Student (Grantee) Check: Strictly 1 application per FISCAL YEAR 
       (January 1 to December 31 of the same year), regardless of status or semester.
    """
    errors = {}
    now = timezone.now()
    current_year = now.year

    # --- PART 1: SCHOOL YEAR BOUNDARIES (for Guardian check only) ---
    if now.month >= 6:
        sy_start = date(current_year, 6, 1)
        sy_end = date(current_year + 1, 5, 31)
    else:
        sy_start = date(current_year - 1, 6, 1)
        sy_end = date(current_year, 5, 31)

    # --- PART 2: FISCAL YEAR BOUNDARIES (for Student/Grantee check) ---
    fy_start = date(current_year, 1, 1)
    fy_end = date(current_year, 12, 31)

    # --- GUARDIAN CHECK: 1 per School Year ---
    guardian_filters = {
        'guardian_first_name__iexact': form_data.get('guardian_fName'),
        'guardian_last_name__iexact': form_data.get('guardian_lName'),
    }
    guardian_mName = form_data.get('guardian_mName')
    guardian_ext = form_data.get('guardian_name_ext')

    if guardian_mName:
        guardian_filters['guardian_middle_name__iexact'] = guardian_mName
    if guardian_ext:
        guardian_filters['guardian_name_ext__iexact'] = guardian_ext

    guardian_match = Applicants.objects.filter(
        **guardian_filters,
        date_created__range=(sy_start, sy_end)
    ).exclude(status='deleted').exists()  # <-- exclude deleted

    if guardian_match:
        msg = "Sorry! A guardian with this name is already registered for this school year!"
        errors["guardian_fName"] = msg
        errors["guardian_lName"] = msg
        errors["guardian"] = msg
        if guardian_mName:
            errors["guardian_mName"] = msg
        if guardian_ext:
            errors["guardian_name_ext"] = msg

    # --- STUDENT (GRANTEE) CHECK: 1 per Fiscal Year ONLY ---
    student_filters = {
        'first_name__iexact': form_data.get('fName'),
        'last_name__iexact': form_data.get('lName'),
    }
    student_mName = form_data.get('mName')
    if student_mName:
        student_filters['middle_name__iexact'] = student_mName

    student_match_in_fy = Applicants.objects.filter(
        **student_filters,
        date_created__range=(fy_start, fy_end)
    ).exclude(status='deleted').exists()  # <-- exclude deleted

    if student_match_in_fy:
        errors["datas"] = (
            f"This student is only eligible for one grant per fiscal year ({current_year}). "
            "An application already exists for this year."
        )

    return errors

#     return errors
def _save_and_check_slots(request, form_data, active_period):
    """SAVE + IMMEDIATE SLOT CHECK"""

    try:
        with transaction.atomic():
            # CREATE APPLICANT
            school_id = Applicants.objects.count()
            year = timezone.now().year
            school = f"{year}000{school_id+1}"
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
                scholar_id = school,
                guardian_first_name=form_data['guardian_fName'],
                guardian_middle_name=form_data['guardian_mName'],
                guardian_last_name=form_data['guardian_lName'],
                guardian_name_ext=form_data['guardian_name_ext'],
                level=form_data['level'],
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
        return redirect("education:receipt",id=applicant.uid)
        
    except Exception as e:
        brgy = Barangay.objects.all()

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



def _save_and_check_slots1(request, form_data):
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
                scholar_id = school,
                guardian_first_name=form_data['guardian_fName'],
                guardian_middle_name=form_data['guardian_mName'],
                guardian_last_name=form_data['guardian_lName'],
                guardian_name_ext=form_data['guardian_name_ext'],
                level=form_data['level'],
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
            'open_date': "",
            'close_date': "",
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
    app = get_object_or_404(Applicants, uid=id)
    context = {
        "data":app
    }
    return render(request,"applicant/receipt.html",context)


@login_required
def bulk_action(request):
    if request.method == 'POST':  # adjust role check
        action = request.POST.get('action')
        applicant_ids = request.POST.getlist('applicant_ids')

        applicants = Applicants.objects.filter(id__in=applicant_ids)

        if action == 'approve':
         
            applicants.update(status='approved',date_approved = timezone.now())  # assuming you have a status field
        elif action == 'disapprove':
            applicants.update(status='disapproved',date_approved = timezone.now())
        elif action == 'delete':
            applicants.update(status='deleted',date_approved = timezone.now())

        messages.success(request, f'{action.capitalize()} action completed.')
        return redirect('education:view')

    return redirect('education:list')


def settings(request):
    entry = DataEntryPeriod.objects.first()
    
    context = {
        "active":"education_settings",
        "data":entry
    }
    
    if request.method == 'POST':
        is_active = request.POST.get('is_active')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        errors = {}
        if not is_active:
            errors['is_active'] = "Please select if Yes or No"
        if not from_date:
            errors['from_date'] = "Open Date is Required"
        if not to_date:
            errors['to_date'] = "Close Date is Required"
        
        if from_date and to_date:
            if from_date > to_date:
                errors['from_date'] = "Open Date Must Earlier than Close Date"
            
            
            
        if errors:
            context['errors'] = errors
        else:
            try:
                updates = get_object_or_404(DataEntryPeriod,id=1)
                updates.is_active = is_active
                updates.open_date = date.fromisoformat(from_date)
                updates.close_date = date.fromisoformat(to_date)
                updates.save()
                
                messages.success(request, f'Settings Updated Successfully!')
                updatedentry = DataEntryPeriod.objects.first()
                context["data"]=updatedentry
                return  redirect("education:view") 
            except Exception as e:
                    
                messages.error(request, f'Saving Settings Failed!')
      
        return  render(request,"settings.html",context)    
    else:
        return  render(request,"settings.html",context)