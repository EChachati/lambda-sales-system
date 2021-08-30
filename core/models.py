from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings

import datetime


class UserManager(BaseUserManager):
    """
    Manager For Users
    """

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Please Provide an Email")

        user = self.model(
            email=email.lower(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Personalized model for Users support login with Email
    """

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    identity_card = models.CharField(max_length=12, default='None')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Salesman(models.Model):
    """
    Salesman Model
    """
    identity_card = models.CharField(max_length=15, blank=False)
    name = models.CharField(max_length=50, blank=False)

    image = models.ImageField(
        upload_to='salesman',
        blank=True,
        null=True
    )
    phone_1 = models.CharField(max_length=15, blank=True)
    phone_2 = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    """
    Client Model
    """
    identity_card = models.CharField(max_length=15, blank=False)
    name = models.CharField(max_length=50, blank=False)
    image = models.ImageField(
        upload_to='client',
        blank=True,
        null=True
    )
    address = models.CharField(max_length=255, blank=False)
    phone = models.CharField(max_length=15, blank=False)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Product Category

    In case you want to delete a Category
    if you have a product in that category you will not be able to delete it
    """
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product Item Model

    FK -> Category
    """
    name = models.CharField(max_length=50, blank=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT
    )
    description = models.CharField(max_length=144, blank=True)
    presentation = models.CharField(max_length=3, blank=True)
    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    price_1 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    price_2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    price_3 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    brand = models.CharField(max_length=32, blank=True)

    image = models.ImageField(
        upload_to='product',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class Barcode(models.Model):
    """
    Product Barcodes

    FK -> Product
    """
    product = models.ForeignKey(
        Product,
        related_name="barcode",
        on_delete=models.CASCADE
    )
    code = models.CharField(max_length=32, blank=False)
    description = models.CharField(max_length=32, blank=False)

    def __str__(self):
        return self.code


class Sale(models.Model):
    """
    Sales
    """

    salesman = models.ForeignKey(
        Salesman,
        on_delete=models.RESTRICT
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.RESTRICT
    )
    income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    product = models.ManyToManyField(
        Product,
        through='ProductSale'
    )
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return str(self.id)


class ProductSale(models.Model):
    """
    Table in between Products per Sale
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    sale = models.ForeignKey(
        Sale, on_delete=models.CASCADE
    )
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    income = models.DecimalField(max_digits=15, decimal_places=2)


class SalesmanIndicators(models.Model):
    salesman = models.OneToOneField(
        Salesman,
        on_delete=models.CASCADE,
        primary_key=True
    )

    biggest_sale = models.OneToOneField(
        Sale,
        on_delete=models.SET_NULL,
        null=True
    )

    purchases = models.PositiveIntegerField(default=0)

    money_generated = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return str(self.salesman)


class ClientIndicator(models.Model):
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        primary_key=True
    )

    biggest_sale = models.OneToOneField(
        Sale,
        on_delete=models.SET_NULL,
        null=True
    )

    purchases = models.PositiveIntegerField(default=0)

    money_generated = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return str(self.client)
