from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ChatRoom, Message
from users.models import CustomUser as User
from .serializers import ChatRoomSerializer, MessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status

class ChatRoomView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        rooms = ChatRoom.objects.all()
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, room_id):
        messages = Message.objects.filter(room_id=room_id).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, room_id):
        data = request.data.copy()
        print("Request data:", data)

        # Retrieve the Room object
        room = get_object_or_404(ChatRoom, id=room_id)
        sender = data['sender']
        
        # Retrieve the authenticated user
        user = User.objects.get(id=sender)

        # Perform manual validation
        content = data.get("content", "").strip()
        if not content:
            return Response({"error": "Content is required and cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the message
        try:
            message = Message.objects.create(
                room=room,
                sender=user,
                content=content
            )
            # Prepare response data
            
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error creating message:", e)
            return Response({"error": "Failed to create the message."} )

