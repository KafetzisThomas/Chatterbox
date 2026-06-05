import json
import base64
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import PrivateChat, Message


class Chat(AsyncWebsocketConsumer):
    async def connect(self):
        # extract both usernames from url route
        username1 = self.scope["url_route"]["kwargs"]["username"]
        username2 = self.scope["url_route"]["kwargs"]["other_username"]

        # create unique group name based on both usernames
        self.group_name = self.create_group_name(username1, username2)
        self.room_group_name = f"chat_{self.group_name}"

        # fetch/create chat group from database
        self.chat = await self.get_or_create_chat(username1, username2)

        # add websocket connection to group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        image_data = data.get("image", "")
        username = data["username"]
        user = await self.get_user(username)

        image = base64.b64decode(image_data) if image_data else None

        await self.save_message(self.chat, user, message, image)

        # display message to websocket group
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "send_message",
            "username": username,
            "message": message,
            "image": image_data
        })

    async def send_message(self, event):
        message = event["message"]
        username = event["username"]
        image = event["image"]
        await self.send(
            text_data=json.dumps({"username": username, "message": message, "image": image})
        )

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def get_or_create_chat(self, username1, username2):
        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)

        if user1.id < user2.id:
            chat, _ = PrivateChat.objects.get_or_create(user1=user1, user2=user2)
        else:
            PrivateChat.objects.get_or_create(user1=user2, user2=user1)
        return chat

    @database_sync_to_async
    def save_message(self, chat, user, message, image):
        Message.objects.create(chat=chat, user=user, content=message, image=image)

    def create_group_name(self, username1, username2):
        return f"{username1}_{username2}" if username1 < username2 else f"{username2}_{username1}"
