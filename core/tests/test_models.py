from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

import datetime


def sample_salesman(name="SalesmanName", identity_card="J-303795579"):

    return models.Salesman.objects.create(
        name=name,
        identity_card=identity_card
    )


def sample_client(identity_card="J-12345678-9", name="Business Test Name", address="Address Test 69", phone="+58412-1234567"):
    return models.Client.objects.create(
        identity_card=identity_card,
        name=name,
        address=address,
        phone=phone
    )


def sample_product(category, name="Test Product"):
    return models.Product.objects.create(name=name, category=category)


def sample_sale():
    salesman = sample_salesman()
    client = sample_client()
    return models.Sale.objects.create(
        salesman=salesman,
        client=client
    )


class ModelTest(TestCase):
    """
    Tests for models
    """

    def setUp(self):
        self.category = models.Category.objects.create(name='DefaultName')

    def test_create_user_with_email_success(self):
        """
        User is created using an Email
        """

        email = "test@example.com"
        password = "Password.123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Make sure email is saved lowercased
        """
        email = "Test@ExaMPLE.com"
        password = "Password.123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_with_invalid_email(self):
        """
        Make sure dies not create user with an invalid email
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "Password.123")

    def test_new_salesman(self):
        """
        Create a Salesman
        """
        name = "SalesmanName"
        identity_card = "J-303795579"
        salesman = models.Salesman.objects.create(
            name=name,
            identity_card=identity_card,
        )

        self.assertEqual(salesman.name, name)

    def test_new_client_(self):
        """
        Create a client
        """

        identity_card = "J-12345678-9"
        name = "Business Test Name"
        address = "Once whwere a shop that put to sea the name of the ship was the belly of tea"
        phone = "+58412-1234567"

        client = models.Client.objects.create(
            identity_card=identity_card,
            name=name,
            address=address,
            phone=phone
        )

        self.assertEqual(client.name, name)

    def test_new_category(self):
        """
        Create a new Category
        """
        name = "Test Category"
        category = models.Category.objects.create(name=name)

        self.assertEqual(category.name, name)

    def test_new_product(self):
        """
        Create a new Product
        """
        name = 'new_product'
        category = models.Category.objects.create(name="category")
        product = models.Product.objects.create(name=name, category=category)

        self.assertEqual(product.category, category)
        self.assertEqual(product.name, name)

    def test_new_barcode(self):
        """
        Create a new Barcode
        """
        name = 'new_product'
        category = models.Category.objects.create(name="category")
        product = models.Product.objects.create(name=name, category=category)

        code = "759123456789"
        barcode = models.Barcode.objects.create(
            code=code,
            product=product
        )
        self.assertEqual(barcode.code, code)
        self.assertEqual(barcode.product, product)

    def test_new_sale(self):
        """
        Create a new sale
        """
        salesman = sample_salesman()
        client = sample_client()
        sale = models.Sale.objects.create(
            salesman=salesman,
            client=client
        )

        self.assertEqual(sale.date, datetime.date.today())
        self.assertEqual(sale.salesman, salesman)
        self.assertEqual(sale.client, client)

    def test_new_product_sale(self):
        """
        Create ProductSale
        """
        category = self.category
        product = sample_product(category=category)
        product.price_1 = 5.00
        quantity = 5
        sale = sample_sale()

        productSale = models.ProductSale.objects.create(
            product=product,
            sale=sale,
            quantity=quantity,
            income=product.price_1*quantity
        )

        self.assertEqual(productSale.product, product)
