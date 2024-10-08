from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email Address", widget=forms.EmailInput, required=True
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email Address", widget=forms.EmailInput, required=True
    )
    password1 = forms.CharField(
        label="New Password", widget=forms.PasswordInput, required=False
    )
    password2 = forms.CharField(
        label="Confirm New Password", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")

        if password1:
            try:
                validate_password(password1)
            except ValidationError as e:
                self.add_error("password1", e)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = []
