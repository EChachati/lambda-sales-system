from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Category, Barcode

PRODUCT_URL = reverse('product:product-list')
CATEGORY_URL = reverse('product:category-list')
BARCODE_URL = reverse('product:barcode-list')


def sample_category():
    return Category.objects.create(name='test')


def sample_product(**params):
    defaults = {
        'name': 'Test',
        'description': 'Test Description',
        'presentation': 'und',
        'cost': '1.00',
        'price_1': '2.00',
        'price_2': '3.00',
        'price_3': '4.00',
        'category': sample_category()
    }

    defaults.update(params)

    return Product.objects.create(**defaults)


class APITests(TestCase):
    def setUp(self):
        self.APIClient = APIClient()

    def test_connection(self):
        """
        Test Connection is made
        """
        res1 = self.APIClient.get(PRODUCT_URL)
        res2 = self.APIClient.get(CATEGORY_URL)
        res3 = self.APIClient.get(BARCODE_URL)

        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res3.status_code, 200)

    def test_create_category(self):
        """
        Test Category correctly created.
        """
        payload = {
            'name': 'test category',
        }

        res = self.APIClient.post(CATEGORY_URL, payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['name'], payload['name'])

    def test_category_incorrect_payload(self):
        """
        Test category creation fails with incorrect Payload
        """

        payload_1 = {'name': ''}
        payload_2 = {}
        payload_3 = {'xd': 'xdd'}

        res1 = self.APIClient.post(CATEGORY_URL, payload_1)
        res2 = self.APIClient.post(CATEGORY_URL, payload_2)
        res3 = self.APIClient.post(CATEGORY_URL, payload_3)

        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res3.status_code, 400)

    def test_create_product(self):
        """
        Test Product correctly created.
        """

        payload = {
            'name': 'Test',
            'description': 'Test Description',
            'presentation': 'und',
            'cost': '1.00',
            'price_1': '2.00',
            'price_2': '3.00',
            'price_3': '4.00',
            'category': sample_category().pk
        }

        res = self.client.post(PRODUCT_URL, payload)
        self.assertEqual(res.status_code, 201)

    def test_create_product_incorrect(self):
        """
        Test Product creation fails with incorrect payload
        """

        payload1 = {
            'name': 'Test',
            'description': 'Test Description',
            'presentation': 'und',
            'cost': '1.00',
            'price_1': '2.00',
            'price_2': '3.00',
            'price_3': '4.00',
        }

        payload2 = {
            # 'name': 'Test',
            'description': 'Test Description',
            'presentation': 'und',
            'cost': '1.00',
            'price_1': '2.00',
            'price_2': '3.00',
            'price_3': '4.00',
            'category': sample_category().pk
        }

        payload3 = {
        }
        payload4 = {
            'name': '',
            'description': 'Test Description',
            'presentation': 'und',
            'cost': '1.00',
            'price_1': '2.00',
            'price_2': '3.00',
            'price_3': '4.00',
            'category': sample_category().pk
        }

        payload6 = {
            'name': 'Test',
            'description': 'Test Description',
            'presentation': 'und',
            'cost': '1.00',
            'price_1': '2.00',
            'price_2': '3.00',
            'price_3': '4.00',
            'category': ''
        }

        res1 = self.APIClient.post(PRODUCT_URL, payload1)
        res2 = self.APIClient.post(PRODUCT_URL, payload2)
        res3 = self.APIClient.post(PRODUCT_URL, payload3)
        res4 = self.APIClient.post(PRODUCT_URL, payload4)
        res6 = self.APIClient.post(PRODUCT_URL, payload6)

        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res3.status_code, 400)
        self.assertEqual(res4.status_code, 400)
        self.assertEqual(res6.status_code, 400)

    def test_create_barcode(self):
        """
        Test Create Barcode created.
        """
        payload = {
            'code': '789456123',
            'product': sample_product().pk,
            'description': 'Test description xddd'
        }

        res1 = self.APIClient.post(BARCODE_URL, payload)
        self.assertEqual(res1.status_code, 201)

    def test_create_barcode_incorrect(self):
        """
        Test Create Barcode Incorrect fails
        """
        payload1 = {
            'code': '',
            'product': sample_product().pk,
            'description': 'Test description xddd'
        }
        payload2 = {
            #    'code': '789456123',
            'product': sample_product().pk,
            'description': 'Test description xddd'
        }
        payload3 = {
            'code': '789456123',
            #    'product': sample_product().pk,
            'description': 'Test description xddd'
        }
        payload4 = {
            'code': '789456123',
            'product': '',
            'description': 'Test description xddd'
        }
        res1 = self.APIClient.post(BARCODE_URL, payload1)
        res2 = self.APIClient.post(BARCODE_URL, payload2)
        res3 = self.APIClient.post(BARCODE_URL, payload3)
        res4 = self.APIClient.post(BARCODE_URL, payload4)

        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res3.status_code, 400)
        self.assertEqual(res4.status_code, 400)
