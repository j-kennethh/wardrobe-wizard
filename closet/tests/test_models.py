from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from taggit.models import Tag
from closet.models import ClothingItem
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import tempfile
import shutil


# temporary directory for media files during tests
temp_media = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=temp_media)
class ClothingItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create user object used by all test methods
        cls.user = User.objects.create_user(username="testuser", password="12345")
        # create file (for testing purposes, copy the fallback.jpeg image)
        cls.test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=open("media/fallback.jpeg", "rb").read(),
            content_type="image/jpeg",
        )

    def tearDown(self):
        shutil.rmtree(temp_media, ignore_errors=True)
        super().tearDown()

    def test_clothing_item_creation(self):
        # test creation of ClothingItem
        item = ClothingItem.objects.create(
            title="Test Shirt", image=self.test_image, user=self.user
        )
        self.assertEqual(item.title, "Test Shirt")
        self.assertEqual(item.user.username, "testuser")
        self.assertIsNotNone(item.date)
        self.assertEqual(item.slug, "")

    def test_title_max_length(self):
        # test that title max_length is 75
        max_length = ClothingItem._meta.get_field("title").max_length
        self.assertEqual(max_length, 75)

    def test_default_image(self):
        # test that default image is used when none is provided
        item = ClothingItem.objects.create(title="Test Default Image", user=self.user)
        self.assertEqual(item.image.name, "fallback.jpeg")

    def test_user_relationship(self):
        # test the user foreign key relationship
        item = ClothingItem.objects.create(title="Test Relationship", user=self.user)
        self.assertEqual(item.user, self.user)
        self.assertEqual(self.user.clothingitem_set.first(), item)

    def test_string_representation(self):
        # test the __str__ method
        item = ClothingItem.objects.create(title="Test String", user=self.user)
        self.assertEqual(str(item), "Test String")

    def test_tags_functionality(self):
        # test that tags can be added and validated
        item = ClothingItem.objects.create(title="Test Tags", user=self.user)
        item.tags.add("summer", "casual", "red")
        self.assertEqual(item.tags.count(), 3)
        self.assertIn("summer", item.tags.values_list("name", flat=True))

    def test_slug_field_blank(self):
        # test that slug field is blank by default
        item = ClothingItem.objects.create(title="Test Slug", user=self.user)
        self.assertEqual(item.slug, "")
