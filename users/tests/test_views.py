"""
This module contains test cases for the following views:
* register, account, delete_account
"""

import io
from PIL import Image
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

    def test_account_view_post_valid_avatar(self):
        """
        Test updating account with a valid avatar upload using a fake image.
        """
        # Create a fake image
        image = Image.new("RGB", (100, 100), color="red")
        byte_arr = io.BytesIO()
        image.save(byte_arr, format="PNG")
        byte_arr.seek(0)
        avatar = SimpleUploadedFile(
            "avatar.png", byte_arr.read(), content_type="image/png"
        )
        valid_data = {
            "username": "updateduser",
            "password1": "newstrongpassword123",
            "password2": "newstrongpassword123",
            "avatar": avatar,
        }
        response = self.client.post(self.url, data=valid_data, follow=True)

        # Refresh user and profile from database
        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        # Check if user details are updated
        self.assertEqual(self.user.username, "updateduser")
        self.assertTrue(self.user.check_password("newstrongpassword123"))
        self.assertIsNotNone(self.profile.avatar)

        # Check response and redirect
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("chatterbox:chat_list"))

    def test_account_view_post_invalid_avatar(self):
        """
        Test updating account with an invalid avatar upload (non-image file).
        """
        invalid_avatar = SimpleUploadedFile(
            "file.txt", b"file_content", content_type="text/plain"
        )
        invalid_data = {
            "username": "testuser",
            "avatar": invalid_avatar,
        }
        response = self.client.post(self.url, data=invalid_data)

        # Ensure user details remain unchanged
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("testpassword"))

        # Check response and form errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/account.html")
        self.assertTrue(response.context["profile_form"].errors)

    def test_account_view_requires_login(self):
        """
        Test that the account view requires login.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/user/login/?next={self.url}")


class DeleteAccountViewTests(TestCase):
    """
    Test case for the delete_account view.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.url = reverse("users:delete_account")

    def test_delete_account_view_logged_in(self):
        """
        Test deleting the user account with a POST request.
        """
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(self.url, follow=True)

        # Check that the user is deleted
        self.assertFalse(User.objects.filter(username="testuser").exists())
        self.assertRedirects(response, reverse("users:register"))

    def test_delete_account_view_not_logged_in(self):
        """
        Test accessing the view when not logged in.
        """
        response = self.client.post(self.url, follow=True)
        login_url = reverse("users:login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")

        # Ensure the user is not deleted
        self.assertTrue(User.objects.filter(username="testuser").exists())
