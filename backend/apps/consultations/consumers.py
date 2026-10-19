"""WebSocket consumer for video consultations."""
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone


class ConsultationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route]["kwargs"]["room_id"]
        self.group_name = f"consultation_{self.room_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "connection.event", "event": "joined", "user_id": self.scope["user"].id},
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        msg_type = content.get("type", "chat")
        if msg_type == "chat":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.message",
                    "sender_id": self.scope["user"].id,
                    "content": content.get("content", ""),
                    "timestamp": timezone.now().isoformat(),
                },
            )
        elif msg_type == "webrtc_signal":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "webrtc.signal",
                    "sender_id": self.scope["user"].id,
                    "signal": content.get("signal"),
                },
            )
        elif msg_type == "connection_status":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "connection.status",
                    "sender_id": self.scope["user"].id,
                    "quality": content.get("quality"),
                },
            )

    async def chat_message(self, event):
        await self.send_json(event)

    async def webrtc_signal(self, event):
        await self.send_json(event)

    async def connection_event(self, event):
        await self.send_json(event)

    async def connection_status(self, event):
        await self.send_json(event)
