from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserChangeForm
from django.contrib.auth.models import User


def register(request):
    """
    Register a new user.
    """
    if request.method == "POST":
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = UserCreationForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)


@login_required
def account(request):
    if request.method == "POST":
        form = CustomUserChangeForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(
                request, request.user
            )  # Important for keeping the user logged in
            return redirect("rt_chat:chat_list")
    else:
        form = CustomUserChangeForm(instance=request.user)

    context = {"form": form}
    return render(request, "users/account.html", context)


@login_required
def delete_account(request):
    user = User.objects.get(id=request.user.id)
    user.delete()
    return redirect("users:register")
