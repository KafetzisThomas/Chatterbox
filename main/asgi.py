"""
ASGI config for main project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from rt_chat import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

application = (
    ProtocolTypeRouter(  # Route incoming connections based on their protocol type
        {
            "http": get_asgi_application(),  # Standard HTTP handling
            "websocket": AuthMiddlewareStack(
                URLRouter(routing.websocket_urlpatterns)
            ),  # WebSocket handling with authentication
        }
    )
)
