""" Views for account creation and authentication. """

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from orders.models import Order
from shop.models import Wishlist

from .forms import RegistrationForm


def register(request):
    """Display the account form and authenticate the user upon success."""
    if request.user.is_authenticated:
        return redirect("shop:home")
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop:home')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
    })


@login_required
def profile(request):
    """Display account details and recent customer activity."""
    recent_orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")[:3]
    )
    wishlist_items = (
        Wishlist.objects.filter(user=request.user)
        .select_related("product", "product__category")[:4]
    )

    return render(request, 'accounts/profile.html', {
        "recent_orders": recent_orders,
        "wishlist_items": wishlist_items,
        "order_count": Order.objects.filter(user=request.user).count(),
        "wishlist_count": Wishlist.objects.filter(user=request.user).count(),
    })
