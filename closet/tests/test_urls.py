from django.test import TestCase, SimpleTestCase
from django.urls import reverse, resolve
from closet.views import clothing_items_list, clothing_item_new, clothing_item_page


class TestUrls(SimpleTestCase):

    def test_list_url_resolves(self):
        url = reverse("closet:list")
        self.assertEquals(resolve(url).func, clothing_items_list)

    def test_new_item_url_resolves(self):
        url = reverse("closet:new_item")
        self.assertEquals(resolve(url).func, clothing_item_new)

    def test_page_url_resolves(self):
        url = reverse("closet:page", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func, clothing_item_page)
