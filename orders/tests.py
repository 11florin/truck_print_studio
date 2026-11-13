from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from shop.models import Category, Product

from .models import Order, OrderItem


class OrderTestDataMixin:
    def create_product(self, **overrides):
        defaults = {
            "category": self.category,
            "name": "Checkout T-shirt",
            "product_type": "tshirt",
            "description": "A checkout test product.",
            "price": Decimal("10.99"),
            "stock": 3,
            "active": True,
        }
        defaults.update(overrides)
        return Product.objects.create(**defaults)

    def checkout_data(self):
        return {
            "email": "customer@example.com",
            "full_name": "Test Customer",
            "address": "1 Test Street",
            "city": "London",
            "postal_code": "SW1A 1AA",
        }


class CheckoutTests(OrderTestDataMixin, TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cab & Driver")
        self.product = self.create_product()

    def add_to_cart(self, quantity=1, size="M"):
        session = self.client.session
        session["cart"] = {f"{self.product.id}:{size}": quantity}
        session.save()

    def test_guest_can_checkout_and_order_keeps_size(self):
        self.add_to_cart(quantity=2, size="XL")

        response = self.client.post(
            reverse("orders:checkout"),
            self.checkout_data(),
        )

        order = Order.objects.get()
        item = OrderItem.objects.get(order=order)
        self.assertRedirects(
            response,
            reverse("orders:success", args=[order.id]),
        )
        self.assertIsNone(order.user)
        self.assertEqual(item.size, "XL")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(order.total, Decimal("21.98"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)
        self.assertEqual(self.client.session["cart"], {})

    def test_checkout_rejects_invalid_input(self):
        self.add_to_cart()

        response = self.client.post(
            reverse("orders:checkout"),
            {**self.checkout_data(), "email": "not-an-email"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_rejects_quantity_above_stock(self):
        self.add_to_cart(quantity=4)

        response = self.client.post(
            reverse("orders:checkout"),
            self.checkout_data(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_empty_cart_can_be_viewed_but_cannot_create_order(self):
        get_response = self.client.get(reverse("orders:checkout"))
        post_response = self.client.post(
            reverse("orders:checkout"),
            self.checkout_data(),
        )

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_guest_checkout_supports_legacy_cart_format(self):
        session = self.client.session
        session["cart"] = {str(self.product.id): 1}
        session.save()

        response = self.client.post(
            reverse("orders:checkout"),
            self.checkout_data(),
        )

        item = OrderItem.objects.get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(item.size, "")


class OrderPermissionTests(OrderTestDataMixin, TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cab & Driver")
        self.product = self.create_product()
        self.owner = User.objects.create_user(
            username="owner",
            password="Strong-password-123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="Strong-password-123",
        )
        self.order = Order.objects.create(
            user=self.owner,
            email="owner@example.com",
            full_name="Order Owner",
            address="1 Test Street",
            city="London",
            postal_code="SW1A 1AA",
            total=self.product.price,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=self.product.price,
            size="M",
        )

    def test_order_history_requires_login(self):
        response = self.client.get(reverse("orders:history"))

        self.assertEqual(response.status_code, 302)

    def test_user_cannot_view_another_users_order(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("orders:detail", args=[self.order.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_owner_can_view_order_history_and_detail(self):
        self.client.force_login(self.owner)

        history_response = self.client.get(reverse("orders:history"))
        detail_response = self.client.get(
            reverse("orders:detail", args=[self.order.id])
        )

        self.assertEqual(history_response.status_code, 200)
        self.assertContains(history_response, f"Order #{self.order.id}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Size: M")

    def test_order_success_requires_recent_order_session(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse("orders:success", args=[self.order.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_view_another_users_order_success(self):
        self.client.force_login(self.other_user)
        session = self.client.session
        session["recent_order_id"] = self.order.id
        session.save()

        response = self.client.get(
            reverse("orders:success", args=[self.order.id])
        )

        self.assertEqual(response.status_code, 404)
