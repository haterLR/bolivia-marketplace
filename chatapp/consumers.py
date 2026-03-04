import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatMessage, ChatThread


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'chat_{self.order_id}'
        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.close(code=4001)
            return

        allowed = await self._is_allowed(user.id, self.order_id)
        if not allowed:
            await self.close(code=4003)
            return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data or '{}')
        text = payload.get('text', '').strip()
        if not text:
            return
        msg = await self._save_message(self.scope['user'].id, self.order_id, text)
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'chat.message', 'message': msg},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def _is_allowed(self, user_id, order_id):
        return ChatThread.objects.filter(order_id=order_id).filter(buyer_id=user_id).exists() or ChatThread.objects.filter(order_id=order_id, seller_id=user_id).exists()

    @database_sync_to_async
    def _save_message(self, user_id, order_id, text):
        thread = ChatThread.objects.get(order_id=order_id)
        msg = ChatMessage.objects.create(thread=thread, sender_id=user_id, text=text)
        return {'id': msg.id, 'sender_id': msg.sender_id, 'text': msg.text, 'created_at': msg.created_at.isoformat()}
