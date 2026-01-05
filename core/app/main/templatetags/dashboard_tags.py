
from django import template
from app.employee.models import Employee
register = template.Library()

@register.simple_tag(takes_context=True)
def is_admin(context):
    user = context['request'].user
    if user.is_superuser:
        return True

@register.simple_tag(takes_context=True)
def check_if_hrmo(context):
    user = context['request'].user
    if user.is_superuser:
        return True
    else:
        employee = Employee.objects.select_related('department').get(user=user)
        if employee.department.abbreviation == "MHRMO":
            return True
        
@register.simple_tag(takes_context=True)
def check_if_gso(context):
    user = context['request'].user
    if user.is_superuser:
        return True
    else:
        employee = Employee.objects.select_related('department').get(user=user)
        if employee.department.abbreviation == "MGSO":
            return True