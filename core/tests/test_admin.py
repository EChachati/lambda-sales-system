from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):
    def setUp(self):
        """
        Funcion de Test antes de correr los Test
        Creamos el cliente, el admin y un user
        """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='Adminpassword123'
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='example@client.com',
            password='password123'
        )

    def test_users_listed(self):
        """
        Testear que los usuarios han sido enlistados en la página de usuario
        """

        url = reverse('admin:core_user_changelist')
        respose = self.client.get(url)

        self.assertContains(respose, self.user.name)
        self.assertContains(respose, self.user.email)

    def test_user_change_page(self):
        """"
        Prueba que la página editada por el usuario funciona
        """
        url = reverse('admin:core_user_change', args=[
                      self.user.id])        # /admin/core/user/1/
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """"
        Testear que la página de crear usuario funciona
        """
        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
