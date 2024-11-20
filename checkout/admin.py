from django.contrib import admin
from checkout.models import Order

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'country')
    search_fields = ('order_number', 'country')
