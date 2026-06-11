from django.urls import path
from . import views

app_name = "chatterbox"
urlpatterns = [
    path("", views.chat_list, name="chat_list"),
    path("chat/create/", views.create_chat, name="create_chat"),
    path("chat/<str:username>/<str:other_username>/", views.chat, name="chat"),
    path("chat/<str:username>/<str:other_username>/upload_image/", views.upload_image, name="upload_image"),
    path("chat/<str:username>/<str:other_username>/delete/", views.delete_chat, name="delete_chat"),
    path("message/<int:message_id>/delete/", views.delete_message, name="delete_message"),
]
