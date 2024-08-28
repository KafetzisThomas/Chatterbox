"""
This module contains test cases for the Profile model.
The tests cover various aspects of the model, including
profile creation, image resizing, and the __str__ method.
"""

import tempfile
from django.test import TestCase
from PIL import Image
from ..models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User


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
        Test that a new Profile instance has the default avatar image.
        """
        profile, _ = Profile.objects.get_or_create(user=self.user)
        self.assertEqual(profile.avatar.name, "default.png")

    def test_avatar_resizing(self):
        """
        Test that the avatar image is resized,
        if its dimensions exceed the specified limit (300x300 pixels).
        """
        # Create a temporary image file for testing (500x500 pixels)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_image:
            image = Image.new("RGB", (500, 500), "white")
            image.save(temp_image, format="JPEG")
            temp_image.seek(0)

            profile, _ = Profile.objects.get_or_create(user=self.user)
            profile.avatar = SimpleUploadedFile(
                temp_image.name, temp_image.read(), content_type="image/jpeg"
            )
            profile.save()

            # Open the image from the saved path
            img = Image.open(profile.avatar.path)

            # Assert that the image has been resized to 300x300 pixels
            self.assertLessEqual(img.height, 300)
            self.assertLessEqual(img.width, 300)

    def test_string_representation(self):
        """
        Test the string representation of Profile.
        """
        profile, _ = Profile.objects.get_or_create(user=self.user)
        self.assertEqual(str(profile), self.user.username)
