import json
from channels.generic.websocket import AsyncWebsocketConsumer

class UpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("updates", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            "updates",
            {
                "type": "send_update",
                "message": data["message"],
            }
        )

    async def send_update(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))