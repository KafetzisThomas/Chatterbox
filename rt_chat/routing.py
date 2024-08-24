from django.urls import re_path
from .consumers import ChatConsumer

# WebSocket URL pattern with both usernames
websocket_urlpatterns = [
    re_path(
        r"^ws/chat/(?P<username>\w+)/(?P<other_username>\w+)/$", ChatConsumer.as_asgi()
    ),
]
