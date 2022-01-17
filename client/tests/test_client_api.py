from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Client, ClientIndicator
import pdb

CLIENT_URL = reverse('client:client-list')
INDICATOR_URL = reverse('client:indicator-list')


class APITests(TestCase):
    def setUp(self):
        self.APIClient = APIClient()

    def test_connection(self):
        """
        Test Connection works
        """
        res1 = self.APIClient.get(CLIENT_URL)
        res2 = self.APIClient.get(INDICATOR_URL)

        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)

    def test_create_client(self):
        """
        Test Client created Successfully
        """
        payload = {
            'name': 'test Client',
            'identity_card': '12345678',
            'address': 'Test Address',
            'phone': '78945656123'
        }

        res = self.APIClient.post(CLIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['identity_card'], payload['identity_card'])
        self.assertEqual(res.data['name'], payload['name'])

    def test_client_indicator_exists(self):
        """
        test Indicator is created when Client its created
        """
        payload = {
            'name': 'test Client',
            'identity_card': '12345678',
            'address': 'Test Address',
            'phone': '78945656123'
        }

        res = self.APIClient.post(CLIENT_URL, payload)
        client = Client.objects.get(pk=res.data['id'])
        res2 = self.APIClient.get(INDICATOR_URL)

        self.assertNotEqual(res2.data, [])
        self.assertEqual(
            res2.data['results'][0]['client']['name'],
            client.name
        )
        self.assertEqual(
            res2.data['results'][0]['client']['identity_card'],
            client.identity_card
        )

    def test_create_fails(self):
        """
        Create Client with bad Payload fails
        """

        payload1 = {}
        payload2 = {
            'name': '',
            'identity_card': '12345678',
            'address': 'Test Address',
            'phone': '78945656123'
        }
        payload3 = {
            'name': 'test Client',
            'identity_card': '',
            'address': 'Test Address',
            'phone': '78945656123'
        }
        payload4 = {
            'name': 'test Client',
            'identity_card': '12345678',
            'address': '',
            'phone': '78945656123'
        }
        payload5 = {
            'name': 'test Client',
            'identity_card': '12345678',
            'address': 'Test Address',
            'phone': ''
        }
        payload6 = payload2 = {
            # 'name': 'test Client',
            'identity_card': '12345678',
            'address': 'Test Address',
            'phone': '78945656123'
        }
        payload7 = {
            'name': 'test Client',
            # 'identity_card': '12345678',
            'address': 'Test Address',
            'phone': '78945656123'
        }
        payload8 = {
            'name': 'test Client',
            'identity_card': '12345678',
            # 'address': 'Test Address',
            'phone': '78945656123'
        }
        payload9 = {
            'name': 'test Client',
            'identity_card': '12345678',
            'address': 'Test Address',
            # 'phone': '78945656123'
        }

        res1 = self.APIClient.post(CLIENT_URL, payload1)
        res2 = self.APIClient.post(CLIENT_URL, payload2)
        res3 = self.APIClient.post(CLIENT_URL, payload3)
        res4 = self.APIClient.post(CLIENT_URL, payload4)
        res5 = self.APIClient.post(CLIENT_URL, payload5)
        res6 = self.APIClient.post(CLIENT_URL, payload6)
        res7 = self.APIClient.post(CLIENT_URL, payload7)
        res8 = self.APIClient.post(CLIENT_URL, payload8)
        res9 = self.APIClient.post(CLIENT_URL, payload9)

        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res3.status_code, 400)
        self.assertEqual(res4.status_code, 400)
        self.assertEqual(res5.status_code, 400)
        self.assertEqual(res6.status_code, 400)
        self.assertEqual(res7.status_code, 400)
        self.assertEqual(res8.status_code, 400)
        self.assertEqual(res9.status_code, 400)
