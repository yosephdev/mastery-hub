from django import template

register = template.Library()

@register.filter(name='sub')
def subtract(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return value
