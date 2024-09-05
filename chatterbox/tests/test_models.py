"""
This module contains test cases for the PrivateChat & Message models.
The tests cover various aspects of the models, including chat & message creation,
field validations, foreign key constraints, and the __str__ method.
"""

import io
from PIL import Image
from django.test import TestCase
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import User
from ..models import PrivateChat, Message


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


class MessageModelTests(TestCase):
    """
    Test suite for the Message model.
    """

    def setUp(self):
        """
        Set up the test environment by creating users and a private chat.
        """
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

    def test_message_creation(self):
        """
        Test creation of a Message instance with text.
        """
        message = Message.objects.create(
            chat=self.chat, user=self.user1, content="Hello World!"
        )
        self.assertEqual(message.chat, self.chat)
        self.assertEqual(message.user, self.user1)
        self.assertEqual(message.content, "Hello World!")

    def test_message_with_image(self):
        """
        Test creation of a Message instance with an image.
        """
        # Create a temporary image file for testing (500x500 pixels)
        image = Image.new("RGB", (500, 500), "white")
        byte_io = io.BytesIO()
        image.save(byte_io, format="JPEG")
        byte_io.seek(0)

        # Retrieve the image bytes
        image_data = byte_io.getvalue()
        message = Message.objects.create(
            chat=self.chat, user=self.user1, content="", image=image_data
        )
        self.assertEqual(message.content, "")
        self.assertEqual(message.image, image_data)
        self.assertEqual(str(message), f"{self.user1.username} sent an image.")

    def test_message_str_representation(self):
        """
        Test the string representation of Message.
        """
        message = Message.objects.create(
            chat=self.chat, user=self.user1, content="Hello World!"
        )
        expected_str = f"{self.user1.username}: Hello World!..."
        self.assertEqual(str(message), expected_str)

    def test_get_time_diff(self):
        """
        Test the get_time_diff method of Message.
        """
        # Create a message 5 minutes ago
        past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        message = Message.objects.create(
            chat=self.chat,
            user=self.user1,
            content="Another message!",
            timestamp=past_time,
        )
        message.timestamp = past_time
        message.save(update_fields=["timestamp"])  # Force timestamp field update
        self.assertIn("minutes ago", message.get_time_diff())

        # Create a message 2 hours ago
        past_time = datetime.now(timezone.utc) - timedelta(hours=2)
        message = Message.objects.create(
            chat=self.chat,
            user=self.user1,
            content="Yet another message!",
            timestamp=past_time,
        )
        message.timestamp = past_time
        message.save(update_fields=["timestamp"])  # Force timestamp field update
        self.assertIn("hours ago", message.get_time_diff())

        # Create a message 3 days ago
        past_time = datetime.now(timezone.utc) - timedelta(days=3)
        message = Message.objects.create(
            chat=self.chat, user=self.user1, content="Old message!", timestamp=past_time
        )
        message.timestamp = past_time
        message.save(update_fields=["timestamp"])  # Force timestamp field update
        self.assertIn("days ago", message.get_time_diff())

    def test_cascade_deletion_chat(self):
        """
        Test that deleting the associated PrivateChat deletes associated Message instances.
        """
        message = Message.objects.create(
            chat=self.chat, user=self.user1, content="Goodbye!"
        )
        self.chat.delete()
        self.assertFalse(Message.objects.filter(id=message.id).exists())

    def test_cascade_deletion_user(self):
        """
        Test that deleting the associated user deletes associated Message instances.
        """
        message = Message.objects.create(
            chat=self.chat, user=self.user1, content="Goodbye!"
        )
        self.user1.delete()
        self.assertFalse(Message.objects.filter(id=message.id).exists())
