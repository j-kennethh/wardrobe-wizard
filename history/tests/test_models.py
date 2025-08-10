import os
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from history.models import OutfitHistory
from fitting_room.models import Look
from django.core.exceptions import ValidationError
from django.utils import timezone
import tempfile
import shutil


# temporary directory for media files during tests
temp_media = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=temp_media)
class OutfitHistoryModelTests(TestCase):
    def setUp(self):
        # creating test user
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123"
        )

        # creating test look
        self.look = Look.objects.create(
            user=self.user,
            title="Test Look",
            # other fields can be left unspecified as blank=true
        )

        # creating test outfit_history
        self.outfit_history = OutfitHistory.objects.create(
            user=self.user,
            look=self.look,
            notes="Test notes",
            date=timezone.now().date(),
        )

    def test_outfit_history_creation(self):
        # test that an OutfitHistory object instance is created properly
        self.assertEqual(self.outfit_history.user.username, "testuser")
        self.assertEqual(self.outfit_history.look.title, "Test Look")
        self.assertEqual(self.outfit_history.notes, "Test notes")
        self.assertEqual(self.outfit_history.date, timezone.now().date())

    def test_outfit_history_str_representation(self):
        # Test the __str__ method of OutfitHistory
        expected_str = (
            f"{self.user.username} wore '{self.look.title}' on {timezone.now().date()}"
        )
        self.assertEqual(str(self.outfit_history), expected_str)

    def test_unique_together_constraint(self):
        # test that user can't have multiple outfit logs on the same date
        with self.assertRaises(ValidationError):
            duplicate_outfit = OutfitHistory(
                user=self.user, look=self.look, date=timezone.now().date()
            )
            duplicate_outfit.full_clean()  # This should raise ValidationError

    def test_optional_notes_field(self):
        # test that notes field can be blank or null
        outfit_without_notes = OutfitHistory.objects.create(
            user=self.user,
            look=self.look,
            date=timezone.now().date() - timezone.timedelta(days=1),  # different date
        )
        self.assertIsNone(outfit_without_notes.notes)

    def test_meta_ordering(self):
        # test date descending ordering
        # create another outfit history with earlier date
        earlier_date = timezone.now().date() - timezone.timedelta(days=1)
        OutfitHistory.objects.create(user=self.user, look=self.look, date=earlier_date)

        # get all outfit histories for the user
        histories = OutfitHistory.objects.filter(user=self.user)

        # check ordering (newest first)
        self.assertEqual(histories[0].date, timezone.now().date())
        self.assertEqual(histories[1].date, earlier_date)

    def tearDown(self):
        shutil.rmtree(temp_media, ignore_errors=True)
        super().tearDown()
