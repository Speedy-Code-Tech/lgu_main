from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def is_superUser(context):
    user = context['request'].user
    if user.is_superuser:
        return True
