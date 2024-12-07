from django import template

register = template.Library()

@register.filter
def get_payment_intent_id(client_secret):
    """Extract payment intent ID from client secret"""
    if client_secret:
        return client_secret.split('_secret_')[0]
    return ''