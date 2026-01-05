from django import template
from app.employee.models import Employee
register = template.Library()


@register.simple_tag(takes_context=True)
def isAdmin(context):
    user = context['request'].user
    if user.is_superuser:
        return True
    if user.is_authenticated:
        try:
            employee = Employee.objects.get(user=user)
            return employee.role == 'admin'
        except Employee.DoesNotExist:
            return False
    return False