from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username"]


class UsernameUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
