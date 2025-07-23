import io
from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    """
    Extending User model by adding an avatar stored as bytes.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.BinaryField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Resize the avatar image.
        Convert it to bytes.
        """
        if self.avatar:
            img = Image.open(io.BytesIO(self.avatar))
            if img.height > 300 or img.width > 300:
                new_img = (300, 300)
                img.thumbnail(new_img)

            byte_io = io.BytesIO()
            img.save(byte_io, format="PNG")
            self.avatar = byte_io.getvalue()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
