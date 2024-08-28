"""
This module contains test cases for the following views:
* register, account
"""

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.forms import UserCreationForm
from ..forms import UpdateUserForm, UpdateProfileForm
from django.contrib.auth.models import User
from ..models import Profile


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


class AccountViewTests(TestCase):
    """
    Test case for the account view.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("users:account")

    def test_account_view_get(self):
        """
        Test rendering the account page with GET request.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/account.html")
        self.assertIsInstance(response.context["user_form"], UpdateUserForm)
        self.assertIsInstance(response.context["profile_form"], UpdateProfileForm)
        self.assertEqual(response.context["user_form"].instance, self.user)
        self.assertEqual(response.context["profile_form"].instance, self.profile)

    def test_account_view_post_valid_data(self):
        """
        Test updating account credentials with valid form data.
        """
        valid_data = {
            "username": "updateduser",
            "password1": "newstrongpassword123",
            "password2": "newstrongpassword123",
        }
        response = self.client.post(self.url, data=valid_data, follow=True)

        # Refresh user and profile from database
        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        # Check if user details are updated
        self.assertEqual(self.user.username, "updateduser")
        self.assertTrue(self.user.check_password("newstrongpassword123"))

        # Check response and redirect
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("chatterbox:chat_list"))

    def test_account_view_post_invalid_data(self):
        """
        Test handling of invalid form submission.
        """
        invalid_data = {
            "username": "testuser",
            "password1": "password123",
            "password2": "differentpassword123",  # Different password confirmation
        }
        response = self.client.post(self.url, data=invalid_data)

        # Ensure user details remain unchanged
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "testuser")  # Username remains unchanged
        self.assertTrue(
            self.user.check_password("testpassword")
        )  # Password remains unchanged

        # Check response and form errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/account.html")
        self.assertTrue(response.context["user_form"].errors)

    def test_account_view_post_invalid_avatar(self):
        """
        Test handling errors when an invalid avatar file is uploaded.
        """
        invalid_data = {
            "username": "updateduser",
            "avatar": SimpleUploadedFile(
                name="test.txt", content=b"not an image", content_type="text/plain"
            ),
        }
        response = self.client.post(self.url, data=invalid_data)

        # Check that user and profile are not updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "testuser")  # Username remains unchanged
        self.assertTrue(
            self.user.check_password("testpassword")
        )  # Password remains unchanged

        # Check response and form errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/account.html")
        self.assertTrue(response.context["profile_form"].errors)
