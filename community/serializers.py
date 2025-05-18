from rest_framework import serializers
from .models import ChatRoom, Message

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'room', 'content', 'timestamp']
