from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from app.education_assistance.models import Applicants as Education
from app.gso.procurement.models import Procurement
from app.employee.models import Employee
from .models import Barangay  # Assuming Barangay is in the same app as the view
from django.utils import timezone
import datetime
@login_required
def dashboard(request):
    user = request.user

    # Base counts
    current_year = timezone.now().year 
    current_month = timezone.now().month 
    
    if current_month >=6 and current_month <=12:
        start_date = datetime.date(current_year, 6, 1)
        end_date = datetime.date(current_year, 12, 31)
    else:
        start_date = datetime.date(current_year, 1, 1)
        end_date = datetime.date(current_year, 5, 31)
        
    education_count = Education.objects.filter(
     date_created__range=[start_date, end_date]
    ).exclude(status='deleted').count()
    
    
    procurement_count = Procurement.objects.count()

    # Employee count with role-based logic
    is_super = user.is_superuser
    employee_count = 0  # Default

    if is_super:
        employee_count = Employee.objects.exclude(stat="Deleted").count()
    else:
        try:
            current_employee = Employee.objects.select_related('department').get(user=user)
            dept_abbrev = current_employee.department.abbreviation if current_employee.department else None

            if dept_abbrev in ["MGSO", "HRMO"]:
                employee_count = Employee.objects.filter(
                    department=current_employee.department
                ).exclude(stat="Deleted").count()
            else:
                employee_count = 1  # Only themselves
        except Employee.DoesNotExist:
            employee_count = 0

    # === Status Chart Data ===
    pending_count = Education.objects.filter(
    status__isnull=True,  # or status='' if you use empty string for pending
    date_created__range=[start_date, end_date]).exclude(status='deleted').count()
    approved_count = Education.objects.filter(status="approved",   date_created__range=[start_date, end_date]).count()
    disapproved_count = Education.objects.filter(status="disapproved",   date_created__range=[start_date, end_date]).count()

    status_chart_data = [pending_count, approved_count, disapproved_count]

    # === Barangay Chart Data (All 52, including 0s) ===
    all_barangays = Barangay.objects.all().order_by('name')

    # Get counts efficiently in one query
    applicant_counts = Education.objects.filter(  date_created__range=[start_date, end_date]).exclude(status='deleted').values('brgy_id') \
                                        .annotate(count=Count('id')) \
                                        .values_list('brgy_id', 'count')
    count_dict = dict(applicant_counts or {})  # Handle empty case

    brgy_labels = []
    brgy_counts = []

    for brgy in all_barangays:
        brgy_name = brgy.name.strip() if brgy.name else "Unknown Barangay"
        brgy_labels.append(brgy_name)
        brgy_counts.append(count_dict.get(brgy.id, 0))

    # Sort by applicant count descending
    sorted_brgy = sorted(zip(brgy_counts, brgy_labels), reverse=True)
    brgy_counts = [count for count, _ in sorted_brgy]
    brgy_labels = [label for _, label in sorted_brgy]
   
    # === Context ===
    context = {
        "title": "Dashboard",
        "name": user.get_full_name() or user.username,  # Better display name
        "active": "dashboard",
        "education": education_count,
        "procurement": procurement_count,
        "employee": employee_count,
        "is_super": is_super,
        "status": status_chart_data,           # For donut chart: [Pending, Approved, Disapproved]
        "brgy_labels": brgy_labels,            # For bar chart labels
        "brgy_counts": brgy_counts,            # For bar chart data
    }

    return render(request, "dashboard.html", context)