"""
This module contains test cases for the following views:
* chat_list
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from ..models import PrivateChat, Message


class ChatListViewTests(TestCase):
    """
    Test suite for the chat_list view.
    """

    def setUp(self):
        """
        Set up the test environment by creating users, chats, and messages.
        """
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.user3 = User.objects.create_user(username="user3", password="password123")
        self.client.login(username="user1", password="password123")

        # Create chats
        self.chat1 = PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        self.chat2 = PrivateChat.objects.create(user1=self.user1, user2=self.user3)

        # Create messages
        Message.objects.create(
            chat=self.chat1, user=self.user1, content="Hello!", timestamp=timezone.now()
        )
        Message.objects.create(
            chat=self.chat2,
            user=self.user3,
            content="Hey there!",
            timestamp=timezone.now(),
        )

    def test_redirect_if_not_logged_in(self):
        """
        Test that the view redirects to the login page if the user is not logged in.
        """
        self.client.logout()
        response = self.client.get(reverse("chatterbox:chat_list"))
        self.assertRedirects(
            response, f'{reverse("users:login")}?next={reverse("chatterbox:chat_list")}'
        )

    def test_view_url_exists_at_desired_location(self):
        """
        Test that the view URL exists at the desired location.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        """
        Test that the view is accessible by its name.
        """
        response = self.client.get(reverse("chatterbox:chat_list"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        Test that the view uses the correct template.
        """
        response = self.client.get(reverse("chatterbox:chat_list"))
        self.assertTemplateUsed(response, "chatterbox/chat_list.html")

    def test_view_contains_chats_with_last_messages(self):
        """
        Test that the view contains the correct chats and last messages in the context.
        """
        response = self.client.get(reverse("chatterbox:chat_list"))
        self.assertEqual(response.status_code, 200)

        # Check that the correct number of chats are returned
        self.assertEqual(len(response.context["chats_with_last_messages"]), 2)

        # Check chat1 details
        chat1_context = response.context["chats_with_last_messages"][0]
        self.assertEqual(chat1_context[0], self.user2)  # Other user in chat1
        self.assertEqual(chat1_context[1].content, "Hello!")  # Last message content
        self.assertIn("seconds ago", chat1_context[2])  # Time difference

        # Check chat2 details
        chat2_context = response.context["chats_with_last_messages"][1]
        self.assertEqual(chat2_context[0], self.user3)  # Other user in chat2
        self.assertEqual(chat2_context[1].content, "Hey there!")  # Last message content
        self.assertIn("seconds ago", chat2_context[2])  # Time difference

    def test_view_handles_no_messages(self):
        """
        Test that the view correctly handles chats with no messages.
        """
        # Clean up previous chats and messages
        PrivateChat.objects.all().delete()
        Message.objects.all().delete()

        # Create a new chat without messages
        PrivateChat.objects.create(user1=self.user2, user2=self.user3)

        # Fetch the view
        response = self.client.get(reverse("chatterbox:chat_list"))
        self.assertEqual(response.status_code, 200)

        # Chat is not created yet so no messages are present
        chats_with_last_messages = response.context["chats_with_last_messages"]
        self.assertEqual(len(chats_with_last_messages), 0)
