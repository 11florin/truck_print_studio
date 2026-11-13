from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Review, Wishlist


class ShopTestDataMixin:
    def create_product(self, **overrides):
        defaults = {
            "category": self.category,
            "name": "Blue Cab T-shirt",
            "product_type": "tshirt",
            "description": "A lorry design for road transport.",
            "price": Decimal("12.50"),
            "stock": 5,
            "active": True,
            "featured": False,
        }
        defaults.update(overrides)
        return Product.objects.create(**defaults)


class CatalogTests(ShopTestDataMixin, TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cab & Driver")
        self.other_category = Category.objects.create(name="Haulage Life")
        self.product = self.create_product(
            image="products/cab.png",
        )
        self.featured_product = self.create_product(
            name="Featured Motorway Hoodie",
            product_type="hoodie",
            category=self.other_category,
            description="A motorway design for long journeys.",
            featured=True,
        )
        self.inactive_product = self.create_product(
            name="Inactive Mug",
            product_type="mug",
            active=False,
        )

    def test_home_shows_active_featured_products_only(self):
        response = self.client.get(reverse("shop:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.featured_product.name)
        self.assertNotContains(response, self.product.name)
        self.assertNotContains(response, self.inactive_product.name)

    def test_catalog_shows_active_products(self):
        response = self.client.get(reverse("shop:list"))

        self.assertContains(response, self.product.name)
        self.assertContains(response, self.featured_product.name)
        self.assertNotContains(response, self.inactive_product.name)

    def test_category_page_filters_products_by_category(self):
        response = self.client.get(
            reverse("shop:category", args=[self.category.slug])
        )

        self.assertContains(response, self.product.name)
        self.assertNotContains(response, self.featured_product.name)

    def test_search_filters_by_name_and_description(self):
        response = self.client.get(
            reverse("shop:list"),
            {"q": "lorry"},
        )

        self.assertContains(response, self.product.name)
        self.assertNotContains(response, self.featured_product.name)

    def test_catalog_filters_by_category_and_product_type(self):
        response = self.client.get(
            reverse("shop:list"),
            {"category": self.other_category.slug, "type": "hoodie"},
        )

        self.assertContains(response, self.featured_product.name)
        self.assertNotContains(response, self.product.name)

    def test_product_detail_exposes_sizes_for_apparel(self):
        response = self.client.get(
            reverse("shop:detail", args=[self.product.slug])
        )

        self.assertContains(response, 'name="size"')
        self.assertContains(response, "Choose a size")
        self.assertEqual(
            response.context["size_choices"],
            Product.SIZE_CHOICES,
        )

    def test_mug_detail_does_not_expose_sizes(self):
        mug = self.create_product(name="Road Mug", product_type="mug")

        response = self.client.get(reverse("shop:detail", args=[mug.slug]))

        self.assertNotContains(response, 'name="size"')
        self.assertEqual(response.context["size_choices"], ())

    def test_inactive_product_detail_returns_not_found(self):
        inactive = self.create_product(name="Unavailable Design", active=False)

        response = self.client.get(
            reverse("shop:detail", args=[inactive.slug])
        )

        self.assertEqual(response.status_code, 404)


class CartTests(ShopTestDataMixin, TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cab & Driver")
        self.product = self.create_product(image="products/cab.png")

    def test_guest_can_add_product_with_size_to_cart(self):
        response = self.client.post(
            reverse("shop:cart_add", args=[self.product.id]),
            {"size": "M", "quantity": 2, "next": reverse("shop:cart")},
        )

        self.assertRedirects(response, reverse("shop:cart"))
        self.assertEqual(self.client.session["cart"], {f"{self.product.id}:M": 2})

        cart_response = self.client.get(reverse("shop:cart"))
        self.assertContains(cart_response, self.product.name)
        self.assertContains(cart_response, "Size: M")
        self.assertContains(cart_response, 'class="bag-item__image"')

    def test_cart_rejects_invalid_size_and_quantity(self):
        invalid_size = self.client.post(
            reverse("shop:cart_add", args=[self.product.id]),
            {"size": "INVALID", "quantity": 1},
        )
        self.assertRedirects(invalid_size, reverse("shop:cart"))
        self.assertEqual(self.client.session["cart"], {})

        invalid_quantity = self.client.post(
            reverse("shop:cart_add", args=[self.product.id]),
            {"size": "M", "quantity": "not-a-number"},
        )
        self.assertRedirects(invalid_quantity, reverse("shop:cart"))
        self.assertEqual(self.client.session["cart"], {})

    def test_cart_caps_quantity_at_stock(self):
        response = self.client.post(
            reverse("shop:cart_add", args=[self.product.id]),
            {"size": "L", "quantity": 99},
        )

        self.assertRedirects(response, reverse("shop:cart"))
        self.assertEqual(self.client.session["cart"], {f"{self.product.id}:L": 5})

    def test_mug_can_be_added_without_a_size(self):
        mug = self.create_product(name="Road Mug", product_type="mug")

        response = self.client.post(
            reverse("shop:cart_add", args=[mug.id]),
            {"quantity": 1},
        )

        self.assertRedirects(response, reverse("shop:cart"))
        self.assertEqual(self.client.session["cart"], {str(mug.id): 1})

    def test_same_product_can_have_multiple_size_variants(self):
        for size in ("S", "XL"):
            self.client.post(
                reverse("shop:cart_add", args=[self.product.id]),
                {"size": size, "quantity": 1},
            )

        self.assertEqual(
            self.client.session["cart"],
            {f"{self.product.id}:S": 1, f"{self.product.id}:XL": 1},
        )

    def test_cart_uses_safe_fallback_for_external_next_url(self):
        response = self.client.post(
            reverse("shop:cart_add", args=[self.product.id]),
            {
                "size": "M",
                "quantity": 1,
                "next": "https://example.com/unsafe",
            },
        )

        self.assertRedirects(response, reverse("shop:cart"))

    def test_cart_rejects_inactive_or_missing_products(self):
        inactive = self.create_product(name="Inactive Product", active=False)

        inactive_response = self.client.post(
            reverse("shop:cart_add", args=[inactive.id]),
            {"size": "M", "quantity": 1},
        )
        missing_response = self.client.post(
            reverse("shop:cart_add", args=[999999]),
            {"size": "M", "quantity": 1},
        )

        self.assertEqual(inactive_response.status_code, 404)
        self.assertEqual(missing_response.status_code, 404)

    def test_cart_reads_legacy_product_id_format(self):
        session = self.client.session
        session["cart"] = {str(self.product.id): 2}
        session.save()

        response = self.client.get(reverse("shop:cart"))

        self.assertContains(response, f"{self.product.name} x 2")
        self.assertNotContains(response, "Size:")

    def test_cart_remove_removes_selected_variant(self):
        self.client.post(
            reverse("shop:cart_add", args=[self.product.id]),
            {"size": "S", "quantity": 1},
        )

        response = self.client.post(
            reverse("shop:cart_remove", args=[f"{self.product.id}:S"])
        )

        self.assertRedirects(response, reverse("shop:cart"))
        self.assertEqual(self.client.session["cart"], {})


class WishlistAndReviewTests(ShopTestDataMixin, TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cab & Driver")
        self.product = self.create_product()
        self.user = User.objects.create_user(
            username="reviewer",
            password="Strong-password-123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="Strong-password-123",
        )

    def test_wishlist_requires_login_and_can_add_and_remove(self):
        protected_response = self.client.get(reverse("shop:wishlist"))
        self.assertRedirects(
            protected_response,
            f"{reverse('accounts:login')}?next={reverse('shop:wishlist')}",
        )

        self.client.force_login(self.user)
        add_response = self.client.post(
            reverse("shop:wishlist_add", args=[self.product.id])
        )
        self.assertRedirects(
            add_response,
            reverse("shop:detail", args=[self.product.slug]),
        )
        self.assertTrue(
            Wishlist.objects.filter(user=self.user, product=self.product).exists()
        )

        remove_response = self.client.post(
            reverse("shop:wishlist_remove", args=[self.product.id])
        )
        self.assertRedirects(
            remove_response,
            reverse("shop:detail", args=[self.product.slug]),
        )
        self.assertFalse(
            Wishlist.objects.filter(user=self.user, product=self.product).exists()
        )

    def test_adding_same_product_to_wishlist_is_idempotent(self):
        self.client.force_login(self.user)

        self.client.post(reverse("shop:wishlist_add", args=[self.product.id]))
        self.client.post(reverse("shop:wishlist_add", args=[self.product.id]))

        self.assertEqual(
            Wishlist.objects.filter(
                user=self.user,
                product=self.product,
            ).count(),
            1,
        )

    def test_review_create_requires_login_and_validates_rating(self):
        protected_response = self.client.get(
            reverse("shop:review_create", args=[self.product.id])
        )
        self.assertEqual(protected_response.status_code, 302)

        self.client.force_login(self.user)
        invalid_response = self.client.post(
            reverse("shop:review_create", args=[self.product.id]),
            {"rating": "6", "comment": "Invalid rating"},
        )
        self.assertEqual(invalid_response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)

        valid_response = self.client.post(
            reverse("shop:review_create", args=[self.product.id]),
            {"rating": "5", "comment": "Excellent design"},
        )
        self.assertRedirects(
            valid_response,
            reverse("shop:detail", args=[self.product.slug]),
        )
        self.assertTrue(
            Review.objects.filter(
                user=self.user,
                product=self.product,
                rating=5,
            ).exists()
        )

    def test_review_update_and_delete_are_limited_to_owner(self):
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            comment="Good",
        )
        self.client.force_login(self.other_user)

        update_response = self.client.get(
            reverse("shop:review_update", args=[review.id])
        )
        delete_response = self.client.post(
            reverse("shop:review_delete", args=[review.id])
        )

        self.assertEqual(update_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.assertTrue(Review.objects.filter(id=review.id).exists())

    def test_review_owner_can_update_and_delete_review(self):
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            comment="Good",
        )
        self.client.force_login(self.user)

        update_response = self.client.post(
            reverse("shop:review_update", args=[review.id]),
            {"rating": "5", "comment": "Excellent"},
        )
        review.refresh_from_db()
        self.assertRedirects(
            update_response,
            reverse("shop:detail", args=[self.product.slug]),
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excellent")

        delete_response = self.client.post(
            reverse("shop:review_delete", args=[review.id])
        )
        self.assertRedirects(
            delete_response,
            reverse("shop:detail", args=[self.product.slug]),
        )
        self.assertFalse(Review.objects.filter(id=review.id).exists())
