from django.shortcuts import render,redirect
from django.contrib import messages

from app.employee.models import Employee,Department
from .models import type_of_good,Mode,Procurement
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def index(request):
    context = {"active":'procurement',
               "procurements":Procurement.objects.filter(is_deleted=False).select_related('person_responsible',      # ← Employee
        'end_user',                 # ← Department
        'type_of_good',             # ← type_of_good model
        'mode_of_procurement').order_by('-id'),
               'active':'procurement'
              }
    if request.user.is_superuser:  
        context['role'] = 'admin'
    else:
        empid = request.user.username
        emp = Employee.objects.select_related('department').filter(employee_id=empid).first()
        dept = emp.role
        if dept=='admin':
            context['role'] = 'admin'

   
    return render(request,'procurement.html',context)


def clean_date(date_str):
    return date_str if date_str else None

@login_required
def create(request):
    # Always load these for the form
    context = {
        "active": "procurement_create",
        "employees": Employee.objects.filter(department__abbreviation__iexact="MGSO").select_related('department'),
        "departments": Department.objects.all().order_by('name'),
        "goods": type_of_good.objects.all().order_by('name'),
        "Modes": Mode.objects.all().order_by('name'),
    }

    if request.method == "POST":
        error = {}

        # === REQUIRED FIELDS VALIDATION ===
        person_responsible_id = request.POST.get('person_responsible')
        purchase_no = request.POST.get('purchase_no', '').strip()
        date_purchase = clean_date(request.POST.get('date_purchase'))
        end_user_id = request.POST.get('end_user')
        type_of_good_id = request.POST.get('type_of_good')
        approved_budget = request.POST.get('approved_budget')
        mode_of_procurement_id = request.POST.get('mode_of_procurement')

        if not person_responsible_id:
            error['person_responsible'] = {'errors': 'Person Responsible is required'}
        if not purchase_no:
            error['purchase_no'] = {'errors': 'Purchase No is required'}
        elif Procurement.objects.filter(purchase_no=purchase_no).exists():
            error['purchase_no'] = {'errors': f'Purchase No. Must be Unique '}
        
        if request.POST.get('mayors_no'):    
            if  Procurement.objects.filter(mayors_no=request.POST.get('mayors_no')).exists():
                error['mayors_no'] = {'errors': f'Mayors No. Must be Unique '}
        
        if request.POST.get('philgeps_reg_no'):    
            if  Procurement.objects.filter(philgeps_reg_no=request.POST.get('philgeps_reg_no')).exists():
                error['philgeps_reg_no'] = {'errors': f'Philgeps Reg No. Must be Unique '}
        
                
        # if not date_purchase:
        #     error['date_purchase'] = {'errors': 'Date of Purchase is required'}
        if not end_user_id:
            error['end_user'] = {'errors': 'End User (Department) is required'}
        if not type_of_good_id:
            error['type_of_good'] = {'errors': 'Type of Good is required'}
        # if not approved_budget:
        #     error['approved_budget'] = {'errors': 'Approved Budget is required'}
        elif not approved_budget.isdigit():
            error['approved_budget'] = {'errors': 'Budget must be a valid number'}
        if not mode_of_procurement_id:
            error['mode_of_procurement'] = {'errors': 'Mode of Procurement is required'}

        # === IF ERRORS → Show form again with errors ===
        if error:
            context['error'] = error
            context.update(request.POST.dict())  # Keep all entered values
            return render(request, 'create_procurement.html', context)

        # === ALL GOOD → SAVE TO DATABASE ===
        try:
            Procurement.objects.create(
                person_responsible_id=person_responsible_id,
                purchase_no=purchase_no,
                date_of_purchase=clean_date(date_purchase),
                end_user_id=end_user_id,
                type_of_good_id=type_of_good_id,
                approved_budget=int(approved_budget),
                charging=request.POST.get('charging'),
                mode_of_procurement_id=mode_of_procurement_id,
                min_of_meeting=request.POST.get('min_of_meeting'),
                bac_resolution=request.POST.get('bac_resolution'),
                proof_of_service=request.POST.get('proof_of_service'),
                rfqs=request.POST.get('rfqs'),
                winning_supplier=request.POST.get('winning_supplier'),
                recommending_award=request.POST.get('recommending_award'),
                philgeps=request.POST.get('philgeps'),
                po_number=request.POST.get('po_number'),
                posting_of_award=clean_date(request.POST.get('posting_of_award')) or None,
                philgeps_reg_no=request.POST.get('philgeps_reg_no'),
                mayors_no=request.POST.get('mayors_no'),
                date_delivery=clean_date(request.POST.get('date_delivery')) or None,
                date_received=clean_date(request.POST.get('date_received')) or None,
                date_check=clean_date(request.POST.get('date_check')) or None,
                checks=request.POST.get('check_no'),
                remarks=request.POST.get('remarks'),
            )

            messages.success(request, "Procurement record created successfully!")
            return redirect('gso:procurement')  # or wherever your list is

        except Exception as e:
            messages.error(request, f"Error saving record: {str(e)}")
            context['error'] = {'non_field_errors': {'errors': 'Something went wrong. Please try again.'}}
            context.update(request.POST.dict())
            return render(request, 'create_procurement.html', context)

    # GET request → just show empty form
    return render(request, 'create_procurement.html', context)


@login_required
def delete(request,id):
    try:

        procurement = Procurement.objects.get(id=id)
        procurement.is_deleted = True
        
        procurement.save()
        messages.success(request,"Procurement Delete Successfully!")
        return redirect("gso:procurement")
    except Exception as e:
        print(e)
        messages.error(request,"Procurement Deletion Failed!")
        return redirect("gso:procurement")
        

@login_required
def view(request,id):
    
    context = {"active":'procurement',
               "pr":Procurement.objects.filter(id=id).select_related('person_responsible',      # ← Employee
               'end_user',                 # ← Department
               'type_of_good',             # ← type_of_good model
               'mode_of_procurement').first(),
          
               }
    
    
    
    return render(request,'view_procurement.html',context)


@login_required
def edit(request, id):
    pr = get_object_or_404(Procurement, id=id)

    context = {
        "active": "procurement",
        "pr": pr,
        "employees": Employee.objects.filter(department__abbreviation__iexact="MGSO").select_related('department'),
        "departments": Department.objects.all().order_by('name'),
        "goods": type_of_good.objects.all().order_by('name'),
        "Modes": Mode.objects.all().order_by('name'),
    }

    if request.method == "POST":
        errors = {}

        purchase_no = request.POST.get('purchase_no', '').strip()
        person_responsible_id = request.POST.get('person_responsible')
        end_user_id = request.POST.get('end_user')
        type_of_good_id = request.POST.get('type_of_good')
        approved_budget = request.POST.get('approved_budget', '').strip()
        mode_of_procurement_id = request.POST.get('mode_of_procurement')

        # Required fields
        if not person_responsible_id:
            errors['person_responsible'] = ["Person Responsible is required."]
        if not purchase_no:
            errors['purchase_no'] = ["Purchase No is required."]
        if not end_user_id:
            errors['end_user'] = ["End User is required."]
        if not type_of_good_id:
            errors['type_of_good'] = ["Type of Good is required."]
        if not mode_of_procurement_id:
            errors['mode_of_procurement'] = ["Mode of Procurement is required."]
        if not approved_budget:
            errors['approved_budget'] = ["Approved Budget is required."]
        elif not approved_budget.isdigit():
            errors['approved_budget'] = ["Must be a valid number."]

        # --- Uniqueness: EXCLUDE current record ---
        if purchase_no != pr.purchase_no:  # only if changed
            if Procurement.objects.filter(purchase_no=purchase_no).exists():
                errors['purchase_no'] = ["This Purchase No is already taken."]

        mayors_no = request.POST.get('mayors_no', '').strip()
        if mayors_no and mayors_no != (pr.mayors_no or ''):
            if Procurement.objects.filter(mayors_no=mayors_no).exists():
                errors['mayors_no'] = ["This Mayor's No is already used."]

        philgeps_reg_no = request.POST.get('philgeps_reg_no', '').strip()
        if philgeps_reg_no and philgeps_reg_no != (pr.philgeps_reg_no or ''):
            if Procurement.objects.filter(philgeps_reg_no=philgeps_reg_no).exists():
                errors['philgeps_reg_no'] = ["This PhilGEPS Reg No is already used."]

        if errors:
            context['errors'] = errors
            context.update(request.POST.dict())
            return render(request, 'edit_procurement.html', context)

        # --- Update record ---
        try:
            pr.person_responsible_id = person_responsible_id
            pr.purchase_no = purchase_no
            pr.date_of_purchase = clean_date(request.POST.get('date_purchase')) or pr.date_of_purchase
            pr.end_user_id = end_user_id
            pr.type_of_good_id = type_of_good_id
            pr.approved_budget = int(approved_budget)
            pr.charging = request.POST.get('charging')
            pr.mode_of_procurement_id = mode_of_procurement_id
            pr.min_of_meeting = request.POST.get('min_of_meeting')
            pr.bac_resolution = request.POST.get('bac_resolution')
            pr.proof_of_service = request.POST.get('proof_of_service')
            pr.rfqs = request.POST.get('rfqs')
            pr.winning_supplier = request.POST.get('winning_supplier')
            pr.recommending_award = request.POST.get('recommending_award')
            pr.philgeps = request.POST.get('philgeps')
            pr.po_number = request.POST.get('po_number')
            pr.posting_of_award = clean_date(request.POST.get('posting_of_award')) or None
            pr.philgeps_reg_no = philgeps_reg_no or None
            pr.mayors_no = mayors_no or None
            pr.date_delivery = clean_date(request.POST.get('date_delivery')) or None
            pr.date_received = clean_date(request.POST.get('date_received')) or None
            pr.date_check = clean_date(request.POST.get('date_check')) or None
            pr.checks = request.POST.get('check_no')
            pr.remarks = request.POST.get('remarks')
            pr.save()

            messages.success(request, "Procurement updated successfully!")
            return redirect('gso:procurement')

        except Exception as e:
            messages.error(request, "Failed to update record.")
            context['errors'] = {"non_field": ["Something went wrong."]}
            context.update(request.POST.dict())
            return render(request, 'edit_procurement.html', context)

    return render(request, 'edit_procurement.html', context)