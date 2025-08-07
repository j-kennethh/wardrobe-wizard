import os
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from fitting_room.models import Look
from django.core.files.uploadedfile import SimpleUploadedFile
import base64
import tempfile
import shutil


# temporary directory for media files during tests
temp_media = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=temp_media)
class LookModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.look = Look.objects.create(
            user=self.user,
            title="Test Look",
        )

    def test_look_creation(self):

        self.assertEqual(self.look.title, "Test Look")
        self.assertEqual(self.look.user, self.user)
        self.assertTrue(self.look.image)  # default image

    def test_create_from_screenshot(self):
        # create a simple base64 encoded image
        test_image = SimpleUploadedFile(
            "test.png", b"file_content", content_type="image/png"
        )
        encoded_image = base64.b64encode(test_image.read()).decode("utf-8")
        screenshot_data = f"data:image/png;base64,{encoded_image}"

        self.look.create_from_screenshot(screenshot_data)
        self.assertTrue(self.look.image)

    def test_str_method(self):
        self.assertEqual(str(self.look), f"{self.user.username}'s Look: Test Look")

    # def tearDown(self):
    #     # clean up media files created during testing
    #     looks = Look.objects.all()

    #     # delete associated image files if they exist
    #     for look in looks:
    #         if look.image:
    #             if os.path.isfile(look.image.path):
    #                 os.remove(look.image.path)

    #     # clear the test database
    #     super().tearDown()

    def tearDown(self):
        shutil.rmtree(temp_media, ignore_errors=True)
        super().tearDown()
