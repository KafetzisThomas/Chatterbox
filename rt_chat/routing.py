from django.urls import path
from .consumers import ChatConsumer

# Route WebSocket connections to ChatConsumer for a specific chat group
websocket_urlpatterns = [
    path("ws/chat/<str:group_name>/", ChatConsumer.as_asgi()),
]
