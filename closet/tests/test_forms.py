from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from closet.forms import CreateClothingItem
from closet.models import ClothingItem
from django.contrib.auth.models import User
from taggit.models import Tag
import os
import tempfile
import shutil
from PIL import Image
import io

# temporary directory for media files during tests
temp_media = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=temp_media)
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

    def test_form_validation_with_missing_required_fields(self):
        # test without title (required field)
        form_data = {"image": self.test_image}
        form = CreateClothingItem(form_data, {"image": self.test_image})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_validation_with_invalid_image(self):
        # create a non-image text file to test the default ImageField validation
        invalid_file = SimpleUploadedFile(
            "test.txt", b"file_content", content_type="text/plain"
        )

        form_data = {"title": "Invalid File Test", "tags": "test"}
        file_data = {"image": invalid_file}
        form = CreateClothingItem(form_data, file_data)

        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)
        self.assertIn(
            "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
            str(form.errors["image"]),
        )

    def test_file_size_validation(self):
        # test our form's custom file size validation (<5mb) with a local image

        # note: require tester to source for themselves a large image file that is >5mb, store it on their local device, and include the path below here:
        large_image_path = (
            r"C:\Users\Phu Xien\Desktop\pictures_for_testing\Large_Test_Image_14mb.jpg"
        )

        # verify the test image  exists and is large enough
        self.assertTrue(
            os.path.exists(large_image_path),
            f"Large test image not found at {large_image_path}",
        )

        file_size = os.path.getsize(large_image_path)
        self.assertGreater(
            file_size,
            5 * 1024 * 1024,
        )

        # read file content
        with open(large_image_path, "rb") as f:
            large_image_content = f.read()

        # set up large file as variable
        large_file = SimpleUploadedFile(
            name=os.path.basename(large_image_path),
            content=large_image_content,
            content_type="image/jpeg",
        )

        form_data = {"title": "Large File Test", "tags": "test"}
        file_data = {"image": large_file}
        form = CreateClothingItem(form_data, file_data)

        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)
        self.assertIn("File size too large", str(form.errors))

    def tearDown(self):
        shutil.rmtree(temp_media, ignore_errors=True)
        super().tearDown()
