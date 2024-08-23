from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ChatGroup, Message
from .forms import ChatGroupForm


@login_required
def chat(request, group_name=None):
    if group_name:
        # Fetch the specific chat group
        # Return a 404 error if not found
        group = get_object_or_404(ChatGroup, name=group_name)
    else:
        # Create a global chat group if it doesn't exist
        # Add the current user as a member
        group, created = ChatGroup.objects.get_or_create(name="global_chat")
        if created:
            group.members.add(request.user)

    # Fetch messages associated with the chat group, ordered by timestamp
    messages = Message.objects.filter(group=group).order_by("timestamp")

    # Fetch all groups
    groups = ChatGroup.objects.all()

    # Create a list of tuples (group, last_message, time_diff)
    groups_with_last_messages = []
    for grp in groups:
        last_message = grp.messages.order_by("-timestamp").first()
        time_diff = last_message.get_time_diff() if last_message else "No messages yet"
        groups_with_last_messages.append((grp, last_message, time_diff))

    context = {
        "group": group,
        "messages": messages,
        "groups_with_last_messages": groups_with_last_messages,
    }
    return render(request, "rt_chat/chat.html", context)


@login_required
def create_group(request):
    if request.method == "POST":
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group_name = form.cleaned_data["group_name"]
            user2_username = form.cleaned_data["user2"]
            user2 = get_object_or_404(User, username=user2_username)

            # Create or get the chat group
            group, _ = ChatGroup.objects.get_or_create(name=group_name)
            group.members.add(request.user, user2)

            return redirect("rt_chat:chat", group_name=group_name)
    else:
        form = ChatGroupForm()

    context = {"form": form}
    return render(request, "rt_chat/create_group.html", context)


def test(request):
    return render(request, "rt_chat/test.html")
