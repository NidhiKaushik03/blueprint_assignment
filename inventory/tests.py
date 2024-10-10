# inventory/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Item
from rest_framework_simplejwt.tokens import RefreshToken

class ItemTests(APITestCase):
    def setUp(self):
        self.item = Item.objects.create(name="Test Item", description="Test description")
        self.user = self.client.post('/auth/users/', {'username': 'testuser', 'password': 'testpassword'}).data
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))

    def test_create_item(self):
        data = {'name': 'New Item', 'description': 'New description'}
        response = self.client.post(reverse('item-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_item(self):
        response = self.client.get(reverse('item-detail', args=[self.item.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item(self):
        data = {'name': 'Updated Item', 'description': 'Updated description'}
        response = self.client.put(reverse('item-detail', args=[self.item.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_item(self):
        response = self.client.delete(reverse('item-detail', args=[self.item.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
