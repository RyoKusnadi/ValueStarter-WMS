from django.urls import reverse
from core.models import Tag, Category

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
