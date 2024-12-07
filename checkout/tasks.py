from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_order_confirmation(order_id):
    from .models import Order
    order = Order.objects.get(id=order_id)
    send_mail(
        f'Order Confirmation - {order.order_number}',
        f'Thank you for your order! Your order number is {order.order_number}.',
        'from@masteryhub.com',
        [order.email],
        fail_silently=False,
    ) 