"""
ASGI config for main project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

import chatterbox.routing

# Route incoming connections based on their protocol type
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,  # Standard HTTP handling
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(chatterbox.routing.websocket_urlpatterns))
        ),  # WebSocket handling with authentication
    }
)
