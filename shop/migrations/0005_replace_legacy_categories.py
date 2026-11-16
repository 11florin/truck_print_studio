from django.db import migrations, models
from django.utils.text import slugify


def replace_legacy_categories(apps, schema_editor):
    Category = apps.get_model("shop", "Category")
    Product = apps.get_model("shop", "Product")

    def get_category(name):
        category = Category.objects.filter(name__iexact=name).first()
        if category:
            return category
        slug = slugify(name)
        category = Category.objects.filter(slug=slug).first()
        if category:
            category.name = name
            category.save(update_fields=["name"])
            return category
        return Category.objects.create(name=name, slug=slug)

    category_names = {
        "hoodie": "Hoodie",
        "mug": "Mugs",
        "tshirt": "T-Shirts",
    }
    new_categories = {
        product_type: get_category(name)
        for product_type, name in category_names.items()
    }
    sweatshirt_category = get_category("Sweatshirt")

    legacy_categories = Category.objects.filter(
        models.Q(name__iexact="Cab & Driver")
        | models.Q(name__iexact="Haulage Life")
        | models.Q(name__iexact="UK Motorway"),
    )
    for product in Product.objects.filter(category__in=legacy_categories):
        target_category = new_categories.get(
            product.product_type,
            sweatshirt_category,
        )
        Product.objects.filter(pk=product.pk).update(
            category=target_category,
        )
    legacy_categories.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0004_remove_product_stock"),
    ]

    operations = [
        migrations.RunPython(
            replace_legacy_categories,
            migrations.RunPython.noop,
        ),
    ]
