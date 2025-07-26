import json

from channels.generic.websocket import AsyncWebsocketConsumer

from financije.models import BreakEvenSnapshot


class BreakEvenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return
        self.tenant_id = user.tenant_id
        self.group_name = f"break_even_{self.tenant_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_current_data()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_current_data(self):
        data = list(
            BreakEvenSnapshot.objects.filter(tenant_id=self.tenant_id)
            .order_by("-date", "division")
            .values("division", "date", "revenue", "profit", "break_even_qty", "status")
        )
        await self.send(text_data=json.dumps({"rows": data}))

    async def break_even_update(self, event):
        await self.send_current_data()


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("dashboard", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard", self.channel_name)

    async def receive(self, text_data):
        pass  # Dashboard is push-only

    async def dashboard_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
