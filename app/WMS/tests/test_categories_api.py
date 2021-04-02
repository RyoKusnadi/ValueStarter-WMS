from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Product
from WMS.serializers import CategorySerializer

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
        serializer = CategorySerializer(tags, many=True)
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

    def test_create_categories_successful(self):
        """Test Creating a new tag"""
        payload = {'name': 'super book'}
        self.client.post(CATEGORIES_URL, payload)
        exists = Category.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_category_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(CATEGORIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_categories_assigned_to_products(self):
        """Test filtering categories by those assigned to products"""
        category1 = Category.objects.create(
            user=self.user, name='New'
        )
        category2 = Category.objects.create(
            user=self.user, name='Old'
        )
        product = Product.objects.create(
            title='New book',
            weight=5,
            price=10,
            user=self.user
        )
        product.categories.add(category1)

        res = self.client.get(CATEGORIES_URL, {'assigned_only': 1})

        serializer1 = CategorySerializer(category1)
        serializer2 = CategorySerializer(category2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_categories_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        category = Category.objects.create(user=self.user, name='Book')
        Category.objects.create(user=self.user, name='Dictionary')
        product1 = Product.objects.create(
            title='Old Book',
            weight=30,
            price=12.00,
            user=self.user
        )
        product1.categories.add(category)
        product2 = Product.objects.create(
            title='new dict',
            weight=20,
            price=5.00,
            user=self.user
        )
        product2.categories.add(category)

        res = self.client.get(CATEGORIES_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
