from django.test import SimpleTestCase
from django.urls import reverse, resolve
from history import views


class HistoryTestUrls(SimpleTestCase):
    def test_history_url_resolves(self):
        url = reverse("history:history")

        self.assertEqual(resolve(url).func, views.history)
        self.assertEqual(resolve(url).route, "history/")

    def test_log_outfit_url_resolves(self):
        url = reverse("history:log_outfit")
        self.assertEqual(resolve(url).func, views.log_outfit)
        self.assertEqual(resolve(url).route, "history/log/")

    def test_url_status_codes(self):
        # test expected status codes
        urls = [
            ("history:history", 302),  # due to @login_required
            ("history:log_outfit", 302),  # due to @login_required
        ]

        for name, expected_code in urls:
            with self.subTest(url_name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, expected_code)
