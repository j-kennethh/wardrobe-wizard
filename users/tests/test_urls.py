from django.test import SimpleTestCase
from django.urls import reverse, resolve
from users.views import register_view, login_view, logout_view


class TestUrls(SimpleTestCase):
    def test_register_url_resolves(self):
        url = reverse("users:register")

        self.assertEqual(resolve(url).func, register_view)
        self.assertEqual(resolve(url).route, "users/register/")

    def test_login_url_resolves(self):
        url = reverse("users:login")
        self.assertEqual(resolve(url).func, login_view)
        self.assertEqual(resolve(url).route, "users/login/")

    def test_logout_url_resolves(self):
        url = reverse("users:logout")
        self.assertEqual(resolve(url).func, logout_view)
        self.assertEqual(resolve(url).route, "users/logout/")

    def test_url_status_codes(self):
        # test expected status codes
        urls = [
            ("users:register", 200),
            ("users:login", 200),
            ("users:logout", 302),  # redirects
        ]

        for name, expected_code in urls:
            with self.subTest(url_name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, expected_code)
