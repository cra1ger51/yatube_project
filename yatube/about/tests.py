from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов для приложения about."""
        url_names = (reverse('about:author'), reverse('about:tech'))
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для приложения about."""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
