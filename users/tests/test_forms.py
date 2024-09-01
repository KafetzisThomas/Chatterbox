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
from ..forms import UpdateUserForm, UpdateAvatarForm
from ..models import Profile


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
            password="password123",
        )
        self.form_data = {
            "username": "newusername",
            "password1": "newpassword123",
            "password2": "newpassword123",
        }

    def test_form_valid_with_correct_data(self):
        """
        Test that the form is valid when correct data is provided.
        """
        form = UpdateUserForm(data=self.form_data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_password_mismatch(self):
        """
        Test that the form is invalid when passwords do not match.
        """
        form_data = self.form_data.copy()
        form_data["password2"] = "differentpassword"
        form = UpdateUserForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertIn("password2", form.errors)

    def test_form_invalid_password_validation(self):
        """
        Test that the form is invalid when the new password does not meet validation requirements.
        """
        form_data = self.form_data.copy()
        form_data["password1"] = "short"
        form = UpdateUserForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertIn("password1", form.errors)

    def test_form_save_with_new_password(self):
        """
        Test that the form's save method updates the user's password correctly.
        """
        form = UpdateUserForm(data=self.form_data, instance=self.user)
        if form.is_valid():
            user = form.save()
            self.assertTrue(user.check_password("newpassword123"), form.errors)

    def test_form_does_not_change_password_if_not_provided(self):
        """
        Test that the form's save method does not change the password if no new password is provided.
        """
        form_data = {"username": "updatedusername"}
        form = UpdateUserForm(data=form_data, instance=self.user)
        if form.is_valid():
            user = form.save()
            self.assertTrue(
                user.check_password("password123"), form.errors
            )  # Original password should still be valid
            self.assertEqual(user.username, "updatedusername", form.errors)


class UpdateAvatarFormTests(TestCase):
    """
    Test suite for the UpdateAvatarForm.
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
        form = UpdateAvatarForm(data={}, files=form_data, instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_with_no_data(self):
        """
        Test that the form is valid when no data is provided, even when no avatar is uploaded.
        """
        form = UpdateAvatarForm(data={}, files={}, instance=self.profile)
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
        form = UpdateAvatarForm(data={}, files=form_data, instance=self.profile)
        self.assertFalse(form.is_valid(), form.errors)
