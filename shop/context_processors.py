from .models import Category


def navigation_categories(request):
    """Make active catalogue categories available to the main navigation."""

    return {
        "navigation_categories": Category.objects.all(),
    }
