from datetime import datetime, timedelta, timezone
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

    def get_time_diff(self):
        if self.timestamp:
            now_time = datetime.now(timezone.utc)
            timediff = now_time - self.timestamp

            # Convert the timediff to human-readable format
            if timediff < timedelta(minutes=1):
                return f"{int(timediff.total_seconds())} seconds ago"
            elif timediff < timedelta(hours=1):
                return f"{int(timediff.total_seconds() // 60)} minutes ago"
            elif timediff < timedelta(days=1):
                return f"{int(timediff.total_seconds() // 3600)} hours ago"
            else:
                return f"{int(timediff.total_seconds() // 86400)} days ago"

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."
