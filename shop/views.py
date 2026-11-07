from django.shortcuts import get_object_or_404, render
from .models import Category, Product


# Create your views here.
# def _cart(request):
#     """ Returns the session cart, initializing it if it is missing. """
#     pass


def home(request):
    """ Displays the homepage with active and featured products. """
    featured = Product.objects.filter(active=True, featured=True)[:8]
    return render(request, "shop/base.html", {
        "featured": featured
    })


def product_list(request):
    """ Display the catalog and apply the filters from the query string. """
    return render(request, "shop/list.html")


def category_detail(request, slug):
    """ Display only the active products from the URL's category. """

    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(active=True).order_by("-created_at")
    return render(request, "shop/category_detail.html", {
        "category": category,
        "products": products,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        active=True
    )
    return render(request, "shop/detail.html", {
        "product": product
    })


def cart(request):
    """ Convert the identifiers from the session into displayable products and totals."""
    return render(request, "shop/cart.html")