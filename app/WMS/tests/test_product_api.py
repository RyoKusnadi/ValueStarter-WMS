import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Tag, Category
from WMS.serializers import ProductSerializer

PRODUCT_URL = reverse('WMS:product-list')


def image_upload_url(product_id):
    """Return URL for product image upload"""
    return reverse('WMS:product-upload-image', args=[product_id])


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

    def test_create_basic_product(self):
        """Test creating product"""
        payload = {
            'title': 'test title',
            'weight': 30,
            'price': 5.00
        }
        res = self.client.post(PRODUCT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(product, key))

    def test_create_product_with_tags(self):
        """Test creating a product with tags"""
        tag1 = sample_tag(user=self.user, name='new')
        tag2 = sample_tag(user=self.user, name='old')
        payload = {
            'title': 'test title with tag',
            'tags': [tag1.id, tag2.id],
            'weight': 60,
            'price': 20.00
        }
        res = self.client.post(PRODUCT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        tags = product.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_product_with_categories(self):
        """Test creating product with ingredients"""
        category1 = sample_category(user=self.user, name='cat1')
        category2 = sample_category(user=self.user,
                                    name='cat2')
        payload = {
            'title': 'title with categories',
            'categories': [category1.id, category2.id],
            'weight': 20,
            'price': 7.00
        }
        res = self.client.post(PRODUCT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        categories = product.categories.all()
        self.assertEqual(categories.count(), 2)
        self.assertIn(category1, categories)
        self.assertIn(category2, categories)

    def test_partial_update_product(self):
        """Test updating a product with patch"""
        product = sample_product(user=self.user)
        product.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='old')

        payload = {'title': 'Chicken Menu Recipe', 'tags': [new_tag.id]}
        url = detail_url(product.id)
        self.client.patch(url, payload)

        product.refresh_from_db()
        self.assertEqual(product.title, payload['title'])
        tags = product.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_product(self):
        """Test updating a product with put"""
        product = sample_product(user=self.user)
        product.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'title 1',
            'weight': 25,
            'price': 5.00
        }
        url = detail_url(product.id)
        self.client.put(url, payload)

        product.refresh_from_db()
        self.assertEqual(product.title, payload['title'])
        self.assertEqual(product.weight, payload['weight'])
        self.assertEqual(product.price, payload['price'])
        tags = product.tags.all()
        self.assertEqual(len(tags), 0)


class ProductImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.product = sample_product(user=self.user)

    def tearDown(self):
        self.product.image.delete()

    def test_upload_image_to_product(self):
        """Test uploading an image to product"""
        url = image_upload_url(self.product.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.product.image.path))

    def test_upload_product_bad_request(self):
        """Test uploading an invalid product"""
        url = image_upload_url(self.product.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_products_by_tags(self):
        """Test returning recipes with specific tags"""
        product1 = sample_product(user=self.user, title='New Book')
        product2 = sample_product(user=self.user, title='Old Book')
        tag1 = sample_tag(user=self.user, name='New')
        tag2 = sample_tag(user=self.user, name='Old')
        product1.tags.add(tag1)
        product2.tags.add(tag2)
        product3 = sample_product(user=self.user, title='Middle Book')

        res = self.client.get(
            PRODUCT_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = ProductSerializer(product1)
        serializer2 = ProductSerializer(product2)
        serializer3 = ProductSerializer(product3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_products_by_ingredients(self):
        """Test returning recipes with specific ingredients"""
        product1 = sample_product(user=self.user, title='Product1')
        product2 = sample_product(user=self.user, title='Product2')
        category1 = sample_category(user=self.user, name='Book')
        category2 = sample_category(user=self.user, name='Dictionary')
        product1.categories.add(category1)
        product2.categories.add(category2)
        product3 = sample_product(user=self.user, title='Product3')

        res = self.client.get(
            PRODUCT_URL,
            {'categories': f'{category1.id},{category2.id}'}
        )

        serializer1 = ProductSerializer(product1)
        serializer2 = ProductSerializer(product2)
        serializer3 = ProductSerializer(product3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
