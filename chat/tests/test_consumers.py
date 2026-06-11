import os
from django.test import TransactionTestCase
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.contrib.auth.models import User
from channels.auth import AuthMiddlewareStack
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
import chat.routing
from ..consumers import Chat
from ..models import PrivateChat, Message

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

# simulate asgi without AllowedHostsOriginValidator() for testing
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(chat.routing.websocket_urlpatterns)
        ),
    }
)


class ChatTests(TransactionTestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="Str0ng_p@ssword")
        self.user2 = User.objects.create_user(username="user2", password="Str0ng_p@ssword")

        self.chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

    async def connect_communicator(self, communicator):
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

    async def disconnect_communicator(self, communicator):
        await communicator.disconnect()

    async def test_connect_and_disconnect(self):
        communicator = WebsocketCommunicator(application, f"/ws/chat/user1/user2/")
        await self.connect_communicator(communicator)
        await self.disconnect_communicator(communicator)

    async def test_receive_message(self):
        communicator = WebsocketCommunicator(application, f"/ws/chat/user1/user2/")
        await self.connect_communicator(communicator)

        message = {"message": "test message", "username": "user1"}
        await communicator.send_json_to(message)

        response = await communicator.receive_json_from()
        self.assertEqual(response["message"], message["message"])
        self.assertEqual(response["username"], message["username"])
        self.assertEqual(response.get("image_url"), "")

        await self.disconnect_communicator(communicator)

    async def test_receive_and_save_image(self):
        communicator = WebsocketCommunicator(application, f"/ws/chat/user1/user2/")
        await self.connect_communicator(communicator)

        message = {
            "message": "test message",
            "username": "user1",
            "image_name": "chat_images/test.png",
            "image_url": "/media/chat_images/test.png"
        }

        await communicator.send_json_to(message)

        response = await communicator.receive_json_from()
        self.assertEqual(response["username"], message["username"])
        self.assertEqual(response["message"], message["message"])
        self.assertEqual(response["image_url"], message["image_url"])

        saved_message = await database_sync_to_async(Message.objects.filter)(
            chat=self.chat, user=self.user1, image="chat_images/test.png"
        )
        self.assertTrue(await database_sync_to_async(saved_message.exists)())

        await self.disconnect_communicator(communicator)

    async def test_save_message_to_database(self):
        communicator = WebsocketCommunicator(application, f"/ws/chat/user1/user2/")
        await self.connect_communicator(communicator)

        message = {"message": "test message", "username": "user1"}

        await communicator.send_json_to(message)
        await communicator.receive_json_from()

        saved_message = await database_sync_to_async(Message.objects.filter)(
            chat=self.chat, user=self.user1, content="test message"
        )
        self.assertTrue(await database_sync_to_async(saved_message.exists)())

        await self.disconnect_communicator(communicator)

    async def test_create_group_name(self):
        consumer = Chat(scope={"type": "websocket"})
        group_name = consumer.create_group_name("user1", "user2")
        self.assertEqual(group_name, "user1_user2")

        # reversed usernames
        group_name_reverse = consumer.create_group_name("user2", "user1")
        self.assertEqual(group_name_reverse, "user1_user2")
