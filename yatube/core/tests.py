from http import HTTPStatus

from django.test import TestCase, Client


class ViewTestClass(TestCase):
    def test_error_page(self):
        client = Client()
        response = client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
