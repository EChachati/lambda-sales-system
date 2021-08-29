from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Salesman, SalesmanIndicators


SALESMAN_URL = reverse('salesman:salesman-list')
INDICATOR_URL = reverse('salesman:indicator-list')


class APITests(TestCase):
    def setUp(self):
        self.APIClient = APIClient()

    def test_connection(self):
        """
        Test connection works
        """
        response = self.APIClient.get(SALESMAN_URL)
        response1 = self.APIClient.get(INDICATOR_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response1.status_code, 200)

    def test_create_salesman(self):
        """
        Test Salesman created Successfully
        """
        payload = {
            'identity_card': '12345678',
            'name': 'Test Salesman Name',
            'phone_1': '12345678'
        }
        res = self.APIClient.post(SALESMAN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['identity_card'], payload['identity_card'])
        self.assertEqual(res.data['name'], payload['name'])

    def test_salesman_indicator_exists(self):
        """
        Test Indicator is created when Salesman its created
        """
        payload = {
            'identity_card': '12345678',
            'name': 'Test Salesman Name',
            'phone_1': '12345678'
        }

        res = self.APIClient.post(SALESMAN_URL, payload)
        salesman = Salesman.objects.get(pk=res.data['id'])

        res2 = self.APIClient.get(INDICATOR_URL)
        self.assertNotEqual(res2.data, [])
        self.assertEqual(res2.data[0]['salesman']['name'], salesman.name)
        self.assertEqual(res2.data[0]['salesman']
                         ['identity_card'], salesman.identity_card)

    def test_try_create_fail(self):
        """
        Create Salesman with bad Payload fails
        """
        empty_payload = {}
        xd_payload = {
            'name': '',
            'identity_card': ''
        }

        res = self.APIClient.post(SALESMAN_URL, empty_payload)
        res2 = self.APIClient.post(SALESMAN_URL, xd_payload)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res2.status_code, 400)
