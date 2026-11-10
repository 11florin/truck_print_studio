""" Views for the store's checkout flow. """

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CheckoutForm
from shop.models import Product
from .models import Order, OrderItem

from decimal import Decimal

# Create your views here.


def checkout(request):
    """ Build the order from the session cart and display the checkout. """

    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys(), active=True)
    items = []
    for product in products:
        try:
            quantity = int(cart[str(product.id)])
        except (KeyError, TypeError, ValueError):
            continue
        if 0 < quantity <= product.stock:
            items.append((product, quantity))
    total = sum((p.price * quantity for p, quantity in items), Decimal('0'))
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and items:
        if not form.is_valid():
            messages.error(request, "Please complete all checkout fields.")
            return render(
                request,
                "orders/checkout.html", {
                    "items": items, 
                    "total": total, 
                    "form": form
                    },
                status=400,
            )
        data = form.cleaned_data
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=data["email"],
            full_name=data["full_name"],
            address=data["address"],
            city=data["city"],
            postal_code=data["postal_code"],
            total=total,
        )
        OrderItem.objects.bulk_create(
            [
                OrderItem(order=order, product=p, quantity=q, price=p.price)
                for p, q in items
            ]
        )
        request.session['cart'] = {}
        request.session["recent_order_id"] = order.id
        messages.success(
            request,
            'Order placed successfully. Stripe can be enabled with STRIPE_SECRET_KEY.',
        )
        return redirect('orders:success', order_id=order.id)
    return render(
        request,
        "orders/checkout.html",
        {"items": items, "total": total, "form": form},
    )



def success(request, order_id):
    """Display the confirmation for the order identified in the URL."""

    if request.session.get("recent_order_id") != order_id:
        raise Http404("Order confirmation is not available.")
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/success.html', {'order': order})