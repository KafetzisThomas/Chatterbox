import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    """
    A WebSocket consumer for handling real-time chat functionality.
    """

    async def connect(self):
        """
        Handle the WebSocket connection when a client connects.
        """
        # Extract usernames from the URL route
        username1 = self.scope["url_route"]["kwargs"]["username"]
        username2 = self.scope["url_route"]["kwargs"]["other_username"]

        # Create a unique group name based on both usernames
        self.group_name = self.create_group_name(username1, username2)

        # Define the group name used by the channel layer
        self.room_group_name = f"chat_{self.group_name}"

        # Fetch or create the chat group from the database
        self.chat = await self.get_or_create_chat(username1, username2)

        # Add the WebSocket connection to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle the WebSocket disconnection.
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages from clients.
        """
        data = json.loads(text_data)  # Parse the JSON data
        message = data["message"]
        username = data["username"]

        # Get the user and save the message to the database
        user = await self.get_user(username)
        await self.save_message(self.chat, user, message)

        # Display the message to the WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_message",  # Specify the type of event to be handled
                "message": message,
                "username": username,
            },
        )

    async def send_message(self, event):
        """
        Send the message to the WebSocket client.
        """
        message = event["message"]
        username = event["username"]

        await self.send(
            text_data=json.dumps({"message": message, "username": username})
        )

    @database_sync_to_async
    def get_user(self, username):
        """
        Retrieve a user from the database by their username.
        """
        from django.contrib.auth.models import User

        return User.objects.get(username=username)

    @database_sync_to_async
    def get_or_create_chat(self, username1, username2):
        """
        Get or create a private chat between two users.
        """
        from django.contrib.auth.models import User
        from .models import PrivateChat

        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)
        chat, _ = (
            PrivateChat.objects.get_or_create(user1=user1, user2=user2)
            if user1.id < user2.id
            else PrivateChat.objects.get_or_create(user1=user2, user2=user1)
        )
        return chat

    @database_sync_to_async
    def save_message(self, chat, user, message):
        """
        Save message to the database.
        """
        from .models import Message

        Message.objects.create(chat=chat, user=user, content=message)

    def create_group_name(self, username1, username2):
        """
        Create a group name based on two usernames, in a consistent order.
        """
        return (
            f"{username1}_{username2}"
            if username1 < username2
            else f"{username2}_{username1}"
        )
