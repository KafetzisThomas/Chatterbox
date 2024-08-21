from django.db import models
from django.contrib.auth.models import User


class ChatGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(User, related_name="chat_groups")

    def __str__(self):
        return self.name


class Message(models.Model):
    group = models.ForeignKey(
        ChatGroup, on_delete=models.CASCADE, related_name="messages"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."
