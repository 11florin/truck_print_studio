from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"


    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPES = [('tshirt', 'T-shirt'), ('hoodie', 'Hoodie'), ('mug', 'Mug')]
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='tshirt')
    design_theme = models.CharField(max_length=120, default='UK Road Transport')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True)
    stock = models.PositiveIntegerField(default=0)
    made_to_order = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name='product_price_non_negative',
            ),
        ]


    