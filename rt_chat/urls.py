"""Defines URL patterns for rt_chat"""

from django.urls import path
from rt_chat import views

app_name = "rt_chat"
urlpatterns = [
    # Chat list page
    path("", views.chat_list, name="chat_list"),
    # Create chat page
    path("create_chat/", views.create_chat, name="create_chat"),
    # Private chat page
    path("chat/<str:username>/<str:other_username>/", views.chat, name="chat"),
]
