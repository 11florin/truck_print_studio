from django.db import models

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