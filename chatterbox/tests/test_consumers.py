from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from ..models import PrivateChat, Message
from main.asgi import application


class ChatConsumerTests(TransactionTestCase):
    """
    Test suite for the ChatConsumer class.
    """

    def setUp(self):
        """
        Set up the test environment by creating users and chats.
        """
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")

        # Create chats
        self.chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

    async def connect_communicator(self, communicator):
        """
        Connects the WebSocket communicator and asserts that the connection is successful.
        """
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

    async def disconnect_communicator(self, communicator):
        """
        Disconnects the WebSocket communicator.
        """
        await communicator.disconnect()

    async def test_connect_and_disconnect(self):
        """
        Test that the WebSocket connection and disconnection work as expected.
        """
        communicator = WebsocketCommunicator(application, f"/ws/chat/user1/user2/")
        await self.connect_communicator(communicator)
        await self.disconnect_communicator(communicator)

    async def test_receive_message(self):
        """
        Test that a message sent to the WebSocket is correctly received and processed.
        """
        communicator = WebsocketCommunicator(application, f"/ws/chat/user1/user2/")
        await self.connect_communicator(communicator)

        message = {"message": "Hello, World!", "username": "user1"}

        # Send a message from the client to the WebSocket
        await communicator.send_json_to(message)

        # Receive a message from the WebSocket
        response = await communicator.receive_json_from()

        self.assertEqual(response["message"], message["message"])
        self.assertEqual(response["username"], message["username"])

        await self.disconnect_communicator(communicator)

    async def test_save_message_to_database(self):
        """
        Test that a message sent through the WebSocket is saved to the database.
        """
        communicator = WebsocketCommunicator(application, f"/ws/chat/user1/user2/")
        await self.connect_communicator(communicator)

        message = {"message": "Hello, World!", "username": "user1"}

        await communicator.send_json_to(message)
        await communicator.receive_json_from()

        # Check if the message is saved in the database
        saved_message = await database_sync_to_async(Message.objects.filter)(
            chat=self.chat, user=self.user1, content="Hello, World!"
        )
        self.assertTrue(await database_sync_to_async(saved_message.exists)())

        await self.disconnect_communicator(communicator)

    async def test_create_group_name(self):
        """
        Test that the create_group_name method correctly generates a consistent group name.
        """
        from ..consumers import ChatConsumer

        consumer = ChatConsumer(scope={"type": "websocket"})

        # Create a group name with two usernames
        group_name = consumer.create_group_name("user1", "user2")
        self.assertEqual(group_name, "user1_user2")

        # Create a group name with reversed usernames
        group_name_reverse = consumer.create_group_name("user2", "user1")
        self.assertEqual(group_name_reverse, "user1_user2")
