"""
This module contains test cases for the following classes:
* UpdateUserForm (validation and saving functionality)
"""

from django.test import TestCase
from django.contrib.auth.models import User
from ..forms import UpdateUserForm


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
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_invalid_password_validation(self):
        """
        Test that the form is invalid when the new password does not meet validation requirements.
        """
        form_data = self.form_data.copy()
        form_data["password1"] = "short"
        form = UpdateUserForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)

    def test_form_save_with_new_password(self):
        """
        Test that the form's save method updates the user's password correctly.
        """
        form = UpdateUserForm(data=self.form_data, instance=self.user)
        if form.is_valid():
            user = form.save()
            self.assertTrue(user.check_password("newpassword123"))

    def test_form_does_not_change_password_if_not_provided(self):
        """
        Test that the form's save method does not change the password if no new password is provided.
        """
        form_data = {"username": "updatedusername"}
        form = UpdateUserForm(data=form_data, instance=self.user)
        if form.is_valid():
            user = form.save()
            self.assertTrue(
                user.check_password("password123")
            )  # Original password should still be valid
            self.assertEqual(user.username, "updatedusername")
