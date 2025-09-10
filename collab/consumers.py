import json
import jwt
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from collab.models import ChatMessage, Collaboration

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.collab_id = self.scope['url_route']['kwargs']['collab_id']
        self.room_group_name = f'collab_{self.collab_id}'

        # Получаем токен из query параметров: ?token=...
        query_string = parse_qs(self.scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        if token is None:
            await self.close(code=4001)
            return

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            self.user = await self.get_user(payload["user_id"])
            self.scope["user"] = self.user
        except Exception:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')

        if not message:
            return

        # Сохраняем сообщение в базу данных
        await self.save_message(self.user, self.collab_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.id,
                'username': self.user.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender'],
            'sender_username': event['username'],
        }))

    @sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @sync_to_async
    def save_message(self, user, collab_id, content):
        collaboration = Collaboration.objects.get(id=collab_id)
        return ChatMessage.objects.create(
            sender=user,
            collaboration=collaboration,  # ✅ правильное имя поля
            message=content                # ✅ правильное имя поля
        )
