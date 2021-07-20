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
