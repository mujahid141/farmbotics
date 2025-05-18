from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>[\w\s]+)/$', ChatConsumer.as_asgi()),  # Allows spaces in the room name
]
