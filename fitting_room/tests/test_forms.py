from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from fitting_room.forms import LookForm
from fitting_room.models import Look
import os


class LookFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.valid_data = {
            "title": "Summer Outfit",
        }
        self.test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"file_content",
            content_type="image/jpg",
        )

    def test_form_fields(self):
        form = LookForm()
        self.assertEqual(list(form.fields.keys()), ["title", "image"])
        self.assertEqual(form.Meta.model, Look)
        self.assertEqual(form.Meta.fields, ["title", "image"])

    def test_form_widget_attributes(self):
        form = LookForm()
        self.assertEqual(form.fields["title"].widget.attrs.get("class"), "form-control")
        self.assertTrue(form.fields["image"].widget.is_hidden)

    def test_form_save_with_valid_data(self):
        form = LookForm(data=self.valid_data, files={"image": self.test_image})
        self.assertTrue(form.is_valid())

        look = form.save(commit=False)
        look.user = self.user
        look.save()

        self.assertEqual(Look.objects.count(), 1)
        self.assertEqual(look.title, "Summer Outfit")
        self.assertTrue(look.image)

    def test_form_validation_with_missing_required_field_title(self):
        # test missing title
        form = LookForm(data={}, files={"image": self.test_image})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["title"], ["This field is required."])

    def test_form_validation_with_missing_optional_field_image(self):
        # test missing image (should be valid since image is not required)
        form = LookForm(data={"title": "No Image Look"}, files={})
        self.assertTrue(form.is_valid())

    def tearDown(self):
        # clean up all Look objects and their associated images
        for look in Look.objects.all():
            if look.image:
                if os.path.isfile(look.image.path):
                    os.remove(look.image.path)
        # clear the database
        Look.objects.all().delete()
