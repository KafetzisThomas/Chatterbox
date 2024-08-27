"""
This module contains test cases for the PrivateChat model.
The tests cover various aspects of the model, including chat creation,
field validations, foreign key constraints, and the __str__ method.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from ..models import PrivateChat


class PrivateChatModelTests(TestCase):
    """
    Test suite for the PrivateChat model.
    """

    def setUp(self):
        """
        Set up the test environment by creating two users.
        """
        self.user1 = User.objects.create(username="user1", password="password123")
        self.user2 = User.objects.create(username="user2", password="password123")

    def test_private_chat_creation(self):
        """
        Test creation of a PrivateChat instance.
        """
        chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        self.assertEqual(chat.user1, self.user1)
        self.assertEqual(chat.user2, self.user2)

    def test_private_chat_str_representation(self):
        """
        Test the string representation of PrivateChat.
        """
        chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        expected_str = f"Chat between {self.user1.username} and {self.user2.username}"
        self.assertEqual(str(chat), expected_str)

    def test_cascade_deletion_user1(self):
        """
        Test that deleting user1 deletes associated PrivateChat instances.
        """
        chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        self.user1.delete()
        self.assertFalse(PrivateChat.objects.filter(id=chat.id).exists())

    def test_cascade_deletion_user2(self):
        """
        Test that deleting user2 deletes associated PrivateChat instances.
        """
        chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        self.user2.delete()
        self.assertFalse(PrivateChat.objects.filter(id=chat.id).exists())
