from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category
from WMS.serializers import TagSerializer

CATEGORIES_URL = reverse('WMS:category-list')


class PublicCategoriesApiTests(TestCase):
    """Test the publicly available Categories API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(CATEGORIES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoriesApiTests(TestCase):
    """Test the authorized user categories API"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'user@domain.com',
            'testing'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_categories(self):
        """Test retrieving categories"""
        Category.objects.create(user=self.user, name='Book')
        Category.objects.create(user=self.user, name='Dictionary')

        res = self.client.get(CATEGORIES_URL)

        tags = Category.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_categories_limited_to_user(self):
        """Test that categories returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@domain.com',
            'testing'
        )
        Category.objects.create(user=user2, name='Pencil')
        category = Category.objects.create(user=self.user, name='Accessories')

        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], category.name)
