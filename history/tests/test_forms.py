import os
from django import forms
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from fitting_room.models import Look
from history.forms import OutfitHistoryForm
from history.models import OutfitHistory
from django.contrib.auth.models import User
from datetime import date
import uuid
import tempfile
import shutil


# temporary directory for media files during tests
temp_media = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=temp_media)
class OutfitHistoryFormTest(TestCase):
    def setUp(self):
        # create user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.test_image = SimpleUploadedFile(
            name=f"test_look_{uuid.uuid4()}.png",
            content=b"simple image content",
            content_type="image/png",
        )

        # create test look
        self.look = Look.objects.create(
            user=self.user, title="Test Look", image=self.test_image
        )

        # store the valid data
        self.valid_data = {
            "look": self.look.id,
            "date": date.today(),
            "notes": "Test notes",
        }

    def test_form_has_correct_fields(self):
        form = OutfitHistoryForm()
        self.assertIn("look", form.fields)
        self.assertIn("date", form.fields)
        self.assertIn("notes", form.fields)

    def test_form_widgets(self):
        form = OutfitHistoryForm()
        date_widget = form.fields["date"].widget

        # test look field widget
        self.assertEqual(form.fields["look"].widget.attrs["class"], "form-select")

        # test date field widget
        self.assertEqual(
            form.fields["date"].widget.input_type, "date"
        )  # checking by input_type instead of attrs[] as DateInput <: Input widget, so type="date" is actually set via the widget's input_type property, not through the attrs dictionary

        # test notes field widget
        self.assertEqual(form.fields["notes"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["notes"].widget.attrs["rows"], 2)

    def test_form_validation_with_valid_data(self):
        form = OutfitHistoryForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_validation_with_missing_required_field_look(self):
        # missing look
        data = self.valid_data.copy()
        data.pop("look")
        form = OutfitHistoryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("look", form.errors)

    def test_form_validation_with_missing_required_field_date(self):
        # test missing date
        data = self.valid_data.copy()
        data.pop("date")
        form = OutfitHistoryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_form_validation_with_optional_notes(self):
        data = self.valid_data.copy()
        data["notes"] = ""
        form = OutfitHistoryForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        form = OutfitHistoryForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

        # save with commit=False to add user later, mimicking the history.view.log_outfit()
        outfit = form.save(commit=False)
        outfit.user = self.user
        outfit.save()

        # verify the saved object
        self.assertEqual(OutfitHistory.objects.count(), 1)
        saved_outfit = OutfitHistory.objects.first()
        self.assertEqual(saved_outfit.look, self.look)
        self.assertEqual(saved_outfit.date, self.valid_data["date"])
        self.assertEqual(saved_outfit.notes, self.valid_data["notes"])
        self.assertEqual(saved_outfit.user, self.user)

    def test_look_queryset_filtering_in_view(self):
        # Test that the form only shows looks belonging to the current user

        # Create another user and look
        other_user = User.objects.create_user(
            username="otheruser", password="testpass1234"
        )
        other_look = Look.objects.create(
            user=other_user, title="Other Look", image=self.test_image
        )

        # Initialize form
        form = OutfitHistoryForm()

        # at first, queryset includes all looks in test db
        self.assertEqual(form.fields["look"].queryset.count(), 2)  # No user context

        # Simulate how the view sets the queryset
        form.fields["look"].queryset = Look.objects.filter(
            user=self.user
        )  # The queryset should only include the current user's looks
        self.assertEqual(form.fields["look"].queryset.count(), 1)
        self.assertEqual(form.fields["look"].queryset.first(), self.look)
        self.assertNotIn(other_look, form.fields["look"].queryset.all())

    def tearDown(self):
        shutil.rmtree(temp_media, ignore_errors=True)
        super().tearDown()
