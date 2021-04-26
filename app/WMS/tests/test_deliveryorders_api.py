from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import DeliveryOrder, Product

DELIVERYORDER_URL = reverse('WMS:deliveryorder-list')


def sample_deliveryorder(user, **params):
    """Create and return a sample delivery order"""
    defaults = {
        'deliveryNumber': 'TRN-001',
        'sentFrom': 'Batam',
        'sentTo': 'Palembang',
        'fullAddress': 'Jln M.Thamrin No.17 Blok C',
        'contactPerson': '08213241234',
        'price': 72.000,
    }
    defaults.update(params)

    return DeliveryOrder.objects.create(user=user, **defaults)


def sample_product(user, **params):
    """Create and return a sample product"""
    defaults = {
        'title': 'sample product',
        'weight': 5.00,
        'price': 7.000
    }
    defaults.update(params)

    return Product.objects.create(user=user, **defaults)


def detail_url(deliveryorder_id):
    """Return Delivery Order Detail URL"""
    return reverse('WMS:deliveryorder-detail', args=[deliveryorder_id])


class DeliveryOrderApiTest(TestCase):
    """Test unauthenticated DeliveryOrder API Access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_requires(self):
        """Test that authentication is required"""
        res = self.client.get(DELIVERYORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDeliveryOrderApiTest(TestCase):
    """Test unauthenticated DeliveryOrder API Access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'tester@domain.com',
            'tester123  '
        )
        self.client.force_authenticate(self.user)

    def test_create_basic_deliveryOrder(self):
        """Test creating product"""
        payload = {
              'deliveryNumber': 'TRN-002',
              'sentFrom': 'Makassar',
              'sentTo': 'Jayabaya',
              'fullAddress': 'Jln M.Thamrin No.12 Blok C',
              'price': 100.000,
        }
        res = self.client.post(DELIVERYORDER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        deliveryOrder = DeliveryOrder.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(deliveryOrder, key))
