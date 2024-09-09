"""Defines URL patterns for chatterbox"""

from django.urls import path
from . import views

app_name = "chatterbox"
urlpatterns = [
    # Chat list page
    path("", views.chat_list, name="chat_list"),
    # Create chat page
    path("create_chat/", views.create_chat, name="create_chat"),
    # Private chat page
    path("chat/<str:username>/<str:other_username>/", views.chat, name="chat"),
    # Delete chat page
    path(
        "chat/<str:username>/<str:other_username>/delete_chat/",
        views.delete_chat,
        name="delete_chat",
    ),
    # Delete message page
    path(
        "delete_message/<int:message_id>/", views.delete_message, name="delete_message"
    ),
]
