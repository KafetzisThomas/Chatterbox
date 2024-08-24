from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from .models import PrivateChat, Message
from .forms import PrivateChatForm


@login_required
def chat_list(request):
    # Get all private chats involving the current user
    chats = PrivateChat.objects.filter(user1=request.user) | PrivateChat.objects.filter(
        user2=request.user
    )

    # Fetch the last message and time diff for each chat
    chats_with_last_messages = []
    for chat in chats:
        last_message = chat.messages.order_by("-timestamp").first()
        time_diff = last_message.get_time_diff() if last_message else "No messages yet"
        other_user = chat.user1 if chat.user2 == request.user else chat.user2
        chats_with_last_messages.append((other_user, last_message, time_diff))

    context = {"chats_with_last_messages": chats_with_last_messages}
    return render(request, "rt_chat/chat_list.html", context)


@login_required
def create_chat(request):
    if request.method == "POST":
        form = PrivateChatForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            other_user = get_object_or_404(User, username=username)

            if other_user == request.user:
                return redirect("rt_chat:chat_list")

            # Fetch or create the chat
            chat, _ = (
                PrivateChat.objects.get_or_create(user1=request.user, user2=other_user)
                if request.user.id < other_user.id
                else PrivateChat.objects.get_or_create(
                    user1=other_user, user2=request.user
                )
            )

            return HttpResponseRedirect(
                reverse(
                    "rt_chat:chat", args=[request.user.username, other_user.username]
                )
            )

    else:
        form = PrivateChatForm()

    context = {"form": form}
    return render(request, "rt_chat/create_chat.html", context)


@login_required
def chat(request, username, other_username):
    user1 = get_object_or_404(User, username=username)
    user2 = get_object_or_404(User, username=other_username)

    if user1 == user2:
        return redirect("rt_chat:chat_list")

    if request.user == user1:
        # Fetch or create the chat
        chat, _ = (
            PrivateChat.objects.get_or_create(user1=user1, user2=user2)
            if user1.id < user2.id
            else PrivateChat.objects.get_or_create(user1=user2, user2=user1)
        )
    else:
        return redirect("rt_chat:chat_list")

    messages = Message.objects.filter(chat=chat).order_by("timestamp")

    context = {
        "messages": messages,
        "other_user": user2,
    }
    return render(request, "rt_chat/chat.html", context)
