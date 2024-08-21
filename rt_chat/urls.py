"""Defines URL patterns for rt_chat"""

from django.urls import path
from rt_chat import views

app_name = "rt_chat"
urlpatterns = [
    # Global chat group page
    path("", views.chat, name="chat"),
    # Create a new private chat group page
    path("create-group/", views.create_group, name="create_group"),
    # Join an existing private group chat page
    path("chat/<str:group_name>/", views.chat, name="chat"),
]
