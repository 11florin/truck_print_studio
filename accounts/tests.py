from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


class AuthenticationTests(TestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_sends_email(self):
        user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="Strong-password-123",
        )

        response = self.client.post(
            reverse("accounts:password_reset"),
            {"email": user.email},
        )

        self.assertRedirects(
            response,
            reverse("accounts:password_reset_done"),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reset", mail.outbox[0].subject.lower())

    def test_register_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new-user",
                "email": "new-user@example.com",
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
                "email": "new-user@example.com",
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
                "email": "existing@example.com",
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

    def test_authenticated_user_cannot_open_login_or_register_pages(self):
        user = User.objects.create_user(
            username="customer",
            password="Strong-password-123",
        )
        self.client.force_login(user)

        self.assertRedirects(
            self.client.get(reverse("accounts:login")),
            reverse("shop:home"),
        )
        self.assertRedirects(
            self.client.get(reverse("accounts:register")),
            reverse("shop:home"),
        )

    def test_regular_user_cannot_access_admin_data_store(self):
        user = User.objects.create_user(
            username="customer",
            password="Strong-password-123",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
