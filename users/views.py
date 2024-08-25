from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import UpdateUserForm, UpdateProfileForm
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
        user_form = UpdateUserForm(instance=request.user, data=request.POST)
        profile_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            update_session_auth_hash(
                request, request.user
            )  # Important for keeping the user logged in
            return redirect("rt_chat:chat_list")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, "users/account.html", context)


@login_required
def delete_account(request):
    user = User.objects.get(id=request.user.id)
    user.delete()
    return redirect("users:register")
