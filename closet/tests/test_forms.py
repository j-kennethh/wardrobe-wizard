from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from closet.forms import CreateClothingItem
from closet.models import ClothingItem
from django.contrib.auth.models import User
from taggit.models import Tag
import os


class CreateClothingItemFormTest(TestCase):
    def setUp(self):
        # create user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=open("media/fallback.jpeg", "rb").read(),
            content_type="image/jpeg",
        )

    def test_form_has_correct_fields(self):
        form = CreateClothingItem()
        self.assertIn("image", form.fields)
        self.assertIn("title", form.fields)
        self.assertIn("tags", form.fields)

    def test_form_widget_attributes(self):
        form = CreateClothingItem()
        # test widget attributes for image
        image_widget = form.fields["image"].widget
        self.assertEqual(image_widget.attrs.get("accept"), "image/*")
        self.assertEqual(image_widget.attrs.get("capture"), "environment")

        # test widget attributes for tags
        tags_widget = form.fields["tags"].widget
        self.assertEqual(
            tags_widget.attrs.get("placeholder"), "Enter tags, separated by commas"
        )

    def test_form_save_with_valid_data(self):
        form_data = {
            "title": "Test Shirt",
            "tags": "casual, summer, cotton",
            "user": self.user,
        }

        file_data = {
            "image": self.test_image,
        }

        form = CreateClothingItem(data=form_data, files=file_data)

        self.assertTrue(form.is_valid())

        clothing_item = form.save(commit=False)
        clothing_item.user = self.user
        clothing_item.save()
        form.save_m2m()  # many to many tags

        self.assertEqual(clothing_item.title, "Test Shirt")
        self.assertEqual(clothing_item.image.name, "test_image.jpg")

        # check tags were saved correctly
        tags = clothing_item.tags.all()
        self.assertEqual(tags.count(), 3)
        self.assertTrue(tags.filter(name="casual").exists())
        self.assertTrue(tags.filter(name="summer").exists())
        self.assertTrue(tags.filter(name="cotton").exists())

    def test_form_with_missing_required_fields(self):
        # test without title (required field)
        form_data = {"image": self.test_image}
        form = CreateClothingItem(form_data, {"image": self.test_image})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_with_invalid_image(self):
        # create a non-image text file
        invalid_file = SimpleUploadedFile(
            "test.txt", b"file_content", content_type="text/plain"
        )

        form_data = {"title": "Invalid File Test", "tags": "test"}
        file_data = {"image": invalid_file}
        form = CreateClothingItem(form_data, file_data)

        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def tearDown(self):
        # clean up the test-created image after each test
        if os.path.exists("media/test_image.jpg"):
            os.remove("media/test_image.jpg")
        super().tearDown()
