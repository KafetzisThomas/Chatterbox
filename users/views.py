from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, UpdateUserForm, UpdateProfileForm

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account successfully created! You're now able to login.")
            return redirect("users:login")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})

@login_required
def account(request):
    if request.method == "POST":
        user_form = UpdateUserForm(instance=request.user, data=request.POST)
        profile_form = UpdateProfileForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            avatar_file = profile_form.cleaned_data.get("avatar")
            if avatar_file:
                avatar_bytes = avatar_file.read()
                profile.avatar = avatar_bytes

            profile.save()

            update_session_auth_hash(request, request.user)  # keep user logged in
            messages.success(request, "Your account settings were successfully updated!")
            return redirect("chatterbox:chat_list")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, "users/account.html", context)

@login_required
def delete_account(request):
    user = User.objects.get(id=request.user.id)
    user.delete()
    messages.error(request, "Your account has been successfully deleted!")
    return redirect("users:register")
