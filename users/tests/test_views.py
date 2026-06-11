import io
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import Profile


class RegisterViewTests(TestCase):

    def setUp(self):
        self.valid_user_data = {
            "username": "user",
            "password1": "Str0ng_p@ssword",
            "password2": "Str0ng_p@ssword"
        }
        self.url = reverse("users:register")

    def test_register_view_valid(self):
        response = self.client.post(self.url, self.valid_user_data)
        self.assertRedirects(response, reverse("users:login"))


class AccountViewTests(TestCase):

    def setUp(self):
        self.url = reverse("users:account")
        self.user = User.objects.create_user(username="user", password="Str0ng_p@ssword")
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        self.client.login(username="user", password="Str0ng_p@ssword")

    def test_unauthenticated_user_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_account_view_post_valid_data(self):
        valid_data = {"username": "updateduser"}
        self.client.post(self.url, data=valid_data, follow=True)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_account_view_post_valid_avatar(self):
        # temp 100x100 image
        image = Image.new("RGB", (100, 100), color="red")
        byte_arr = io.BytesIO()
        image.save(byte_arr, format="PNG")
        byte_arr.seek(0)
        avatar = SimpleUploadedFile("test_avatar.png", byte_arr.read(), content_type="image/png")
        valid_data = {"username": "user", "avatar": avatar}
        self.client.post(self.url, data=valid_data, follow=True)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertIsNotNone(self.profile.avatar)
