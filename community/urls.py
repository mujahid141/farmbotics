from django.urls import path
from django.urls import re_path
from .views import ChatRoomView, MessageView 

urlpatterns = [
    path('rooms/', ChatRoomView.as_view(), name='chat-rooms'),
    path('rooms/<int:room_id>/messages/', MessageView.as_view(), name='room-messages'),
]
