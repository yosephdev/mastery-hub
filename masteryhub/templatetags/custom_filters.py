from django import template

register = template.Library()

@register.filter(name='sub')
def subtract(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return value

@register.filter
def custom_field_errors(field):
    return field.errors