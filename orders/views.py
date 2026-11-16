"""Views for the store's checkout flow."""

import logging
from decimal import Decimal
from smtplib import SMTPException

import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from resend.exceptions import ResendError

from .forms import CheckoutForm
from .email_service import send_order_confirmation
from .models import Order, OrderItem
from shop.models import Product
from .stripe_service import (
    StripeConfigurationError,
    create_checkout_session,
    expire_checkout_session,
    verify_webhook,
)

logger = logging.getLogger(__name__)


def _cancel_order(order):
    """Cancel a pending order."""

    order.status = "cancelled"
    order.save(update_fields=["status"])


def checkout(request):
    """ Build the order from the session cart and display the checkout. """

    cart = request.session.get('cart', {})
    cart_entries = []
    product_ids = set()
    for cart_key, cart_value in cart.items():
        product_id, separator, size = str(cart_key).partition(":")
        if not product_id.isdigit():
            continue
        if separator and size not in dict(Product.SIZE_CHOICES):
            continue
        quantity = cart_value.get("quantity", 0) if isinstance(cart_value, dict) else cart_value
        cart_entries.append((int(product_id), size, quantity))
        product_ids.add(int(product_id))
    products = Product.objects.filter(id__in=product_ids, active=True)
    products_by_id = {product.id: product for product in products}
    items = []
    checkout_errors = []
    for product_id, size, raw_quantity in cart_entries:
        product = products_by_id.get(product_id)
        if product is None:
            checkout_errors.append("One or more products in your bag are no longer available.")
            continue
        try:
            quantity = int(raw_quantity)
        except (KeyError, TypeError, ValueError):
            checkout_errors.append(f"{product.name} has an invalid quantity.")
            continue
        if quantity <= 0:
            checkout_errors.append(f"{product.name} must have a positive quantity.")
        else:
            items.append((product, quantity, size))

    missing_product_ids = product_ids - set(products_by_id)
    if missing_product_ids:
        checkout_errors.append("One or more products in your bag are no longer available.")

    total = sum((p.price * quantity for p, quantity, size in items), Decimal('0'))
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and (items or checkout_errors):
        if checkout_errors:
            for error in checkout_errors:
                messages.error(request, error)
            return render(
                request,
                "orders/checkout.html",
                {"items": items, "total": total, "form": form},
                status=400,
            )
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
        with transaction.atomic():
            total = sum(
                (product.price * quantity for product, quantity, size in items),
                Decimal("0"),
            )
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
                    OrderItem(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        size=size,
                    )
                    for product, quantity, size in items
                ]
            )
        try:
            checkout_session = create_checkout_session(order, request)
        except (StripeConfigurationError, stripe.error.StripeError) as error:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order.id)
                _cancel_order(order)
            request.session["cart"] = cart
            request.session.modified = True
            messages.error(request, f"Unable to start payment: {error}")
            return render(
                request,
                "orders/checkout.html",
                {"items": items, "total": total, "form": form},
                status=503,
            )
        order.stripe_session_id = checkout_session.id
        order.save(update_fields=["stripe_session_id"])
        request.session["pending_cart"] = cart
        request.session["cart"] = {}
        request.session["recent_order_id"] = order.id
        request.session["recent_checkout_session_id"] = checkout_session.id
        request.session.modified = True
        return redirect(checkout_session.url)
    return render(
        request,
        "orders/checkout.html",
        {"items": items, "total": total, "form": form},
    )



def success(request, order_id):
    """Display the confirmation for the order identified in the URL."""

    if request.session.get("recent_order_id") != order_id:
        raise Http404("Order confirmation is not available.")
    session_id = request.GET.get("session_id")
    if session_id != request.session.get("recent_checkout_session_id"):
        raise Http404("Order confirmation is not available.")
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        id=order_id,
    )
    if request.user.is_authenticated and order.user_id != request.user.id:
        raise Http404("Order confirmation is not available.")
    if order.stripe_session_id != session_id:
        raise Http404("Order confirmation is not available.")
    return render(request, 'orders/success.html', {'order': order})


def cancel(request, order_id):
    """Cancel a pending payment and restore the pending cart."""

    if request.session.get("recent_order_id") != order_id:
        raise Http404("Order cancellation is not available.")
    order = get_object_or_404(Order, id=order_id)
    if request.user.is_authenticated and order.user_id != request.user.id:
        raise Http404("Order cancellation is not available.")
    if order.status == "pending":
        try:
            if order.stripe_session_id:
                expire_checkout_session(order.stripe_session_id)
        except (StripeConfigurationError, stripe.error.StripeError) as error:
            messages.error(request, f"Unable to cancel payment: {error}")
            return redirect("orders:checkout")
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order.id)
            _cancel_order(order)
    pending_cart = request.session.pop("pending_cart", {})
    request.session["cart"] = pending_cart
    request.session.modified = True
    messages.info(request, "Payment was cancelled. Your bag is ready to try again.")
    return redirect("shop:cart")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Process Stripe events after verifying their signatures."""

    try:
        event = verify_webhook(
            request.body,
            request.headers.get("Stripe-Signature", ""),
        )
    except (
        ValueError,
        StripeConfigurationError,
        stripe.error.SignatureVerificationError,
    ):
        return HttpResponseBadRequest("Invalid Stripe webhook.")

    if hasattr(event, "to_dict"):
        event = event.to_dict()
    try:
        event_type = event["type"]
        session = event["data"]["object"]
    except (KeyError, TypeError):
        return HttpResponseBadRequest("Invalid Stripe event.")
    if hasattr(session, "to_dict"):
        session = session.to_dict()
    if not isinstance(session, dict):
        return HttpResponseBadRequest("Invalid Stripe event.")
    order_id = (session.get("metadata") or {}).get("order_id")
    if not order_id:
        return HttpResponse(status=200)
    try:
        send_confirmation = False
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            if event_type in {
                "checkout.session.completed",
                "checkout.session.async_payment_succeeded",
            }:
                if (
                    session.get("payment_status") == "paid"
                    and order.status == "pending"
                ):
                    order.status = "paid"
                    order.paid_at = timezone.now()
                    payment_intent_id = session.get("payment_intent")
                    if payment_intent_id:
                        order.stripe_payment_intent_id = payment_intent_id
                    update_fields = ["status", "paid_at"]
                    if payment_intent_id:
                        update_fields.append("stripe_payment_intent_id")
                    order.save(update_fields=update_fields)
                    send_confirmation = True
            elif (
                event_type in {
                    "checkout.session.completed",
                    "checkout.session.async_payment_succeeded",
                }
                and order.status == "paid"
                and not order.confirmation_email_sent
            ):
                send_confirmation = True
            elif event_type in {
                "checkout.session.async_payment_failed",
                "checkout.session.expired",
            } and order.status == "pending":
                _cancel_order(order)
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Unknown order.")
    if send_confirmation:
        try:
            send_order_confirmation(order)
        except (
            ImproperlyConfigured,
            OSError,
            ResendError,
            SMTPException,
        ):
            logger.exception("Order confirmation email failed for order %s.", order.id)
            return HttpResponse(status=503)
        order.confirmation_email_sent = True
        order.save(update_fields=["confirmation_email_sent"])
    return HttpResponse(status=200)


@login_required
def order_history(request):
    """Display the authenticated user's orders."""

    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    """Display an order only when it belongs to the authenticated user."""

    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        id=order_id,
        user=request.user,
    )
    return render(request, "orders/detail.html", {"order": order})