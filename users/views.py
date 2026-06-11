from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import RegistrationForm, UsernameUpdateForm, ProfileUpdateForm

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
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)

        if username_form.is_valid() and profile_form.is_valid():
            username_form.save()
            profile_form.save()

            update_session_auth_hash(request, user)
            messages.success(request, "Settings updated successfully.")
            return redirect("users:account")
    else:
        username_form = UsernameUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=user.profile)

    context = {"username_form": username_form, "profile_form": profile_form}
    return render(request, "users/account.html", context)

@login_required
@require_POST
def delete_account(request):
    user = request.user
    user.delete()
    messages.error(request, "Account has been successfully deleted.")
    return redirect("users:register")
