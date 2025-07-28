from django.test import TestCase, Client
from django.urls import reverse
from closet.models import ClothingItem, User
import json


class TestViews(TestCase):
    # login as view has @login_required decorator
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client = Client()
        self.client.login(username="testuser", password="12345")
        self.list_url = reverse("closet:list")

        # setting up for clothing_item_page
        self.clothing_item = ClothingItem.objects.create(
            id=1,
            user=self.user,
            title="test",
        )
        self.page_url = reverse("closet:page", kwargs={"pk": 1})

        self.new_item_url = reverse("closet:new_item")

    def test_clothing_item_list_GET(self):
        response = self.client.get(self.list_url)

        self.assertEquals(response.status_code, 200)

        # more than 1 template referenced
        self.assertTemplateUsed(response, "closet/clothing_items_list.html")
        self.assertTemplateUsed(response, "layout.html")

    def test_clothing_item_page_GET(self):
        response = self.client.get(self.page_url)

        self.assertEquals(response.status_code, 200)

        # check for correct item saving
        self.assertEquals(ClothingItem.objects.get(id=1).title, "test")

        # more than 1 template referenced
        self.assertTemplateUsed(response, "closet/clothing_item_page.html")
        self.assertTemplateUsed(response, "layout.html")

    def test_clothing_item_new_POST(self):
        response = self.client.get(self.new_item_url)

        self.assertEquals(response.status_code, 200)

        # more than 1 template referenced
        self.assertTemplateUsed(response, "closet/new_item.html")
        self.assertTemplateUsed(response, "layout.html")
