"""Order-related email notifications."""

from django.conf import settings
from django.core.mail import send_mail


def send_order_confirmation(order):
    """Send payment and order details to the customer."""

    items = order.items.select_related("product").all()
    item_lines = "\n".join(
        f"- {item.product.name} x {item.quantity}"
        f"{f' (Size: {item.size})' if item.size else ''}"
        f" - £{item.price:.2f}"
        for item in items
    )
    transaction = order.stripe_payment_intent_id or "Pending confirmation"
    body = (
        f"Thank you for your order, {order.full_name}.\n\n"
        f"Order number: #{order.id}\n"
        f"Payment status: {order.get_status_display()}\n"
        f"Transaction number: {transaction}\n"
        f"Total: £{order.total:.2f}\n\n"
        f"Items:\n{item_lines}\n\n"
        "We will process your order shortly.\n"
        "Truck Print Studio"
    )
    return send_mail(
        subject=f"Order confirmation #{order.id}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=False,
    )
