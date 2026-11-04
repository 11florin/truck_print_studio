from django.conf import settings
from django.db import models
from shop.models import Product

# Create your models here.

class Coupon(models.Model):
    code = models.CharField(max_length=40, unique=True)
    discount_percent = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(discount_percent__lte=100),
                name="coupon_discount_at_most_100",
            ),
        ]

    def __str__(self):
        return self.code


class Order(models.Model):
    STATUS = [('pending', 'Pending'), ('paid', 'Paid'),
              ('shipped', 'Shipped'), ('cancelled', 'Cancelled')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField()
    full_name = models.CharField(max_length=160)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_session_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total__gte=0),
                name='order_total_non_negative',
            ),
        ]
        