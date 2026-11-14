"""Stripe Checkout and webhook helpers."""

from django.conf import settings
from django.urls import reverse

import stripe


class StripeConfigurationError(RuntimeError):
    """Raised when Stripe is not configured for the current environment."""


def _stripe_api_key():
    if not settings.STRIPE_SECRET_KEY:
        raise StripeConfigurationError("Stripe is not configured.")
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(order, request):
    """Create a hosted Stripe Checkout Session for an order."""

    _stripe_api_key()
    line_items = [
        {
            "price_data": {
                "currency": settings.STRIPE_CURRENCY,
                "product_data": {
                    "name": item.product.name,
                    "metadata": {"size": item.size} if item.size else {},
                },
                "unit_amount": int(item.price * 100),
            },
            "quantity": item.quantity,
        }
        for item in order.items.select_related("product").all()
    ]
    return stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        customer_email=order.email,
        metadata={"order_id": str(order.id)},
        success_url=(
            request.build_absolute_uri(
                reverse("orders:success", args=[order.id])
            )
            + "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url=request.build_absolute_uri(
            reverse("orders:cancel", args=[order.id])
        ),
    )


def verify_webhook(payload, signature):
    """Verify and decode a Stripe webhook payload."""

    if not settings.STRIPE_WEBHOOK_SECRET:
        raise StripeConfigurationError("Stripe webhook is not configured.")
    return stripe.Webhook.construct_event(
        payload,
        signature,
        settings.STRIPE_WEBHOOK_SECRET,
    )


def expire_checkout_session(session_id):
    """Expire an open Checkout Session after a customer cancels."""

    _stripe_api_key()
    return stripe.checkout.Session.expire(session_id)
