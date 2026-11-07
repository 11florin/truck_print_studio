""" Register the order models in the Django admin. """
from django.contrib import admin
from .models import Coupon, Order, OrderItem

# Register your models here.
admin.site.register([Coupon, Order, OrderItem])