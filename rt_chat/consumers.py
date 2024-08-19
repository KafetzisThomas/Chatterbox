import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Create a group name for the chatroom.
        Add the group to the channel layer group.
        """
        self.roomGroupName = "group_chat"
        await self.channel_layer.group_add(self.roomGroupName, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Remove the instance from the group.
        """
        await self.channel_layer.group_discard(self.roomGroupName, self.channel_layer)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        await self.channel_layer.group_send(
            self.roomGroupName,
            {
                "type": "sendMessage",
                "message": message,
                "username": username,
            },
        )

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]
        await self.send(
            text_data=json.dumps({"message": message, "username": username})
        )
