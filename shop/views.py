from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from .models import Category, Product

from decimal import Decimal



# Create your views here.
def _cart(request):
    """ Returns the session cart, initializing it if it is missing. """
    return request.session.setdefault('cart', {})


def home(request):
    """ Displays the homepage with active and featured products. """
    featured = Product.objects.filter(active=True, featured=True)[:8]
    return render(request, "shop/home.html", {
        "featured": featured
    })


def product_list(request):
    """ Display the catalog and apply the filters from the query string. """

    products = Product.objects.filter(active=True).select_related("category")
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    product_type = request.GET.get("type", "").strip()
    valid_product_types = dict(Product.PRODUCT_TYPES)

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if category:
        products = products.filter(category__slug=category)

    if product_type in valid_product_types:
        products = products.filter(product_type=product_type)

    return render(request, "shop/list.html", {
        "products": products,
        "categories": Category.objects.all(),
        "query": query,
        "product_type": Product.PRODUCT_TYPES,
        "selected_category": category,
        "selected_type": product_type if product_type in valid_product_types else "",
    })


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


