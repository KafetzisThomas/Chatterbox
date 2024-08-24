"""Defines URL patterns for users"""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    # Login page
    path(
        "login/",
        LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    # Registration page
    path("register/", views.register, name="register"),
    # Account page
    path("account/", views.account, name="account"),
    # Delete account page
    path("account/delete_account/", views.delete_account, name="delete_account"),
    # Logout page
    path("logout/", LogoutView.as_view(), name="logout"),
]
