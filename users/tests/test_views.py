"""
This module contains test cases for the following views:
* register
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterViewTests(TestCase):
    """
    Test case for the register view.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.url = reverse("users:register")

    def test_register_view_get(self):
        """
        Test that the register view renders correctly on GET request.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")
        self.assertIsInstance(response.context["form"], UserCreationForm)

    def test_register_view_post_valid_data(self):
        """
        Test registering a new user with a valid form submission.
        """
        valid_data = {
            "username": "testuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        response = self.client.post(self.url, data=valid_data)

        # Check that user is created
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, "testuser")

        # Check response and redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:login"))

    def test_register_view_post_invalid_data(self):
        """
        Test registering a new user with an invalid form submission.
        """
        invalid_data = {
            "username": "testuser",
            "password1": "strongpassword123",
            "password2": "differentpassword123",  # Different password confirmation
        }
        response = self.client.post(self.url, data=invalid_data)

        # Check that user is not created
        self.assertEqual(User.objects.count(), 0)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")
        self.assertIsInstance(response.context["form"], UserCreationForm)
        self.assertTrue(response.context["form"].errors)
