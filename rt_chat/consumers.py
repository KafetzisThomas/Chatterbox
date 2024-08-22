import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatGroup, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    A WebSocket consumer for handling real-time chat functionality.
    """

    async def connect(self):
        """
        Handle the WebSocket connection when a client connects.
        """
        # Extract the group name from the URL route
        self.group_name = self.scope["url_route"]["kwargs"]["group_name"]
        # Fetch the chat group from the database
        self.group = await self.get_group(self.group_name)
        # Define the group name used by the channel layer
        self.room_group_name = f"chat_{self.group_name}"

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

        # Get the user and save the message to the db
        user = await self.get_user(username)
        await self.save_message(self.group, user, message)

        # Display the message to the chat group
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
    def get_group(self, group_name):
        """
        Retrieve a chat group from the db by its name.
        """
        return ChatGroup.objects.get(name=group_name)

    @database_sync_to_async
    def get_user(self, username):
        """
        Retrieve a user from the db by their username.
        """
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_message(self, group, user, message):
        """
        Save message to the db.
        """
        Message.objects.create(group=group, user=user, content=message)
