from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from djmoney.models.fields import MoneyField
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
    class Type(models.TextChoices):
        """
        Staff Status
        """
        NONE = 'NONE', _('None')
        ADMIN = 'ADMIN', _('Admin')
        SALESMAN = 'SALESMAN', _('Salesman')
        CLIENT = 'CLIENT', _('Client')
        SALESMAN_AND_CLIENT = 'SALESMAN_AND_CLIENT', _('Salesman and Client')

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    identity_card = models.CharField(max_length=12, default='None')
    phone = models.CharField(max_length=20, default='None')
    address = models.CharField(max_length=255, default='None')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.NONE
    )

    USERNAME_FIELD = 'email'

    def to_dict(self):
        """
        Return a dictionary with the user information
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'identity_card': self.identity_card,
            'phone': self.phone,
            'address': self.address,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'type': self.type
        }


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

    def to_dict(self):
        """
        Return a dictionary with the user information
        """
        return {
            'id': self.id,
            'identity_card': self.identity_card,
            'name': self.name,
            'image': self.image.name,
            'phone_1': self.phone_1,
            'phone_2': self.phone_2,
            'address': self.address
        }


class Client(models.Model):
    """
    Client Model
    """
    identity_card = models.CharField(max_length=15, blank=False)

    name = models.CharField(max_length=128, blank=False)
    image = models.ImageField(
        upload_to='client',
        blank=True,
        null=True
    )
    address = models.CharField(max_length=255, blank=False)

    phone = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name

    def to_dict(self):
        """
        Return a dictionary with the user information
        """
        return {
            'id': self.id,
            'identity_card': self.identity_card,
            'name': self.name,
            'image': self.image.name,
            'address': self.address,
            'phone': self.phone
        }


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

    code = models.CharField(max_length=50, unique=True, default='None')
    name = models.CharField(max_length=50, blank=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT
    )
    description = models.CharField(max_length=144, blank=True)
    presentation = models.CharField(max_length=3, blank=True)
    cost = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        default=0.00
    )

    price_1 = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        default=0.00
    )
    price_2 = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        default=0.00
    )
    price_3 = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
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

    def to_dict(self):
        """
        Return a dictionary with the user information
        """
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'category': self.category.name,
            'description': self.description,
            'presentation': self.presentation,
            'cost': self.cost.amount,
            'price_1': self.price_1.amount,
            'price_2': self.price_2.amount,
            'price_3': self.price_3.amount,
            'brand': self.brand,
            'image': self.image.name
        }


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

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    id = models.CharField(max_length=50, unique=True, primary_key=True)

    salesman = models.ForeignKey(
        Salesman,
        on_delete=models.RESTRICT
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.RESTRICT
    )
    income = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        default=0.00
    )
    product = models.ManyToManyField(
        Product,
        through='ProductSale'
    )
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=datetime.date.today)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )

    def __str__(self):
        return str(self.id)

    def to_dict(self):
        """
        Return a dictionary with the user information
        """
        return {
            'id': self.id,
            'salesman': self.salesman.to_dict(),
            'client': self.client.to_dict(),
            'income': self.income.amount,
            'product': [product.to_dict() for product in self.product.all()],
            'description': self.description,
            'date': self.date,
            'status': self.status
        }


class Order(models.Model):

    id = models.CharField(max_length=50, unique=True, primary_key=True)

    salesman = models.ForeignKey(
        Salesman,
        on_delete=models.RESTRICT
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.RESTRICT
    )
    income = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        default=0.00
    )
    product = models.ManyToManyField(
        Product,
        through='ProductOrder'
    )
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return str(self.id)

    def to_dict(self):
        """
        Return a dictionary with the user information
        """
        return {
            'id': self.id,
            'salesman': self.salesman.to_dict(),
            'client': self.client.to_dict(),
            'income': self.income.amount,
            'product': [product.to_dict() for product in self.product.all()],
            'description': self.description,
            'date': self.date
        }


class OrderSale(models.Model):
    """
    Order Sale
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.order) + ' - ' + str(self.sale)


class ProductOrder(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(default=1)
    income = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        default=0.00
    )


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
    income = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        default=0.00
    )


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

    money_generated = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        default=0.00
    )

    def __str__(self):
        return str(self.salesman)

    def to_dict(self):
        return {
            'salesman': self.salesman.to_dict(),
            'biggest_sale': self.biggest_sale.to_dict() if self.biggest_sale else None,
            'purchases': self.purchases,
            'money_generated': self.money_generated.amount
        }


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

    money_generated = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        default=0.00
    )

    def __str__(self):
        return str(self.client)

    def to_dict(self):
        return {
            'client': self.client.to_dict(),
            'biggest_sale': self.biggest_sale.to_dict() if self.biggest_sale else None,
            'purchases': self.purchases,
            'money_generated': self.money_generated.amount
        }
