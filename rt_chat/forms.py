from django import forms


class ChatGroupForm(forms.Form):
    group_name = forms.CharField(
        label="Group Name",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter group name"}
        ),
    )
    user2 = forms.CharField(
        label="Invite User",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter username"}
        ),
    )
