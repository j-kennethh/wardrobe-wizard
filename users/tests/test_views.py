from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.logout_url = reverse("users:logout")
        # Create existing user
        self.test_user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        # Set up new user
        self.valid_register_data = {
            "username": "newuser",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }
        self.valid_login_data = {"username": "testuser", "password": "testpass123"}

    def test_register_view_GET(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
        self.assertIsInstance(response.context["form"], UserCreationForm)

    def test_register_view_POST_valid(self):
        response = self.client.post(self.register_url, data=self.valid_register_data)
        self.assertEqual(
            response.status_code, 302  # shld redirect after successful registration
        )
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_view_POST_invalid(self):
        invalid_data = self.valid_register_data.copy()
        invalid_data["password2"] = "wrongpassword"
        response = self.client.post(self.register_url, data=invalid_data)
        self.assertEqual(response.status_code, 200)  # Should re-render form with errors
        self.assertFalse(User.objects.filter(username="newuser").exists())
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("password2", form.errors)
        self.assertEqual(
            form.errors["password2"][0],
            "The two password fields didn’t match.",  # curly apostrophe
        )

    def test_login_view_GET(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")
        self.assertIsInstance(response.context["form"], AuthenticationForm)

    def test_login_view_POST_valid(self):
        response = self.client.post(self.login_url, data=self.valid_login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_login_view_POST_valid_with_next(self):
        next_url = reverse("closet:list")
        data = self.valid_login_data.copy()
        data["next"] = next_url
        response = self.client.post(self.login_url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, next_url)

    def test_login_view_POST_invalid(self):
        invalid_data = self.valid_login_data.copy()
        invalid_data["password"] = "wrongpassword"
        response = self.client.post(self.login_url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("__all__", form.errors)
        self.assertEqual(
            form.errors["__all__"][0],
            "Please enter a correct username and password. Note that both fields may be case-sensitive.",
        )

    def test_logout_view_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.logout_url, follow=True)
        self.assertEqual(
            response.status_code,
            200,
            # not redirect because the closet:list that is redirected to has @login_required, so we follow all the way to the final destination which is the register page
        )
        # check the final URL after all redirects
        self.assertEqual(response.request["PATH_INFO"], reverse("users:register"))
        self.assertFalse("_auth_user_id" in self.client.session)
