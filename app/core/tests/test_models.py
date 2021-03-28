from django.test import TestCase
from django.contrib.auth import get_user_model
from .. import models


def sample_user(email='test@domain,com', password='testing'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@domain.com'
        password = '12345'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@DOMAIN.COM'
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test Creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@domain.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='New'
        )

        self.assertEqual(str(tag), tag.name)

    def test_category_str(self):
        """Test the Model string representation"""
        category = models.Category.objects.create(
            user=sample_user(),
            name='Book'
        )

        self.assertEqual(str(category), category.name)
