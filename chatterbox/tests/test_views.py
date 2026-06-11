import io
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import PrivateChat, Message


class ChatListViewTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="Str0ng_p@ssword")
        self.user2 = User.objects.create_user(username="user2", password="Str0ng_p@ssword")
        self.user3 = User.objects.create_user(username="user3", password="Str0ng_p@ssword")
        self.client.login(username="user1", password="Str0ng_p@ssword")

        self.chat1 = PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        self.chat2 = PrivateChat.objects.create(user1=self.user1, user2=self.user3)

        Message.objects.create(chat=self.chat1, user=self.user1, content="Hello!")
        Message.objects.create(chat=self.chat2, user=self.user3, content="Hey there!")

        self.url = reverse("chatterbox:chat_list")

    def test_unauthenticated_user_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_contains_chats(self):
        response = self.client.get(self.url)
        chats = response.context["chats_with_last_messages"]
        self.assertEqual(len(chats), 2)

        results = {(entry[0].username, entry[1].content) for entry in chats}
        self.assertEqual(results, {("user2", "Hello!"), ("user3", "Hey there!")})


class CreateChatViewTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="Str0ng_p@ssword")
        self.user2 = User.objects.create_user(username="user2", password="Str0ng_p@ssword")
        self.user3 = User.objects.create_user(username="user3", password="Str0ng_p@ssword")
        self.client.login(username="user1", password="Str0ng_p@ssword")

        self.url = reverse("chatterbox:create_chat")
    
    def test_unauthenticated_user_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_create_chat_valid(self):
        form_data = {"username": "user2"}
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)

        chat = PrivateChat.objects.get(user1=self.user1, user2=self.user2)
        self.assertIsNotNone(chat)  # chat created/fetched

        expected_url = reverse("chatterbox:chat", args=["user1", "user2"])
        self.assertRedirects(response, expected_url)

    def test_create_chat_self_chat(self):
        form_data = {"username": "user1"}
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)

    def test_create_chat_user_does_not_exist(self):
        form_data = {"username": "nonexistentuser"}
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)

    def test_create_chat_reverse_user_ordering(self):
        self.client.login(username="user3", password="Str0ng_p@ssword")
        form_data = {"username": "user1"}
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PrivateChat.objects.filter(user1=self.user1, user2=self.user3).exists())

    def test_create_chat_existing_chat_not_duplicated(self):
        PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        form_data = {"username": "user2"}
        self.client.post(self.url, data=form_data)
        self.assertEqual(PrivateChat.objects.filter(user1=self.user1, user2=self.user2).count(), 1)


class ChatViewTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="Str0ng_p@ssword")
        self.user2 = User.objects.create_user(username="user2", password="Str0ng_p@ssword")
        self.user3 = User.objects.create_user(username="user3", password="Str0ng_p@ssword")
        self.client.login(username="user1", password="Str0ng_p@ssword")

        self.chat1 = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

        self.message1 = Message.objects.create(chat=self.chat1, user=self.user1, content="Hello!")
        self.message2 = Message.objects.create(chat=self.chat1, user=self.user2, content="Hi!")

        self.chat_url = reverse("chatterbox:chat", args=[self.user1.username, self.user2.username])
        self.chat_list_url = reverse("chatterbox:chat_list")

    def test_unauthenticated_user_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 302)

    def test_chat_view_redirects_if_request_user_is_not_url_user(self):
        self.client.login(username="user3", password="Str0ng_p@ssword")
        response = self.client.get(self.chat_url)
        self.assertRedirects(response, self.chat_list_url)

    def test_chat_view_redirects_if_same_user_in_url(self):
        url = reverse("chatterbox:chat", args=[self.user1.username, self.user1.username])
        response = self.client.get(url)
        self.assertRedirects(response, self.chat_list_url)


class UploadImageViewTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="Str0ng_p@ssword")
        self.user2 = User.objects.create_user(username="user2", password="Str0ng_p@ssword")
        self.client.login(username="user1", password="Str0ng_p@ssword")

        self.url = reverse("chatterbox:upload_image", args=[self.user1.username, self.user2.username])

    def test_upload_image_no_file(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_upload_image_success(self):
        img = Image.new("RGB", (100, 100), color="red")
        byte_arr = io.BytesIO()
        img.save(byte_arr, format="PNG")
        byte_arr.seek(0)

        image = SimpleUploadedFile("test.png", byte_arr.read(), content_type="image/png")
        response = self.client.post(self.url, {"image": image})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("image_name", data)
        self.assertIn("image_url", data)


class DeleteChatViewTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="Str0ng_p@ssword")
        self.user2 = User.objects.create_user(username="user2", password="Str0ng_p@ssword")
        self.user3 = User.objects.create_user(username="user3", password="Str0ng_p@ssword")
        self.client.login(username="user1", password="Str0ng_p@ssword")

        self.chat1 = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

        self.message1 = Message.objects.create(chat=self.chat1, user=self.user1, content="Hello!")
        self.message2 = Message.objects.create(chat=self.chat1, user=self.user2, content="Hi!")

        self.url = reverse("chatterbox:delete_chat", kwargs={
            "username": self.user1.username, "other_username": self.user2.username},
        )

    def test_unauthenticated_user_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_delete_chat_success(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("chatterbox:chat_list"))
        self.assertFalse(PrivateChat.objects.filter(id=self.chat1.id).exists())
        self.assertFalse(Message.objects.filter(id=self.message1.id).exists())
        self.assertFalse(Message.objects.filter(id=self.message2.id).exists())

    def test_delete_chat_forbidden_for_non_participant(self):
        self.client.login(username="user3", password="Str0ng_p@ssword")
        self.client.post(self.url)
        self.assertTrue(PrivateChat.objects.filter(id=self.chat1.id).exists())


class DeleteMessageViewTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="Str0ng_p@ssword")
        self.user2 = User.objects.create_user(username="user2", password="Str0ng_p@ssword")
        self.client.login(username="user1", password="Str0ng_p@ssword")

        self.chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

        self.message1 = Message.objects.create(chat=self.chat, user=self.user1, content="Hello")
        self.message2 = Message.objects.create(chat=self.chat, user=self.user2, content="Hi")

        self.url = reverse("chatterbox:delete_message", args=[self.message1.id])

    def test_unauthenticated_user_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_delete_message_success(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Message.objects.filter(id=self.message1.id).exists())

    def test_delete_message_forbidden_for_other_user(self):
        url = reverse("chatterbox:delete_message", args=[self.message2.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Message.objects.filter(id=self.message2.id).exists())

    def test_delete_message_not_exist(self):
        response = self.client.post(reverse("chatterbox:delete_message", args=[9999]))
        self.assertEqual(response.status_code, 404)
