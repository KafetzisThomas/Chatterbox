from django.urls import re_path
from .consumers import Chat

websocket_urlpatterns = [
    re_path(r"^ws/chat/(?P<username>\w+)/(?P<other_username>\w+)/$", Chat.as_asgi()),
]
