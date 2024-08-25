from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    """
    Extending User model by adding an avatar.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default="default.png", upload_to="profile_images/")

    def save(self, *args, **kwargs):
        """
        Resize the avatar image.
        """
        super().save()
        img = Image.open(self.avatar.path)
        if img.height > 300 or img.width > 300:
            new_img = (300, 300)
            img.thumbnail(new_img)
            img.save(self.avatar.path)

    def __str__(self):
        return self.user.username
