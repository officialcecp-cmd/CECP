from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Checks if a user belongs to a specific group.
    Usage: {% if request.user|has_group:"CECP_Admins" %}
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()

@register.filter(name='split')
def split(value, arg):
    """
    Splits a string by a delimiter.
    Usage: {{ value|split:"," }}
    """
    if not value:
        return []
    return value.split(arg)

@register.filter(name='trim')
def trim(value):
    """
    Trims whitespace from a string.
    Usage: {{ value|trim }}
    """
    if not value:
        return ""
    return value.strip()

