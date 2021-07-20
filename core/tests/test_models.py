from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class ModelTest(TestCase):
    """
    Tests for models
    """

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
