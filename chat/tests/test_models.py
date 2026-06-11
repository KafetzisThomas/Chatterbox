import io
from PIL import Image
from django.test import TestCase
from django.contrib.auth.models import User
from ..models import PrivateChat, Message


class PrivateChatModelTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username="user1", password="password123")
        self.user2 = User.objects.create(username="user2", password="password123")

    def test_private_chat_creation(self):
        chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        self.assertEqual(chat.user1, self.user1)
        self.assertEqual(chat.user2, self.user2)

    def test_cascade_deletion_user1(self):
        chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        self.user1.delete()
        self.assertFalse(PrivateChat.objects.filter(id=chat.id).exists())

    def test_cascade_deletion_user2(self):
        chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)
        self.user2.delete()
        self.assertFalse(PrivateChat.objects.filter(id=chat.id).exists())


class MessageModelTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.chat = PrivateChat.objects.create(user1=self.user1, user2=self.user2)

    def test_message_creation(self):
        message = Message.objects.create(chat=self.chat, user=self.user1, content="Hello World!")
        self.assertEqual(message.chat, self.chat)
        self.assertEqual(message.user, self.user1)
        self.assertEqual(message.content, "Hello World!")

    def test_message_with_image(self):
        # temp 100x100 image
        image = Image.new("RGB", (100, 100), "white")
        byte_io = io.BytesIO()
        image.save(byte_io, format="JPEG")
        byte_io.seek(0)

        image_data = byte_io.getvalue()
        message = Message.objects.create(chat=self.chat, user=self.user1, content="", image=image_data)
        self.assertEqual(message.content, "")
        self.assertEqual(message.image, image_data)

    def test_cascade_deletion_chat(self):
        message = Message.objects.create(chat=self.chat, user=self.user1, content="Goodbye!")
        self.chat.delete()
        self.assertFalse(Message.objects.filter(id=message.id).exists())

    def test_cascade_deletion_user(self):
        message = Message.objects.create(chat=self.chat, user=self.user1, content="Goodbye!")
        self.user1.delete()
        self.assertFalse(Message.objects.filter(id=message.id).exists())
