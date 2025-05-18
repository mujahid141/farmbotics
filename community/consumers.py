import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get room name from URL parameter
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name.replace(' ', '_')}"  # Replacing spaces with underscores for group name

        # Create or get the ChatRoom instance
        self.room, created = await database_sync_to_async(ChatRoom.objects.get_or_create)(name=self.room_name)

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse the message data
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']

        # Save the message to the database
        await database_sync_to_async(self.save_message)(user, message)

        # Send the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    def save_message(self, user, message):
        # Save the message to the database
        Message.objects.create(
            sender=user,
            room=self.room,
            content=message
        )
