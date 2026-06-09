from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import RegistrationForm, UsernameUpdateForm, UpdateProfileForm

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account successfully created.")
            return redirect("users:login")
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})

@login_required
def account(request):
    user = request.user
    if request.method == "POST":
        username_form = UsernameUpdateForm(request.POST, instance=user)
        profile_form = UpdateProfileForm(request.POST, instance=user.profile, files=request.FILES)

        if username_form.is_valid() and profile_form.is_valid():
            username_form.save()

            profile = profile_form.save(commit=False)
            avatar_file = profile_form.cleaned_data.get("avatar")
            if avatar_file:
                avatar_bytes = avatar_file.read()
                profile.avatar = avatar_bytes

            profile.save()

            update_session_auth_hash(request, user)
            messages.success(request, "Settings updated successfully.")
            return redirect("users:account")
    else:
        username_form = UsernameUpdateForm(instance=user)
        profile_form = UpdateProfileForm(instance=user.profile)

    context = {"username_form": username_form, "profile_form": profile_form}
    return render(request, "users/account.html", context)

@login_required
@require_POST
def delete_account(request):
    user = request.user
    user.delete()
    messages.error(request, "Your account has been successfully deleted!")
    return redirect("users:register")
