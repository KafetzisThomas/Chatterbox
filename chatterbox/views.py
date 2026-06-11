from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .models import PrivateChat, Message
from .forms import PrivateChatForm

@login_required
def chat_list(request):
    chats = PrivateChat.objects.filter(user1=request.user) | PrivateChat.objects.filter(user2=request.user)
    chats_with_last_messages = []

    for chat in chats:
        last_message = chat.messages.order_by("-timestamp").first()
        time_diff = last_message.get_time_diff() if last_message else "No messages yet"
        other_user = chat.user1 if chat.user2 == request.user else chat.user2
        chats_with_last_messages.append((other_user, last_message, time_diff))

    context = {"chats_with_last_messages": chats_with_last_messages}
    return render(request, "chatterbox/chat_list.html", context)

@login_required
def create_chat(request):
    if request.method == "POST":
        form = PrivateChatForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            other_user = User.objects.filter(username=username).first()

            if not other_user:
                messages.error(request, "Username doesn't exist.")
                return redirect("chatterbox:create_chat")

            if other_user == request.user:
                messages.success(request, "You can't start a chat with yourself.")
                return redirect("chatterbox:create_chat")

            # fetch/create chat
            if request.user.id < other_user.id:
                chat, _ = PrivateChat.objects.get_or_create(user1=request.user, user2=other_user)
            else:
                chat, _ = PrivateChat.objects.get_or_create(user1=other_user, user2=request.user)

            return HttpResponseRedirect(reverse("chatterbox:chat", args=[request.user.username, other_user.username]))

    else:
        form = PrivateChatForm()

    return render(request, "chatterbox/create_chat.html", {"form": form})

@login_required
def chat(request, username, other_username):
    user1 = get_object_or_404(User, username=username)
    user2 = get_object_or_404(User, username=other_username)

    if user1 == user2:
        return redirect("chatterbox:chat_list")

    if request.user == user1:
        # fetch/create chat
        if user1.id < user2.id:
            chat, _ = PrivateChat.objects.get_or_create(user1=user1, user2=user2)
        else:
            chat, _ = PrivateChat.objects.get_or_create(user1=user2, user2=user1)
    else:
        return redirect("chatterbox:chat_list")

    messages = Message.objects.filter(chat=chat).order_by("timestamp")

    # zip with previous message
    messages_with_prev = []
    prev = None
    for message in messages:
        messages_with_prev.append((message, prev))
        prev = message

    context = {"messages_with_prev": messages_with_prev, "current_user": user1, "other_user": user2}
    return render(request, "chatterbox/chat.html", context)

@login_required
@require_POST
def upload_image(request, username, other_username):
    image = request.FILES.get("image")
    if not image:
        return JsonResponse({"error": "No image provided."}, status=400)

    message = Message(user=request.user, chat_id=0)
    message.image.save(image.name, image, save=False)
    return JsonResponse({"image_name": message.image.name, "image_url": message.image.url})

@login_required
def delete_chat(request, username, other_username):
    try:
        user1 = User.objects.get(username=username)
        user2 = User.objects.get(username=other_username)

        if user1.id < user2.id:
            chat = PrivateChat.objects.get(user1=user1, user2=user2)
        else:
            chat = PrivateChat.objects.get(user1=user2, user2=user1)
        chat.delete()
        messages.success(request, "Chat has been successfully deleted!")

    except User.DoesNotExist:
        messages.error(request, "One or both users do not exist.")
    except PrivateChat.DoesNotExist:
        messages.error(request, "Chat does not exist.")
    except Exception:
        messages.error(request, "An unexpected error occurred.")

    return redirect("chatterbox:chat_list")

@login_required
@require_POST
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.user != request.user:
        return HttpResponseForbidden("Not allowed to delete this message.")

    chat = message.chat
    other_user = chat.user2 if chat.user1 == request.user else chat.user1
    message.delete()

    return redirect("chatterbox:chat", username=request.user.username, other_username=other_user.username)
