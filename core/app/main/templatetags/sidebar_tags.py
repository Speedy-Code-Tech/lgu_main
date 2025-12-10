
from django import template
from app.employee.models import Employee

register = template.Library()

@register.simple_tag
def is_gso_active(request, active):
    path = request.path if request else ''
    gso_active = (
        'gso' in path or
        active in ['procurement', 'procurement_create', 'inventory', 
                  'supplies', 'vehicle', 'reports']
    )
    return 'open' if gso_active else ''

@register.simple_tag
def is_gso_active_class(request,active):
    paths = request.path if request else ''
    gso_active = (
    'gso' in paths or
    active in ['procurement', 'procurement_create', 'inventory', 
              'supplies', 'vehicle', 'reports']
    )
    return 'bg-green-600 text-white' if gso_active else 'text-gray-700 hover:bg-gray-100'
    
@register.simple_tag(takes_context=True)
def check_role(context):
    user = context['request'].user
    if not user.is_authenticated:
        return "guest"
    if user.is_superuser:
        return "superadmin"
    if user.groups.filter(name='Admin').exists():
        return "admin"
    if user.groups.filter(name='Co-Admin').exists():
        return "coadmin"
    return "user"


@register.simple_tag(takes_context=True)
def check_if_gso(context):
    user = context['request'].user
    if user.is_superuser:
        return True
    else:
        employee = Employee.objects.select_related('department').get(user=user)
        if employee.department.abbreviation == "MGSO":
            return True


@register.simple_tag(takes_context=True)
def check_education(context):
    user = context['request'].user
    if user.is_superuser:
        return True
        
@register.simple_tag(takes_context=True)
def check_event(context):
    user = context['request'].user
    if user.is_superuser:
        return True
        

@register.simple_tag(takes_context=True)
def check_employee(context):
    user = context['request'].user
    if user.is_superuser:
        return True
    else:
        employee = Employee.objects.select_related('department').get(user=user)
        if employee.role == "admin":
            return True

