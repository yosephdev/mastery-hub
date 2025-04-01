from django import template

register = template.Library()

@register.filter
def get_payment_intent_id(client_secret):
    """Extract payment intent ID from client secret"""
    if client_secret:
        try:
            # The client secret format is: pi_<payment_intent_id>_secret_<secret>
            return client_secret.split('_secret_')[0]
        except:
            return ''
    return ''

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0