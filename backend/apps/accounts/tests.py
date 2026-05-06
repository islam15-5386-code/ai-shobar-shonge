from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class AuthApiTests(APITestCase):
    def test_register_and_login(self):
        r = self.client.post('/api/accounts/register/', {'username': 'u1', 'password': 'pass12345'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertIn('tokens', r.data)

        r2 = self.client.post('/api/accounts/login/', {'username': 'u1', 'password': 'pass12345'}, format='json')
        self.assertEqual(r2.status_code, 200)
        self.assertIn('tokens', r2.data)

    def test_me_requires_auth(self):
        r = self.client.get('/api/accounts/me/')
        self.assertEqual(r.status_code, 401)
