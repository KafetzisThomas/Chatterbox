"""Defines URL patterns for rt_chat"""

from django.urls import path
from rt_chat import views

app_name = "rt_chat"
urlpatterns = [
    path("", views.chat, name="chat"),
]
