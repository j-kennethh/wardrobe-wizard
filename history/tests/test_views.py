from datetime import date
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from history.models import OutfitHistory
from fitting_room.models import Look
from history.forms import OutfitHistoryForm
from django.utils import timezone
import os
import tempfile
import shutil


# temporary directory for media files during tests
temp_media = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=temp_media)
class HistoryTestViews(TestCase):
    def setUp(self):
        # creating test user
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client = Client()
        self.client.login(username="testuser", password="12345")

        # creating test look
        self.look = Look.objects.create(
            user=self.user,
            title="Test Look",
            # other fields can be left unspecified as blank=true
        )

        # creating test outfit_history
        self.history_entry = OutfitHistory.objects.create(
            user=self.user,
            look=self.look,
            notes="Test notes",
            date=timezone.now().date(),
        )

    def test_history_view_authenticated(self):
        # test views.history returns 200 and shows user's entries
        response = self.client.get(reverse("history:history"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "history/history.html")
        self.assertContains(response, "Test notes")
        self.assertEqual(len(response.context["entries"]), 1)
        self.assertEqual(response.context["entries"][0], self.history_entry)

    def test_history_view_unauthenticated(self):
        # test history view redirects to registration pagewhen not logged in
        self.client.logout()
        response = self.client.get(reverse("history:history"))
        self.assertEqual(response.status_code, 302)
        # check redirect is to registration page
        self.assertRedirects(response, f"/users/register/?next=/history/")

    def test_log_outfit_view_GET(self):
        # test log_outfit GET returns form with user's looks
        response = self.client.get(reverse("history:log_outfit"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "history/log_outfit.html")
        self.assertIsInstance(response.context["form"], OutfitHistoryForm)
        # verify the look queryset is filtered to user's looks
        self.assertEqual(
            list(response.context["form"].fields["look"].queryset), [self.look]
        )

    def test_log_outfit_view_POST_valid(self):
        # test log_outfit POST with valid data creates entry
        data = {
            "look": self.look.id,
            "notes": "New test entry",
            "user": self.user,
            "date": date(2025, 1, 1),  # Fixed test date
        }
        response = self.client.post(reverse("history:log_outfit"), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("history:history"))
        self.assertEqual(OutfitHistory.objects.count(), 2)  # 1 from setUp + new one

    def test_log_outfit_view_POST_invalid(self):
        # test log_outfit POST with invalid data shows form with errors
        data = {}  # empty form data
        response = self.client.post(reverse("history:log_outfit"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "history/log_outfit.html")
        self.assertTrue(response.context["form"].errors)

    def test_log_outfit_view_unauthenticated(self):
        # test log_outfit view redirects when not logged in
        self.client.logout()
        response = self.client.get(reverse("history:log_outfit"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/users/register/?next=/history/log/")

    def test_log_outfit_foreign_look_prevention(self):
        # test user can't log a look that doesn't belong to them

        # create another user and their look
        other_user = User.objects.create_user(username="otheruser", password="123")
        other_look = Look.objects.create(
            user=other_user,
            title="Other Look",
        )

        # create data to log the other user's look
        data = {
            "look": other_look.id,
            "date": date(2025, 1, 2),  # required field from model
            "notes": "Should fail validation",
            "user": other_user,
        }

        # To test both GET and POST scenarios:
        # test that the other_look doesn't appear in the form's look choices
        response = self.client.get(reverse("history:log_outfit"))
        form = response.context["form"]
        self.assertNotIn(other_look, form.fields["look"].queryset)

        # test that POST with other_look fails validation
        response = self.client.post(reverse("history:log_outfit"), data)
        # user should remain on the form page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "history/log_outfit.html")
        # should show up as validation error for the look field
        self.assertTrue(response.context["form"].errors)
        self.assertIn("look", response.context["form"].errors)
        self.assertIn(
            "Select a valid choice.", str(response.context["form"].errors["look"])
        )

        # verify no new entry was created
        self.assertEqual(OutfitHistory.objects.count(), 1)  # the one from setUp

    def tearDown(self):
        shutil.rmtree(temp_media, ignore_errors=True)
        super().tearDown()
