from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    def test_register_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new-user",
                "password1": "Strong-password-123",
                "password2": "Strong-password-123",
            },
        )

        self.assertRedirects(response, reverse("shop:home"))
        self.assertTrue(User.objects.filter(username="new-user").exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new-user",
                "password1": "Strong-password-123",
                "password2": "Different-password-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn")
        self.assertFalse(User.objects.filter(username="new-user").exists())

    def test_login_and_logout(self):
        user = User.objects.create_user(
            username="customer",
            password="Strong-password-123",
        )

        login_response = self.client.post(
            reverse("accounts:login"),
            {"username": user.username, "password": "Strong-password-123"},
        )
        self.assertRedirects(login_response, reverse("shop:home"))

        logout_response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(logout_response, reverse("shop:home"))

    def test_register_rejects_duplicate_username(self):
        User.objects.create_user(
            username="existing",
            password="Strong-password-123",
        )

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "existing",
                "password1": "Strong-password-123",
                "password2": "Strong-password-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="existing").count(), 1)

    def test_login_rejects_invalid_password(self):
        user = User.objects.create_user(
            username="customer",
            password="Strong-password-123",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"username": user.username, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:profile')}",
        )
