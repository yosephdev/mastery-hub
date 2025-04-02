from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task
from .models import Order
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_order_confirmation(order_id):
    """
    Task to send an order confirmation email
    """
    logger.info(
        f"Attempting to send confirmation email for order ID: {order_id}")
    try:
        order = Order.objects.get(id=order_id)

        # Check if email has already been sent
        if order.confirmation_email_sent:
            logger.info(
                f"Confirmation email already sent for order {order.order_number}")
            return f"Confirmation email already sent for order {order.order_number}"

        logger.info(f"Preparing email for order {order.order_number}")
        subject = f'MasteryHub - Order Confirmation #{order.order_number}'

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

        # Send to both user and admin
        recipient_list = [order.email]
        if settings.DEFAULT_FROM_EMAIL:
            recipient_list.append(settings.DEFAULT_FROM_EMAIL)

        logger.info(
            f"Sending email to {recipient_list} for order {order.order_number}")
        logger.info(f"Email settings being used:")
        logger.info(f"HOST: {settings.EMAIL_HOST}")
        logger.info(f"PORT: {settings.EMAIL_PORT}")
        logger.info(f"TLS: {settings.EMAIL_USE_TLS}")
        logger.info(f"USER: {settings.EMAIL_HOST_USER}")
        logger.info(f"FROM: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"To: {recipient_list}")

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
                html_message=html_message
            )
            logger.info(f"Email sent successfully")
        except Exception as mail_error:
            logger.error(f"SMTP Error: {str(mail_error)}")
            raise

        # Mark the email as sent
        order.confirmation_email_sent = True
        order.save()
        logger.info(
            f"Confirmation email sent successfully for order {order.order_number}")

        return f"Confirmation email sent for order {order.order_number}"

    except Order.DoesNotExist:
        logger.error(
            f"Order {order_id} not found when trying to send confirmation email")
        return f"Order {order_id} not found"
    except Exception as e:
        logger.error(
            f"Error sending confirmation email for order {order_id}: {str(e)}")
        return f"Error sending confirmation email: {str(e)}"


@shared_task
def send_payment_failure_email(order_id):
    """
    Task to send an email to the user when payment fails
    """
    logger.info(
        f"Attempting to send payment failure email for order ID: {order_id}")
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

        logger.info(
            f"Sending payment failure email to {order.email} for order {order.order_number}")
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
            html_message=html_message
        )
        logger.info(
            f"Payment failure email sent successfully for order {order.order_number}")

        return f"Payment failure email sent for order {order.order_number}"

    except Order.DoesNotExist:
        logger.error(
            f"Order {order_id} not found when trying to send payment failure email")
        return f"Order {order_id} not found"
    except Exception as e:
        logger.error(
            f"Error sending payment failure email for order {order_id}: {str(e)}")
        return f"Error sending payment failure email: {str(e)}"
