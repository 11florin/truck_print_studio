from django.shortcuts import get_object_or_404, render
from django.db.models import Q
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

    products = Product.objects.filter(active=True).select_related("category")
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    product_type = request.GET.get("type", "")

    if query:
        products = products.filter(Q(name_icontains=query) | Q(description_icontains=query))

    if category:
        products = products.filter(category__slug=category)

    if product_type in dict(Product.PRODUCT_TYPES):
        products = products.filter(product_type=product_type)

    return render(request, "shop/list.html", {
        "products": products,
        "categories": Category.objects.all(),
        "query": query,
        "product_type": Product.PRODUCT_TYPES,
        "selected_type": product_type,
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


def cart(request):
    """ Convert the identifiers from the session into displayable products and totals."""
    return render(request, "shop/cart.html")