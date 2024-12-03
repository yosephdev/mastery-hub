from django import template

register = template.Library()


@register.filter(name='sub')
def subtract(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return value


@register.filter
def range_filter(value):
    return range(value)


@register.filter
def to(value, arg):
    try:
        return type(value)(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def custom_field_errors(field):
    return field.errors


@register.filter(name='addclass')
def add_class(field, css_class):
    print(f"add_class called with field type: {type(field).__name__}")
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css_class})
    else:
        raise ValueError(
            f"Expected a form field, got a {type(field).__name__} instead.")
