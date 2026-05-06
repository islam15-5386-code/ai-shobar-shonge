from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from apps.businesses.models import Business
from apps.products.models import Product


class ProductIsolationTests(APITestCase):
    def setUp(self):
        self.owner1 = User.objects.create_user(username='owner1', password='pass12345')
        self.owner2 = User.objects.create_user(username='owner2', password='pass12345')
        self.b1 = Business.objects.create(owner=self.owner1, name='B1', slug='b1')
        self.b2 = Business.objects.create(owner=self.owner2, name='B2', slug='b2')
        Product.objects.create(business=self.b1, name='P1', price=100)
        Product.objects.create(business=self.b2, name='P2', price=200)

    def _auth(self, username):
        r = self.client.post('/api/accounts/login/', {'username': username, 'password': 'pass12345'}, format='json')
        token = r.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_business_data_isolation(self):
        self._auth('owner1')
        r = self.client.get('/api/products/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['name'], 'P1')
