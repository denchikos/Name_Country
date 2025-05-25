from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class NameCountryViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_name_required(self):
        response = self.client.get("/api/name/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json().get("error", "").lower())

    def test_valid_name(self):
        response = self.client.get("/api/name/?name=olga")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertIn("countries", response.data)


class CountryDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_code_required(self):
        response = self.client.get("/api/country/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.json().get("error", "").lower())

    def test_invalid_country_code(self):
        response = self.client.get("/api/country/?code=XXX")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_country_code(self):
        response = self.client.get("/api/country/?code=UA")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertIn("code", response.data)