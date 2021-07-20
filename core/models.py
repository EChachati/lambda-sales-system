from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings


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
    purchases = models.PositiveIntegerField(default=0)
    money_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
