from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile


class UpdateUserForm(forms.ModelForm):
    password1 = forms.CharField(
        label="New Password", widget=forms.PasswordInput, required=False
    )
    password2 = forms.CharField(
        label="Confirm New Password", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

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
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UpdateAvatarForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = []
