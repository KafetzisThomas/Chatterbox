import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    """
    A WebSocket consumer for handling real-time chat functionality.
    """

    async def connect(self):
        """
        Handle the WebSocket connection when a client connects.
        """
        self.room_group_name = "group_chat"  # Define a group name for the chat room
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )  # Add the connection to the group
        await self.accept()  # Accept the WebSocket connection

    async def disconnect(self, close_code):
        """
        Handles the WebSocket disconnection.
        """
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )  # Remove the connection from the group

    async def receive(self, text_data):
        """
        Handle incoming messages from the WebSocket.
        """
        data = json.loads(text_data)  # Parse the JSON data
        message = data["message"]
        username = data["username"]

        # Send the message to the chat room group
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
        Send the message to the WebSocket.
        """
        message = event["message"]
        username = event["username"]

        # Send the message to the WebSocket client
        await self.send(
            text_data=json.dumps({"message": message, "username": username})
        )
