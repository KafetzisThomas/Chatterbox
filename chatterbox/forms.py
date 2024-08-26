from django import forms


class PrivateChatForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter username to chat"}
        ),
    )
