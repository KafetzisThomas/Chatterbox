"""
This module contains test cases for the following views:
* chat_list, create_chat, chat
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from ..models import PrivateChat, Message
from ..forms import PrivateChatForm


class ChatListViewTests(TestCase):
    """
    Test suite for the chat_list view.
    """

    def setUp(self):
        """
        Set up the test environment by creating users, chats, and messages.
        """
        # Create users
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
            response, f"{reverse('users:login')}?next={reverse('chatterbox:chat_list')}"
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


class CreateChatViewTests(TestCase):
    """
    Test suite for the create_chat view.
    """

    def setUp(self):
        """
        Set up the test environment by creating users.
        """
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.user3 = User.objects.create_user(username="user3", password="password123")
        self.client.login(username="user1", password="password123")

    def test_create_chat_valid_form(self):
        """
        Test that the form is valid, creates or fetches a chat, and redirects correctly.
        """
        form_data = {"username": "user2"}
        response = self.client.post(reverse("chatterbox:create_chat"), data=form_data)
        self.assertEqual(response.status_code, 302)  # Expect redirect

        chat = PrivateChat.objects.get(user1=self.user1, user2=self.user2)
        self.assertIsNotNone(chat)  # Ensure chat was created or fetched

        expected_url = reverse("chatterbox:chat", args=["user1", "user2"])
        self.assertRedirects(response, expected_url)

    def test_create_chat_self_chat(self):
        """
        Test that the view redirects to chat_list when trying to create a chat with oneself.
        """
        form_data = {"username": "user1"}
        response = self.client.post(reverse("chatterbox:create_chat"), data=form_data)
        self.assertEqual(response.status_code, 302)  # Expect redirect to create_chat

        expected_url = reverse("chatterbox:create_chat")
        self.assertRedirects(response, expected_url)

    def test_create_chat_invalid_form(self):
        """
        Test that an invalid form submission re-renders the form with errors.
        """
        form_data = {"username": ""}  # Empty username is invalid
        response = self.client.post(reverse("chatterbox:create_chat"), data=form_data)
        self.assertEqual(response.status_code, 200)  # Expect to render the form again
        self.assertContains(response, "This field is required.")

    def test_create_chat_user_does_not_exist(self):
        """
        Test that the view handles the case where the user to chat with does not exist.
        """
        form_data = {"username": "nonexistentuser"}
        response = self.client.post(reverse("chatterbox:create_chat"), data=form_data)
        self.assertEqual(
            response.status_code, 302
        )  # Expect redirect if user does not exist

        expected_url = reverse("chatterbox:create_chat")
        self.assertRedirects(response, expected_url)

    def test_get_create_chat_view(self):
        """
        Test that a GET request renders the form correctly.
        """
        response = self.client.get(reverse("chatterbox:create_chat"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chatterbox/create_chat.html")
        self.assertIsInstance(response.context["form"], PrivateChatForm)


class ChatViewTests(TestCase):
    """
    Test suite for the chat view.
    """

    def setUp(self):
        """
        Set up the test environment by creating users, chats, and messages.
        """
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.user3 = User.objects.create_user(username="user3", password="password123")
        self.client.login(username="user1", password="password123")

        # Create chat
        self.chat1 = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

        # Create messages
        self.message1 = Message.objects.create(
            chat=self.chat1, user=self.user1, content="Hello!", timestamp=timezone.now()
        )
        self.message2 = Message.objects.create(
            chat=self.chat1, user=self.user2, content="Hi!", timestamp=timezone.now()
        )

    def test_redirect_if_not_logged_in(self):
        """
        Test that the view redirects to the login page if the user is not logged in.
        """
        self.client.logout()
        response = self.client.get(
            reverse("chatterbox:chat", args=[self.user1.username, self.user2.username])
        )
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('chatterbox:chat', args=[self.user1.username, self.user2.username])}",
        )

    def test_chat_view_url_exists_at_desired_location(self):
        """
        Test that the chat view URL exists at the desired location.
        """
        response = self.client.get(
            f"/chat/{self.user1.username}/{self.user2.username}/"
        )
        self.assertEqual(response.status_code, 200)

    def test_chat_view_accessible_by_name(self):
        """
        Test that the chat view is accessible by its name.
        """
        response = self.client.get(
            reverse("chatterbox:chat", args=[self.user1.username, self.user2.username])
        )
        self.assertEqual(response.status_code, 200)

    def test_chat_view_uses_correct_template(self):
        """
        Test that the chat view uses the correct template.
        """
        response = self.client.get(
            reverse("chatterbox:chat", args=[self.user1.username, self.user2.username])
        )
        self.assertTemplateUsed(response, "chatterbox/chat.html")

    def test_chat_view_correct_context_data(self):
        """
        Test that the chat view provides the correct context data.
        """
        response = self.client.get(
            reverse("chatterbox:chat", args=[self.user1.username, self.user2.username])
        )
        self.assertEqual(response.status_code, 200)

        # Check context data
        self.assertEqual(response.context["current_user"], self.user1)
        self.assertEqual(response.context["other_user"], self.user2)
        self.assertEqual(len(response.context["messages_with_prev"]), 2)
        self.assertEqual(response.context["messages_with_prev"][1][1], self.message1)
        self.assertEqual(response.context["messages_with_prev"][1][0], self.message2)

    def test_chat_view_redirects_if_user_not_involved_in_chat(self):
        """
        Test that the view redirects to the chat list if the user is not involved in the chat.
        """
        self.client.login(username="user3", password="password123")
        response = self.client.get(
            reverse("chatterbox:chat", args=[self.user1.username, self.user2.username])
        )
        self.assertRedirects(response, reverse("chatterbox:chat_list"))

    def test_chat_view_redirects_if_user_tries_to_chat_with_self(self):
        """
        Test that the view redirects to the chat list if the user tries to chat with themselves.
        """
        response = self.client.get(
            reverse("chatterbox:chat", args=[self.user1.username, self.user1.username])
        )
        self.assertRedirects(response, reverse("chatterbox:chat_list"))

    def test_chat_view_creates_chat_if_not_exists(self):
        """
        Test that the view creates a chat if it does not already exist.
        """
        self.client.login(username="user1", password="password123")
        response = self.client.get(
            reverse("chatterbox:chat", args=[self.user1.username, self.user3.username])
        )
        self.assertEqual(response.status_code, 200)
        new_chat = PrivateChat.objects.filter(
            user1=self.user1, user2=self.user3
        ).first()
        self.assertIsNotNone(new_chat)


class DeleteChatViewTests(TestCase):
    """
    Test case for the delete_chat view.
    """

    def setUp(self):
        """
        Set up the test environment by creating users, chats, and messages.
        """
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.client.login(username="user1", password="password123")

        # Create chat
        self.chat1 = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

        # Create messages
        self.message1 = Message.objects.create(
            chat=self.chat1, user=self.user1, content="Hello!", timestamp=timezone.now()
        )
        self.message2 = Message.objects.create(
            chat=self.chat1, user=self.user2, content="Hi!", timestamp=timezone.now()
        )
        # URL for deleting the chat, using the usernames as parameters
        self.url = reverse(
            "chatterbox:delete_chat",
            kwargs={
                "username": self.user1.username,
                "other_username": self.user2.username,
            },
        )

    def test_delete_chat_view_logged_in(self):
        """
        Test deleting the chat with a POST request.
        """
        response = self.client.post(self.url, follow=True)

        # Check that the chat is deleted
        self.assertFalse(
            PrivateChat.objects.filter(user1=self.user1, user2=self.user2).exists()
        )
        self.assertRedirects(response, reverse("chatterbox:chat_list"))

    def test_delete_chat_view_not_logged_in(self):
        """
        Test accessing the view when not logged in.
        """
        self.client.logout()
        response = self.client.post(self.url, follow=True)
        login_url = reverse("users:login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")

        # Ensure the chat is not deleted
        self.assertTrue(
            PrivateChat.objects.filter(user1=self.user1, user2=self.user2).exists()
        )


class DeleteMessageViewTests(TestCase):
    """
    Test case for the delete_message view.
    """

    def setUp(self):
        """
        Set up the test environment by creating users, chat, and messages.
        """
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.client.login(username="user1", password="password123")

        # Create chat
        self.chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

        # Create messages
        self.message1 = Message.objects.create(
            chat=self.chat, user=self.user1, content="Hello", timestamp=timezone.now()
        )
        self.message2 = Message.objects.create(
            chat=self.chat, user=self.user2, content="Hi", timestamp=timezone.now()
        )

    def test_delete_message_success(self):
        """
        Test that a logged-in user can successfully delete a message.
        """
        self.client.login(username="user1", password="password123")
        response = self.client.post(
            reverse("chatterbox:delete_message", args=[self.message1.id])
        )

        # Check if the message is deleted
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=self.message1.id)

        self.assertRedirects(
            response,
            reverse("chatterbox:chat", args=[self.user1.username, self.user2.username]),
        )

    def test_delete_message_not_exist(self):
        """
        Test that deleting a non-existent message returns a 404 status code.
        """
        self.client.login(username="user1", password="password123")

        # Attempt to delete a message that doesn't exist
        response = self.client.post(reverse("chatterbox:delete_message", args=[9999]))

        # Ensure that the response is a 404 --not found
        self.assertEqual(response.status_code, 404)

    def test_delete_message_not_logged_in(self):
        """
        Test that a non-logged-in user attempting to delete a message is redirected to the login page.
        """
        # Attempt to delete a message without logging in
        self.client.logout()
        response = self.client.post(
            reverse("chatterbox:delete_message", args=[self.message1.id])
        )

        # Ensure the user is redirected to the login page
        self.assertRedirects(
            response,
            f"/user/login/?next={reverse('chatterbox:delete_message', args=[self.message1.id])}",
        )
