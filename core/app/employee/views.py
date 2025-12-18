from django.shortcuts import render,redirect
from django.contrib import messages
from django.db import IntegrityError
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404

from .models import Department
from .models import Position
from .models import Employee

# Create your views here.
@login_required
def index(request):
   
                
    context = {
        'active':"employee",
        "employee":Employee.objects.filter(stat="None").order_by('-id')  
       
    }
    if request.user.is_superuser:  
        context['employee'] = Employee.objects.filter(stat="None").order_by('-id')
    else:
        empid = request.user.username
        emp = Employee.objects.select_related('department').filter(employee_id=empid).first()
        dept = emp.department.id
       
        context['employee'] = Employee.objects.filter(department_id=dept,stat="None").order_by('-id')
            
    return render(request,'employee/view.html',context)


def generate_employee_id():
    year = timezone.now().year
    year_str = str(year)  # "2025"

    # Get the last employee ID that starts with current year
    last_employee = Employee.objects.filter(
        employee_id__startswith=year_str
    ).order_by('-id').first()

    if last_employee and last_employee.employee_id:
        # Extract the number part: "20250005" → 5
        try:
            last_number = int(last_employee.employee_id[-4:])  # last 4 digits
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1

    new_id = f"{year_str}{next_number:04d}"
    return new_id


def parse_date(date_str):
    if date_str and date_str.strip():
        return date_str.strip()
    return None
        
@login_required
def create(request):
    emp_id = generate_employee_id()


    context = {
        'active': "employee",
        'departments': Department.objects.all(),
        'positions': Position.objects.all(),
        'emp_id':emp_id
    }

    if request.method == 'POST':
        # Extract data
        first_name = request.POST.get('first_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip() or None
        last_name = request.POST.get('last_name', '').strip()
        ext_name = request.POST.get('ext_name', '').strip() or None
        gender = request.POST.get('gender')
        role = request.POST.get('role')
        civil_status = request.POST.get('civil_status')
        mobile_number = request.POST.get('mobile_number', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        date_of_birth_str = request.POST.get('date_of_birth', '').strip()
        place_of_birth = request.POST.get('place_of_birth', '').strip()
        employee_id =  request.POST.get('employee_id', '').strip()
        tin_no = request.POST.get('tin_no', '').strip() or None
        pagibig = request.POST.get('pagibig_no', '').strip() or None
        gsis_no = request.POST.get('gsis_no', '').strip() or None
        philhealth_no = request.POST.get('philhealth_no', '').strip() or None
        sss_no = request.POST.get('sss_no', '').strip() or None

        department_id = request.POST.get('department') or None
        position_id = request.POST.get('position') or None
        employment_status = request.POST.get('employement_status')  # fix typo in template too!
        is_employed = request.POST.get('is_employed', 'True') == 'True'

        has_eligibility = request.POST.get('has_eligibility')
        eligibility_type = request.POST.get('eligibility_type', '').strip() or None
        ratings = request.POST.get('ratings', '').strip()
        ratings = float(ratings) if ratings else None

        profile_picture = request.FILES.get('profile')

        # Optional date fields - convert empty string to None
     

        date_hired = parse_date(request.POST.get('date_hired'))
        date_regularized = parse_date(request.POST.get('date_regularized'))
        date_separation = parse_date(request.POST.get('date_separation'))
        date_of_examination = parse_date(request.POST.get('date_examination'))
        date_of_birth = parse_date(date_of_birth_str)

        # Validation
        error = {}
        if not first_name:
            error['first_name'] = {'msg': 'First name is required'}
        if not role:
            error['role'] = {'msg': 'Role is required'}
        if not last_name:
            error['last_name'] = {'msg': 'Last name is required'}
        if not gender:
            error['gender'] = {'msg': 'Please select gender'}
        if not civil_status:
            error['civil_status'] = {'msg': 'Please select civil status'}
        if not date_of_birth:
            error['date_of_birth'] = {'msg': 'Date of Birth is Required'}
        if not date_hired:
            error['date_hired'] = {'msg': 'Date Hired is Required'}
        if not place_of_birth:
            error['place_of_birth'] = {'msg': 'Place of Birth is Required'}
        if not address:
            error['address'] = {'msg': 'Address is Required'}
        if not mobile_number:
            error['mobile_number'] = {'msg': 'Mobile number is required'}
        elif len(mobile_number) != 11 or not mobile_number.startswith('09'):
            error['mobile_number'] = {'msg': 'Must be 11 digits starting with 09'}
        if not department_id:
            error['department'] = {'msg': 'Please select department'}
        if not position_id:
            error['position'] = {'msg': 'Please select position'}
        if not employment_status:
            error['employement_status'] = {'msg': 'Please select employment status'}

        if error:
            context['error'] = error
            context.update({
                'form_data': request.POST  # optional: repopulate form
            })
            return render(request, 'employee/create.html', context)

        try:
            user = User.objects.create_user(
                password="lgulabo2025",
                username=emp_id,
                email=email,
                first_name = first_name,
                last_name = last_name
            )
            Employee.objects.create(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                name_ext=ext_name or None,
                gender=gender,
                employee_id = employee_id,
                civil_status=civil_status,
                mobile=mobile_number,
                email=email,
                date_of_birth=date_of_birth,
                place_of_birth=place_of_birth,
                address=address,
                tin=tin_no,
                pagibig=pagibig,
                gsis=gsis_no,
                philhealth=philhealth_no,
                sss=sss_no,
                department_id=department_id,
                position_id=position_id,
                employment_status=employment_status,
                date_hired=date_hired,
                date_regularized=date_regularized,
                date_separation=date_separation,
                is_active=is_employed,
                has_eligibility=has_eligibility,
                eligibility_type=eligibility_type or None,
                rating=ratings,
                date_of_examination=date_of_examination,
                profile_picture=profile_picture,
                role = role,
                user = user,
                
            )
            

            
            messages.success(request, f"Employee {first_name} {last_name} created successfully!")
            return redirect('employee:view')

        except Exception as e:
            print("Error saving employee:", e)
            messages.error(request, f"Failed to save employee. Error: {str(e)}")
            context['form_data'] = request.POST
            return render(request, 'employee/create.html', context)

    return render(request, 'employee/create.html', context)

@login_required
def show(request,id):
    context = {
        'active':"employee",
        "emp":Employee.objects.filter(id=id).first(),
        'departments': Department.objects.all(),
        'positions': Position.objects.all(),
          
       
    }
    return render(request,'employee/show.html',context)

@login_required
def destroy(request):
    id = request.POST.get("id")
    print(f"ID: {id}")
    try:
        emp = Employee.objects.filter(id=id).first()
        emp.stat = "Deleted"
        emp.save()
        messages.success(request,f"Employee  Deleted  Successfully")    
    except Exception as e:
        print(e)
        messages.error(request,f"Employee Deleting  Failed!")    
        
    return redirect("employee:view")



@login_required
def edit(request, id):
    # GET THE ACTUAL EMPLOYEE BY ID
    employee = get_object_or_404(Employee, id=id)

    context = {
        'active': "employee",
        'departments': Department.objects.all(),
        'positions': Position.objects.all(),
        'employee': employee,  # Pass the employee object
        'emp_id': employee.employee_id,  # Show current ID (not generate new!)
    }

    if request.method == 'POST':
        # Extract data
        first_name = request.POST.get('first_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip() or None
        last_name = request.POST.get('last_name', '').strip()
        ext_name = request.POST.get('ext_name', '').strip() or None
        gender = request.POST.get('gender')
        role = request.POST.get('role')
        civil_status = request.POST.get('civil_status')
        mobile_number = request.POST.get('mobile_number', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        date_of_birth_str = request.POST.get('date_of_birth', '').strip()
        place_of_birth = request.POST.get('place_of_birth', '').strip()
        tin_no = request.POST.get('tin_no', '').strip() or None
        pagibig = request.POST.get('pagibig_no', '').strip() or None
        gsis_no = request.POST.get('gsis_no', '').strip() or None
        philhealth_no = request.POST.get('philhealth_no', '').strip() or None
        sss_no = request.POST.get('sss_no', '').strip() or None

        department_id = request.POST.get('department')
        position_id = request.POST.get('position')
        employment_status = request.POST.get('employement_status')
        is_employed = request.POST.get('is_employed', 'True') == 'True'
        has_eligibility = request.POST.get('has_eligibility', 'False') == 'True'
        eligibility_type = request.POST.get('eligibility_type', '').strip() or None
        ratings = request.POST.get('ratings', '').strip()
        ratings = float(ratings) if ratings else None
        profile_picture = request.FILES.get('profile')

        # Parse dates
        date_hired = parse_date(request.POST.get('date_hired')) if request.POST.get('date_hired') else None
        date_regularized = parse_date(request.POST.get('date_regularized')) if request.POST.get('date_regularized') else None
        date_separation = parse_date(request.POST.get('date_separation')) if request.POST.get('date_separation') else None
        date_examination = parse_date(request.POST.get('date_examination')) if request.POST.get('date_examination') else None
        date_of_birth = parse_date(date_of_birth_str) if date_of_birth_str else None

        # Validation
        error = {}
        if not first_name: error['first_name'] = {'msg': 'First name is required'}
        if not last_name: error['last_name'] = {'msg': 'Last name is required'}
        if not gender: error['gender'] = {'msg': 'Please select gender'}
        if not role: error['role'] = {'msg': 'Please select Role'}
        if not civil_status: error['civil_status'] = {'msg': 'Please select civil status'}
        if not date_of_birth: error['date_of_birth'] = {'msg': 'Date of Birth is Required'}
        if not date_hired: error['date_hired'] = {'msg': 'Date Hired is Required'}
        if not mobile_number or len(mobile_number) != 11 or not mobile_number.startswith('09'):
            error['mobile_number'] = {'msg': 'Must be 11 digits starting with 09'}
        if not department_id: error['department'] = {'msg': 'Please select department'}
        if not position_id: error['position'] = {'msg': 'Please select position'}
        if not employment_status: error['employement_status'] = {'msg': 'Please select employment status'}

        if error:
            context['error'] = error
            return render(request, 'employee/edit.html', context)

        try:
            # UPDATE THE EXISTING EMPLOYEE
            employee.first_name = first_name
            employee.middle_name = middle_name
            employee.last_name = last_name
            employee.name_ext = ext_name
            employee.gender = gender
            employee.civil_status = civil_status
            employee.mobile = mobile_number
            employee.email = email
            employee.date_of_birth = date_of_birth
            employee.place_of_birth = place_of_birth
            employee.address = address
            employee.tin = tin_no
            employee.pagibig = pagibig
            employee.gsis = gsis_no
            employee.philhealth = philhealth_no
            employee.sss = sss_no
            employee.department_id = department_id
            employee.position_id = position_id
            employee.employment_status = employment_status
            employee.date_hired = date_hired
            employee.date_regularized = date_regularized
            employee.date_separation = date_separation
            employee.is_active = is_employed
            employee.has_eligibility = has_eligibility
            employee.eligibility_type = eligibility_type
            employee.rating = ratings
            employee.date_of_examination = date_examination

            if profile_picture:
                employee.profile_picture = profile_picture

            employee.role = role
            employee.save()
            # Optional: Update associated User (only if exists)
            if hasattr(employee, 'user'):  # if you have OneToOne with User
                user = employee.user
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
            else:
                # Or find by username = employee_id
                try:
                    user = User.objects.get(username=employee.employee_id)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.save()
                except User.DoesNotExist:
                    pass  # no user linked yet

            messages.success(request, f"Employee {first_name} {last_name} updated successfully!")
            return redirect('employee:view')  # or show page

        except Exception as e:
            messages.error(request, f"Error updating employee: {str(e)}")
            context['error'] = {'general': {'msg': str(e)}}
            return render(request, 'employee/edit.html', context)

    # GET request - pre-fill form
    else:
        context.update({
            'request.POST': {
                'first_name': employee.first_name,
                'middle_name': employee.middle_name or '',
                'last_name': employee.last_name,
                'ext_name': employee.name_ext or '',
                'gender': employee.gender,
                'civil_status': employee.civil_status,
                'role':employee.role,
                'mobile_number': employee.mobile,
                'email': employee.email or '',
                'date_of_birth': employee.date_of_birth.strftime('%Y-%m-%d') if employee.date_of_birth else '',
                'place_of_birth': employee.place_of_birth or '',
                'address': employee.address or '',
                'tin_no': employee.tin or '',
                'pagibig_no': employee.pagibig or '',
                'gsis_no': employee.gsis or '',
                'philhealth_no': employee.philhealth or '',
                'sss_no': employee.sss or '',
                'department': str(employee.department_id) if employee.department else '',
                'position': str(employee.position_id) if employee.position else '',
                'employement_status': employee.employment_status,
                'is_employed': 'True' if employee.is_active else 'False',
                'has_eligibility': 'True' if employee.has_eligibility else 'False',
                'eligibility_type': employee.eligibility_type or '',
                'ratings': employee.rating or '',
                'date_hired': employee.date_hired.strftime('%Y-%m-%d') if employee.date_hired else '',
                'date_regularized': employee.date_regularized.strftime('%Y-%m-%d') if employee.date_regularized else '',
                'date_separation': employee.date_separation.strftime('%Y-%m-%d') if employee.date_separation else '',
                'date_examination': employee.date_of_examination.strftime('%Y-%m-%d') if employee.date_of_examination else '',
            }
        })

    return render(request, 'employee/edit.html', context)