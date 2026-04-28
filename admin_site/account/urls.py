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
    # Two-factor for admin-site
    path(
        "site/<slug>/admin-two-factor/<username>/setup/",
        account_views.AdminTwoFactorSetup.as_view(),
        name="admin_otp_setup",
    ),
    path(
        "site/<slug>/admin-two-factor/<username>/setup-complete/",
        account_views.AdminTwoFactorSetupComplete.as_view(),
        name="admin_otp_setup_complete",
    ),
    path(
        "site/<slug>/admin-two-factor/<username>/disable/",
        account_views.AdminTwoFactorDisable.as_view(),
        name="admin_otp_disable",
    ),
    path(
        "site/<slug>/admin-two-factor/<username>/backup-tokens/",
        account_views.AdminTwoFactorBackupTokens.as_view(),
        name="admin_otp_backup",
    ),
    # Users
    path("site/<slug>/users/", account_views.UserRedirect.as_view(), name="users"),
    path(
        "users/", account_views.UserRedirectSite.as_view(), name="users_redirect_site"
    ),
    path("site/<slug>/users/new/", account_views.UserCreate.as_view(), name="new_user"),
    path(
        "site/<slug>/users/link/", account_views.UserLink.as_view(), name="link_users"
    ),
    path(
        "site/<slug>/users/<username>/",
        account_views.UserUpdate.as_view(),
        name="user",
    ),
    path(
        "site/<slug>/users/<username>/delete/",
        account_views.UserDelete.as_view(),
        name="user_delete",
    ),
]
