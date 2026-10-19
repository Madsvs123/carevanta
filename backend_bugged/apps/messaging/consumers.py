from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone


class MessagingConsumer(AsyncJsonWebsocketConsumer):
  async def connect(self):
        user = self.scope.get("user")
        if user is None or user.is_anonymous:
            await self.close()
            return
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        if not await self._user_in_conversation(user.id, self.conversation_id):
            await self.close()
            return
        self.group_name = f"conversation_{self.conversation_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        text = (content.get("content") or "").strip()
        if not text:
            return
        message = await self._persist_message(self.scope["user"].id, self.conversation_id, text)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "message.new",
                "id": message["id"],
                "sender_id": message["sender_id"],
                "content": message["content"],
                "created_at": message["created_at"],
            },
        )

    async def message_new(self, event):
        await self.send_json(event)

    @database_sync_to_async
    def _user_in_conversation(self, user_id, conversation_id):
        from .models import Conversation

        return Conversation.objects.filter(pk=conversation_id, participants__id=user_id).exists()

    @database_sync_to_async
    def _persist_message(self, user_id, conversation_id, content):
        from .models import Conversation, Message

        conversation = Conversation.objects.get(pk=conversation_id)
        msg = Message.objects.create(conversation=conversation, sender_id=user_id, content=content)
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=["last_message_at", "updated_at"])
        return {
            "id": msg.id,
            "sender_id": user_id,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
        }
