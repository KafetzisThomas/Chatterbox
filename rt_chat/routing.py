from django.urls import path
from .consumers import ChatConsumer

# Route WebSocket connections to ChatConsumer
websocket_urlpatterns = [
    path("", ChatConsumer.as_asgi()),
]
