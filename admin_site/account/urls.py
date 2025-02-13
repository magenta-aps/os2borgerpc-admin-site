from django.urls import path
from account import views as account_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path(
        "accounts/login/",
        account_views.LoginView.as_view(template_name="two_factor/core/login.html"),
    ),
    path(
        "accounts/sso-login-error/",
        account_views.LoginView.as_view(template_name="two_factor/core/login.html"),
        name="sso-login-error",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(template_name="logout.html"),
        name="logout",
    ),
]
