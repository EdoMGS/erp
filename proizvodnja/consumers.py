# proizvodnja/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotifikacijaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return
        
        self.group_name = f"notifikacije_{user.id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # testna poruka
        await self.send(text_data=json.dumps({"message": "Primljena poruka!"}))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))
