from datetime import datetime
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import *
import json

ORDER_URL = reverse('order:order-list')
CREATE_OS_URL = reverse('order:create-os')


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

        # Creating Test Client
        res = self.APIClient.post(
            reverse('client:client-list'),
            {
                'name': 'test Client',
                'identity_card': '12345678',
                'address': 'Test Address',
                'phone': '78945656123'
            }
        )

        self.client = Client.objects.get(
            pk=res.data['id']
        )

        # Creating Test Salesman
        res = self.APIClient.post(
            reverse('salesman:salesman-list'),
            {
                'identity_card': '12345678',
                'name': 'Test Salesman Name',
                'phone_1': '12345678'
            }
        )

        self.salesman = Salesman.objects.get(
            pk=res.data['id']
        )

        self.category = sample_category()
        self.product = sample_product()
        self.date = str(datetime.date.today())

        res = self.APIClient.post(ORDER_URL, {
            'salesman': self.salesman.pk,
            'client': self.client.pk,
            'income': '15.00',
            'date': self.date
        })

        self.order = Order.objects.get(
            pk=res.data['id']
        )

    def test_connection(self):

        res1 = self.APIClient.get(ORDER_URL)
        res2 = self.APIClient.get(CREATE_OS_URL)

        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)

    def test_create_sale(self):
        """
        Test Empty Sale correctly created
        """
        payload = {
            'salesman': self.salesman.pk,
            'client': self.client.pk,
            'income': '15.00',
            'date': self.date
        }

        res = self.APIClient.post(ORDER_URL, payload)
        self.assertEqual(res.status_code, 201)

    def test_create_order_incorrect(self):
        """
        Test Order Creation fails with incorrect Payload
        """
        payload1 = {
            # 'salesman': self.salesman.pk,
            'client': self.client.pk,
            'income': '15.00',
            'date': self.date
        }
        payload2 = {
            'salesman': self.salesman.pk,
            # 'client': self.client.pk,
            'income': '15.00',
            'date': self.date
        }

        payload5 = {
            'salesman': '',
            'client': self.client.pk,
            'income': '15.00',
            'date': self.date
        }
        payload6 = {
            'salesman': self.salesman.pk,
            'client': '',
            'income': '15.00',
            'date': self.date
        }

        res1 = self.APIClient.post(ORDER_URL, payload1)
        res2 = self.APIClient.post(ORDER_URL, payload2)
        res5 = self.APIClient.post(ORDER_URL, payload5)
        res6 = self.APIClient.post(ORDER_URL, payload6)

        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res5.status_code, 400)
        self.assertEqual(res6.status_code, 400)

    def test_create_productorder(self):
        """
        Create ProductOrderfor a Order works
        """
        payload = [{
            'product': self.product.pk,
            'order': self.order.pk,
            'quantity': 3,
            'income': '15'
        }]

        res = self.APIClient.post(
            CREATE_OS_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(res.status_code, 201)

    def test_create_productsale_incorrect(self):
        """
        Create productsale with incorrect payload fails
        """

        payload1 = [{
            # 'product': self.product.pk,
            'order': self.order.pk,
            'quantity': 3,
            'income': '15'
        }]

        payload2 = [{
            'product': self.product.pk,
            # 'sale': self.sale.pk,
            'quantity': 3,
            'income': '15'
        }
        ]
        payload4 = [{
            'product': self.product.pk,
            'order': self.order.pk,
            'quantity': 3,
            # 'income': '15'
        }]

        payload5 = [{
            'product': '',
            'order': self.order.pk,
            'quantity': 3,
            'income': '15'
        }]
        payload6 = [{
            'product': self.product.pk,
            'order': '',
            'quantity': 3,
            'income': '15'
        }]
        payload8 = [{
            'product': self.product.pk,
            'order': self.order.pk,
            'quantity': 3,
            'income': ''
        }]

        res1 = self.APIClient.post(
            CREATE_OS_URL,
            data=json.dumps(payload1),
            content_type='application/json')
        res2 = self.APIClient.post(
            CREATE_OS_URL,
            data=json.dumps(payload2),
            content_type='application/json')
        res4 = self.APIClient.post(
            CREATE_OS_URL,
            data=json.dumps(payload4),
            content_type='application/json')
        res5 = self.APIClient.post(
            CREATE_OS_URL,
            data=json.dumps(payload5),
            content_type='application/json')
        res6 = self.APIClient.post(
            CREATE_OS_URL,
            data=json.dumps(payload6),
            content_type='application/json')
        res8 = self.APIClient.post(
            CREATE_OS_URL,
            data=json.dumps(payload8),
            content_type='application/json')

        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res4.status_code, 400)
        self.assertEqual(res5.status_code, 400)
        self.assertEqual(res6.status_code, 400)
        self.assertEqual(res8.status_code, 400)

    def test_create_multiple_product_order_one_post(self):
        """
        Test Creation of multiple ProductOrder objects with one post Works.
        """
        payload = [
            {
                'product': self.product.pk,
                'order': self.order.pk,
                'quantity': 3,
                'income': '12'
            },
            {
                'product': self.product.pk,
                'order': self.order.pk,
                'quantity': 3.02,
                'income': '125'
            }
        ]

        payload2 = [
            {
                'product': self.product.pk,
                'order': self.order.pk,
                'quantity': 3,
                'income': '12'
            }
        ]

        res = self.APIClient.post(
            CREATE_OS_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        res2 = self.APIClient.post(
            CREATE_OS_URL,
            data=json.dumps(payload2),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res2.status_code, 201)
