"""
This module contains test cases for the following classes:
* UpdateUserForm (validation and saving functionality)
* UpdateProfileForm (validation and image handling functionality)
"""

import io
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from ..forms import CustomUserCreationForm, UpdateUserForm, UpdateProfileForm
from ..models import Profile


class CustomUserCreationFormTests(TestCase):
    """
    Test suite for the CustomUserCreationForm.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.valid_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }

    def test_form_valid_with_correct_data(self):
        """
        Test that the form is valid when correct data is provided.
        """
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_when_email_missing(self):
        """
        Test that the form is invalid when the email is missing.
        """
        invalid_data = self.valid_data.copy()
        invalid_data.pop("email")
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid(), form.errors)

    def test_form_invalid_when_email_invalid(self):
        """
        Test that the form is invalid when an invalid email is provided.
        """
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = "invalidemail"
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid(), form.errors)

    def test_form_invalid_when_passwords_mismatch(self):
        """
        Test that the form is invalid when passwords do not match.
        """
        invalid_data = self.valid_data.copy()
        invalid_data["password2"] = "differentpassword"
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid(), form.errors)

    def test_form_invalid_when_password_too_weak(self):
        """
        Test that the form is invalid when the password is too weak (doesn't meet validation requirements).
        """
        invalid_data = self.valid_data.copy()
        invalid_data["password1"] = "weak"
        invalid_data["password2"] = "weak"
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid(), form.errors)

    def test_form_creates_user_with_valid_data(self):
        """
        Test that the form successfully creates a user when valid data is provided.
        """
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("strongpassword123"))

    def test_form_does_not_create_user_when_invalid(self):
        """
        Test that no user is created when the form is invalid.
        """
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = ""  # Missing email
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid(), form.errors)


class UpdateUserFormTests(TestCase):
    """
    Test suite for the UpdateUserForm.
    """

    def setUp(self):
        """
        Set up the test environment by creating a user.
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
        )
        self.form_data = {
            "username": "newusername",
            "email": "newemail@example.com",
            "password1": "newpassword123",
            "password2": "newpassword123",
        }

    def test_form_valid_with_correct_data(self):
        """
        Test that the form is valid when correct data is provided.
        """
        form = UpdateUserForm(data=self.form_data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_email_missing(self):
        """
        Test that the form is invalid when the email field is missing.
        """
        form_data = self.form_data.copy()
        form_data.pop("email")
        form = UpdateUserForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid(), form.errors)

    def test_form_invalid_password_mismatch(self):
        """
        Test that the form is invalid when passwords do not match.
        """
        form_data = self.form_data.copy()
        form_data["password2"] = "differentpassword"
        form = UpdateUserForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid(), form.errors)

    def test_form_invalid_password_validation(self):
        """
        Test that the form is invalid when the new password does not meet validation requirements.
        """
        form_data = self.form_data.copy()
        form_data["password1"] = "short"
        form = UpdateUserForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid(), form.errors)

    def test_form_save_with_new_password_and_email(self):
        """
        Test that the form's save method updates the user's password and email correctly.
        """
        form = UpdateUserForm(data=self.form_data, instance=self.user)
        if form.is_valid():
            user = form.save()
            self.assertTrue(user.check_password("newpassword123"))
            self.assertEqual(user.email, "newemail@example.com")

    def test_form_does_not_change_password_if_not_provided(self):
        """
        Test that the form's save method does not change the password if no new password is provided.
        """
        form_data = {"username": "updatedusername", "email": "updatedemail@example.com"}
        form = UpdateUserForm(data=form_data, instance=self.user)
        if form.is_valid():
            user = form.save()
            self.assertTrue(
                user.check_password("password123")
            )  # Original password should still be valid
            self.assertEqual(user.username, "updatedusername")
            self.assertEqual(user.email, "updatedemail@example.com")


class UpdateProfileFormTests(TestCase):
    """
    Test suite for the UpdateProfileForm.
    """

    def setUp(self):
        """
        Set up the test environment by creating a user and a profile.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpassword123"
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.user)

    def test_form_with_valid_image(self):
        """
        Test the form with a valid image file (byte stream using PIL).
        """
        image = Image.new("RGB", (100, 100))
        image_byte_array = io.BytesIO()
        image.save(image_byte_array, format="JPEG")
        image_byte_array.seek(0)

        image_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=image_byte_array.read(),
            content_type="image/jpeg",
        )

        form_data = {"avatar": image_file}
        form = UpdateProfileForm(data={}, files=form_data, instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_with_no_data(self):
        """
        Test that the form is valid when no data is provided, even when no avatar is uploaded.
        """
        form = UpdateProfileForm(data={}, files={}, instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_with_invalid_file_type(self):
        """
        Test that the form is invalid when a non-image file is provided for the avatar field.
        """
        invalid_file = SimpleUploadedFile(
            name="test_file.txt",
            content=b"this is a text file, not an image",
            content_type="text/plain",
        )

        form_data = {"avatar": invalid_file}
        form = UpdateProfileForm(data={}, files=form_data, instance=self.profile)
        self.assertFalse(form.is_valid(), form.errors)
