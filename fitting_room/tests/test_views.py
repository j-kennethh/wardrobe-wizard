import os
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from fitting_room.models import Look
from closet.models import ClothingItem
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import base64
import tempfile
import shutil


# temporary directory for media files during tests
temp_media = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=temp_media)
class FittingRoomViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.look = Look.objects.create(
            user=self.user,
            title="Test Look",
        )
        self.clothing_item = ClothingItem.objects.create(
            user=self.user, title="Test item", image="test.jpg"
        )

    def test_fitting_room_view_authenticated(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("fitting_room:fitting_room"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fitting_room/fitting_room.html")

    def test_fitting_room_view_unauthenticated(self):
        response = self.client.get(reverse("fitting_room:fitting_room"))
        self.assertRedirects(
            response, f'/users/register/?next={reverse("fitting_room:fitting_room")}'
        )

    def test_fitting_room_POST_valid(self):
        self.client.login(username="testuser", password="12345")

        # create a simple image for testing
        test_image = SimpleUploadedFile(
            "Test.png", b"file_content", content_type="image/png"
        )
        encoded_image = base64.b64encode(test_image.read()).decode("utf-8")
        screenshot_data = f"data:image/png;base64,{encoded_image}"

        response = self.client.post(
            reverse("fitting_room:fitting_room"),
            {"title": "New Look", "screenshot_data": screenshot_data},
        )

        self.assertEqual(response.status_code, 302)  # should redirect to lookbook
        self.assertEqual(Look.objects.count(), 2)  # one from setup and one new
        new_look = Look.objects.latest("created_at")
        self.assertEqual(new_look.title, "New Look")
        self.assertTrue(new_look.image)

    def test_fitting_room_post_invalid(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("fitting_room:fitting_room"),
            {
                "title": "",  # invalid as title cant be empty
            },
        )

        self.assertEqual(response.status_code, 200)  # response should re-render form
        self.assertTrue(response.context["form"].errors)
        self.assertIn("title", response.context["form"].errors)
        self.assertEqual(
            Look.objects.count(), 1
        )  # only the original object should exist

    def test_lookbook_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("fitting_room:lookbook"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fitting_room/lookbook.html")
        self.assertIn("looks", response.context)

    def test_delete_look_view_POST(self):
        self.client.login(username="testuser", password="12345")
        url = reverse("fitting_room:delete_look", args=[self.look.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("fitting_room:lookbook"))
        self.assertEqual(Look.objects.count(), 0)

    def test_delete_look_view_GET(self):
        self.client.login(username="testuser", password="12345")
        url = reverse("fitting_room:delete_look", args=[self.look.id])
        response = self.client.get(url)  # try GET
        self.assertRedirects(response, reverse("fitting_room:lookbook"))
        self.assertEqual(Look.objects.count(), 1)  # Should not delete on GET

    def tearDown(self):
        shutil.rmtree(temp_media, ignore_errors=True)
        super().tearDown()
