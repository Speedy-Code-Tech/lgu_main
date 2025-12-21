from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.education_assistance.models import Applicants as Education
from app.gso.procurement.models import Procurement
from app.employee.models import Position
from app.employee.models import Employee

@login_required
def dashboard(request):
    user = request.user

    # # Base counts
    education_count = Education.objects.count()
    procurement_count = Procurement.objects.count()
    employee_count = Employee.objects.count()

    is_super = user.is_superuser

    if is_super:
        # Superuser sees all employees with department info
        employees = Employee.objects.select_related('department').exclude(stat = "Deleted").all()
        employee_count = employees.count()
    else:
        try:
            employee_obj = Employee.objects.select_related('department').get(user=user)
            if employee_obj.department.abbreviation in ["MGSO", "HRMO"]:
                # For MGSO/HRMO, count employees in that department
                employee_count = Employee.objects.filter(
                    department=employee_obj.department,
                    
                ).exclude(stat = "Deleted").count()
            else:
                # Otherwise just show the single employee
                employee_count = 1
        except Employee.DoesNotExist:
            employee_count = 0

    # emp = Employee.objects.select_related('department').all()
    # print(emp)
    context = {
        "title": "Login",
        "name": user,
        "active": "dashboard",
        "education": education_count,
        "procurement": procurement_count,
        "employee": employee_count,
        "is_super": is_super,
        
    }
    return render(request, "dashboard.html", context)
