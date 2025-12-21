from django import template
from app.employee.models import Employee
register = template.Library()


@register.simple_tag(takes_context=True)
def isAdmin(context):
    user = context['request'].user
    empRole = Employee.objects.filter(user_id=user.id).first()
    role = empRole.role    
    if role=='admin':
        return True