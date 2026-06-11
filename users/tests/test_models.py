import io
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from PIL import Image
from ..models import Profile


class ProfileModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="user", password="password123")

    def test_profile_creation(self):
        profile, _ = Profile.objects.get_or_create(user=self.user)
        self.assertEqual(profile.user, self.user)

    def test_default_avatar(self):
        profile, _ = Profile.objects.get_or_create(user=self.user)
        self.assertFalse(profile.avatar)

    def test_avatar_resizing(self):
        # temp 500x500 image
        image = Image.new("RGB", (500, 500), "white")
        byte_io = io.BytesIO()
        image.save(byte_io, format="JPEG")
        byte_io.seek(0)

        avatar = SimpleUploadedFile("test_avatar.jpg", byte_io.getvalue(), content_type="image/jpeg")
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.avatar = avatar
        profile.save()

        img = Image.open(profile.avatar.path)
        self.assertLessEqual(img.height, 300)
        self.assertLessEqual(img.width, 300)
