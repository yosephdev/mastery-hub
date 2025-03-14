from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task
from .models import Order


@shared_task
def send_order_confirmation(order_id):
    """
    Task to send an order confirmation email
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Check if email has already been sent
        if order.confirmation_email_sent:
            return f"Confirmation email already sent for order {order.order_number}"
            
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order}
        )

        context = {
            'order': order,
            'contact_email': settings.DEFAULT_FROM_EMAIL,
            'site_name': 'MasteryHub',
        }

        # Plain text email
        message = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            context
        )

        # HTML email
        html_message = render_to_string(
            'checkout/confirmation_emails/confirmation_email.html',
            context
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
            html_message=html_message
        )
        
        # Mark the email as sent
        order.confirmation_email_sent = True
        order.save()

        return f"Confirmation email sent for order {order.order_number}"

    except Order.DoesNotExist:
        return f"Order {order_id} not found"
    except Exception as e:
        return f"Error sending confirmation email: {str(e)}"


def send_payment_failure_email(order_id):
    """
    Task to send an email to the user when payment fails
    """
    try:
        order = Order.objects.get(id=order_id)
        subject = f'MasteryHub - Payment Failed for Order #{order.order_number}'

        context = {
            'order': order,
            'contact_email': settings.DEFAULT_FROM_EMAIL,
            'site_name': 'MasteryHub',
        }

        message = render_to_string(
            'checkout/confirmation_emails/payment_failure_email.txt',
            context
        )

        html_message = render_to_string(
            'checkout/confirmation_emails/payment_failure_email.html',
            context
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
            html_message=html_message
        )

        return f"Payment failure email sent for order {order.order_number}"

    except Order.DoesNotExist:
        return f"Order {order_id} not found"
    except Exception as e:
        return f"Error sending payment failure email: {str(e)}"
