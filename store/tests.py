from django.test import TestCase
from django.urls import reverse

class HomePageTests(TestCase):
    def test_homepage_status_code(self):
        response = self.client.get(reverse('home'))  # або '/' якщо не використовуєш name в url
        self.assertEqual(response.status_code, 200)
