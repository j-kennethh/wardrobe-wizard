from django.test import TestCase
from django.urls import reverse, resolve
from fitting_room import views


class UrlsTest(TestCase):
    def test_fitting_room_url_resolves(self):
        url = reverse("fitting_room:fitting_room")
        self.assertEqual(resolve(url).func, views.fitting_room)

    def test_lookbook_url_resolves(self):
        url = reverse("fitting_room:lookbook")
        self.assertEqual(resolve(url).func, views.lookbook)

    def test_delete_look_url_resolves(self):
        url = reverse("fitting_room:delete_look", args=[1])
        self.assertEqual(resolve(url).func, views.delete_look)
