
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.http import HttpRequest
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import Category, Product, Review, Wishlist

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
    is_in_wishlist = (
        request.user.is_authenticated
        and Wishlist.objects.filter(user=request.user, product=product).exists()
    )
    reviews = product.reviews.select_related("user")
    return render(request, "shop/detail.html", {
        "product": product,
        "is_in_wishlist": is_in_wishlist,
        "reviews": reviews,
    })


@login_required
def review_create(request, product_id):
    """Create a review for an active product."""

    product = get_object_or_404(Product, id=product_id, active=True)
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.save()
        messages.success(request, "Your review was added.")
        return redirect("shop:detail", slug=product.slug)
    return render(request, "shop/review_form.html", {
        "form": form,
        "product": product,
        "form_title": "Write a review",
        "submit_label": "Publish review",
    })


@login_required
def review_update(request, review_id):
    """Edit a review only when it belongs to the authenticated user."""

    review = get_object_or_404(
        Review.objects.select_related("product"),
        id=review_id,
        user=request.user,
    )
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your review was updated.")
        return redirect("shop:detail", slug=review.product.slug)
    return render(request, "shop/review_form.html", {
        "form": form,
        "product": review.product,
        "form_title": "Edit your review",
        "submit_label": "Save changes",
    })


@login_required
@require_POST
def review_delete(request, review_id):
    """Delete a review only when it belongs to the authenticated user."""

    review = get_object_or_404(
        Review.objects.select_related("product"),
        id=review_id,
        user=request.user,
    )
    product_slug = review.product.slug
    review.delete()
    messages.success(request, "Your review was deleted.")
    return redirect("shop:detail", slug=product_slug)


@login_required
def wishlist(request):
    """Display the authenticated user's saved products."""

    wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
        "product",
        "product__category",
    )
    return render(request, "shop/wishlist.html", {
        "wishlist_items": wishlist_items,
    })


@login_required
@require_POST
def wishlist_add(request, product_id):
    """Save an active product for the authenticated user."""

    product = get_object_or_404(Product, id=product_id, active=True)
    _, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
    )
    if created:
        messages.success(request, f"{product.name} was added to your wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    return redirect("shop:detail", slug=product.slug)


@login_required
@require_POST
def wishlist_remove(request, product_id):
    """Remove a product only from the authenticated user's wishlist."""

    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"{product.name} was removed from your wishlist.")
    return redirect("shop:detail", slug=product.slug)


@require_POST
def cart_add(request, product_id):
    """Add the requested quantity to the cart stored in the session."""

    product = get_object_or_404(Product, id=product_id, active=True)
    cart = _cart(request)
    key = str(product.id)
    next_url = _safe_next_url(request)
    try:
        requested_quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect(next_url)
    if requested_quantity < 1:
        messages.error(request, "Quantity must be at least one.")
        return redirect(next_url)
    quantity = min(
        int(cart.get(key, 0)) + requested_quantity,
        product.stock,
    )
    if quantity:
        cart[key] = quantity
        request.session.modified = True
        messages.success(request, f'{product.name} added to your bag.')
    return redirect(next_url)


@require_POST
def cart_remove(request, product_id):
    """Remove a product from the session cart and return to the bag."""

    cart = _cart(request)
    key = str(product_id)
    product = Product.objects.filter(id=product_id).first()
    if key in cart:
        cart.pop(key)
        request.session.modified = True
        product_name = product.name if product else "Product"
        messages.success(request, f"{product_name} was removed from your bag.")
    return redirect("shop:cart")


def _safe_next_url(request: HttpRequest) -> str:
    """Returns a valid internal destination or the cart page."""

    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return "shop:cart"


def cart(request):
    """ Convert the identifiers from the session into displayable products and totals."""
    cart_data = _cart(request)
    products = Product.objects.filter(id__in=cart_data.keys(), active=True)
    items = []
    for product in products:
        try:
            quantity = int(cart_data[str(product.id)])
        except (KeyError, TypeError, ValueError):
            continue
        if 0 < quantity <= product.stock:
            items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "total": product.price * quantity,
                }
            )
    total = sum((item["total"] for item in items), Decimal("0"))
    return render(request, "shop/cart.html", {"items": items, "total": total})