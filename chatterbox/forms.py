from django import forms


class PrivateChatForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Enter username to chat"}), max_length=100,
    )
