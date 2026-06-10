import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone

def chat_image_path(instance, filename):
    """
    Store chat images with UUID filenames to avoid collisions.
    """
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    return f"chat_images/{unique_filename}"


class PrivateChat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_user2")

    def __str__(self):
        return f"{self.user1.username} and {self.user2.username}"


class Message(models.Model):
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to=chat_image_path, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_time_diff(self):
        if self.timestamp:
            now_time = datetime.now(timezone.utc)
            timediff = now_time - self.timestamp

            if timediff < timedelta(minutes=1):
                return f"{int(timediff.total_seconds())} seconds ago"
            elif timediff < timedelta(hours=1):
                return f"{int(timediff.total_seconds() // 60)} minutes ago"
            elif timediff < timedelta(days=1):
                return f"{int(timediff.total_seconds() // 3600)} hours ago"
            else:
                return f"{int(timediff.total_seconds() // 86400)} days ago"

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
