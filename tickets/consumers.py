import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_group_name = f"user_{self.user.id}_notifications"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        # Envía la notificación al cliente
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'tipo': event['tipo'],
            'unread_count': event['unread_count']
        }))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # El ID de la incidencia viene de la URL
        self.incidencia_id = self.scope['url_route']['kwargs']['incidencia_id']
        self.room_group_name = f'chat_{self.incidencia_id}'

        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Recibe mensaje del WebSocket (cliente)
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'typing':
            # Notifica a todos en el grupo (menos al que envía)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_typing',
                    'user': self.scope["user"].get_full_name() or self.scope["user"].username,
                    'is_typing': data.get('is_typing'),
                    'user_id': self.scope["user"].id
                }
            )
        elif message_type == 'message_sent':
            # Notifica a todos que hay un nuevo mensaje
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'user_id': self.scope["user"].id
                }
            )

    # Recibe del grupo y manda al WebSocket (cliente)
    async def chat_typing(self, event):
        # No enviárselo a uno mismo para evitar flasheos innecesarios (JS lo maneja pero mejor filtrar)
        if self.scope["user"].id != event['user_id']:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user': event['user'],
                'is_typing': event['is_typing']
            }))

    async def chat_message(self, event):
        if self.scope["user"].id != event['user_id']:
            await self.send(text_data=json.dumps({
                'type': 'new_message'
            }))
