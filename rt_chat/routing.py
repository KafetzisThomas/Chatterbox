from django.urls import path
from .consumers import ChatConsumer

# Routing to the URL ChatConsumer which will handle the chat functionality.
websocket_urlpatterns = [
    path("", ChatConsumer.as_asgi()),
]
