"""
This module contains test cases for the PrivateChat form.
"""

from django.test import TestCase
from ..forms import PrivateChatForm


class PrivateChatFormTest(TestCase):
    """
    Test suite for the PrivateChatForm.
    """

    def test_form_valid_data(self):
        """
        Test that the form is valid when given valid data.
        """
        form_data = {"username": "testuser"}
        form = PrivateChatForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_empty_data(self):
        """
        Test that the form is invalid when given empty data.
        """
        form_data = {"username": ""}
        form = PrivateChatForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertEqual(form.errors["username"], ["This field is required."])

    def test_form_exceeding_max_length(self):
        """
        Test that the form is invalid when the username exceeds max_length.
        """
        form_data = {"username": "a" * 101}  # 101 characters
        form = PrivateChatForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertEqual(
            form.errors["username"],
            ["Ensure this value has at most 100 characters (it has 101)."],
        )

    def test_form_field_attributes(self):
        """
        Test that the form field has the correct attributes.
        """
        form = PrivateChatForm()
        username_field = form.fields["username"]
        self.assertEqual(username_field.max_length, 100)
        self.assertEqual(username_field.label, "Username")
        self.assertEqual(username_field.widget.attrs["class"], "form-control")
        self.assertEqual(
            username_field.widget.attrs["placeholder"], "Enter username to chat"
        )
