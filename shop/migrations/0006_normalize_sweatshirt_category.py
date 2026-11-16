from django.db import migrations


def normalize_sweatshirt_category(apps, schema_editor):
    Category = apps.get_model("shop", "Category")
    Product = apps.get_model("shop", "Product")

    canonical = Category.objects.filter(name__iexact="Sweatshirt").first()
    duplicate = Category.objects.filter(name__iexact="Sweatshirts").first()

    if not duplicate:
        return

    if not canonical:
        duplicate.name = "Sweatshirt"
        duplicate.slug = "sweatshirt"
        duplicate.save(update_fields=["name", "slug"])
        return

    Product.objects.filter(category=duplicate).update(category=canonical)
    duplicate.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0005_replace_legacy_categories"),
    ]

    operations = [
        migrations.RunPython(
            normalize_sweatshirt_category,
            migrations.RunPython.noop,
        ),
    ]
