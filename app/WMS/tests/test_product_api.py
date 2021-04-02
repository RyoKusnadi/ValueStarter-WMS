from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Tag, Category
from WMS.serializers import ProductSerializer, ProductDetailSerializer

PRODUCT_URL = reverse('WMS:product-list')


def detail_url(product_id):
    """Return Product Detail URL"""
    return reverse('WMS:product-detail', args=[product_id])


def sample_tag(user, name='New'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_category(user, name='Book'):
    """Create and Return a sample Category"""
    return Category.objects.create(user=user, name=name)


def sample_product(user, **params):
    """Create and return a sample product"""
    defaults = {
        'title': 'sample product',
        'weight': 5.00,
        'price': 7.000
    }
    defaults.update(params)

    return Product.objects.create(user=user, **defaults)


class PublicProductApiTest(TestCase):
    """Test unauthenticated Product API Access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_requires(self):
        """Test that authentication is required"""
        res = self.client.get(PRODUCT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductApiTest(TestCase):
    """Test unauthenticated Product API Access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'tester@domain.com',
            'tester123  '
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_product(self):
        """Test retrieving a list of product"""
        sample_product(user=self.user)
        sample_product(user=self.user)

        res = self.client.get(PRODUCT_URL)

        products = Product.objects.all().order_by('id')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_products_limited_to_user(self):
        """Test retrieving products for user"""
        user2 = get_user_model().objects.create_user(
            'tester2@domain.com',
            'testing'
        )
        sample_product(user=user2)
        sample_product(user=self.user)

        res = self.client.get(PRODUCT_URL)

        products = Product.objects.filter(user=self.user)
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_product_detail(self):
        """Test viewing a product detail"""
        product = sample_product(user=self.user)
        product.tags.add(sample_tag(user=self.user))
        product.categories.add(sample_category(user=self.user))

        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, serializer.data)
