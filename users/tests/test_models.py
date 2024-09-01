"""
This module contains test cases for the Profile model.
The tests cover various aspects of the model, including
profile creation, image resizing, and the __str__ method.
"""

import io
from django.test import TestCase
from PIL import Image
from django.contrib.auth.models import User
from ..models import Profile


class ProfileModelTests(TestCase):
    """
    Test case for the Profile model.
    """

    def setUp(self):
        """
        Set up the test environment by creating a user.
        """
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

    def test_profile_creation(self):
        """
        Test that a Profile instance is created correctly and linked to a User instance.
        """
        profile, _ = Profile.objects.get_or_create(user=self.user)
        self.assertEqual(profile.user, self.user)

    def test_default_avatar(self):
        """
        Test that a new Profile instance has no avatar object by default.
        """
        profile, _ = Profile.objects.get_or_create(user=self.user)
        self.assertIsNone(profile.avatar)

    def test_avatar_resizing(self):
        """
        Test that the avatar image is resized,
        if its dimensions exceed the specified limit (300x300 pixels).
        """
        # Create a temporary image file for testing (500x500 pixels)
        image = Image.new("RGB", (500, 500), "white")
        byte_io = io.BytesIO()
        image.save(byte_io, format="JPEG")
        byte_io.seek(0)

        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.avatar = byte_io.getvalue()
        profile.save()

        # Verify the image was resized
        img = Image.open(io.BytesIO(profile.avatar))
        self.assertLessEqual(img.height, 300)
        self.assertLessEqual(img.width, 300)

    def test_string_representation(self):
        """
        Test the string representation of Profile.
        """
        profile, _ = Profile.objects.get_or_create(user=self.user)
        self.assertEqual(str(profile), self.user.username)
