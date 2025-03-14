from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path("accounts/logout/", views.CustomLogoutView.as_view(), name="account_logout"),
    path(
        "accounts/profile/", views.login_redirect, name="login-redirect"
    ),  # Dito una papasok si user, then redirect natin
    path("accounts/", include("allauth.urls")),
    # path("accounts/signup/", views.register_view, name="account_signup"),
    # path("logout/", views.logout_view, name="logout"),
    # path("reset_password/", views.ResetPasswordView.as_view(), name="password_reset"),
    # path(
    #     "reset_password_sent/",
    #     auth_views.PasswordResetDoneView.as_view(),
    #     name="password_reset_done",
    # ),
    # path(
    #     "reset/<uidb64>/<token>/",
    #     views.PasswordResetConfirmView.as_view(),
    #     name="password_reset_confirm",
    # ),
    # path(
    #     "reset_password_complete/",
    #     auth_views.PasswordResetCompleteView.as_view(),
    #     name="password_reset_complete",
    # ),
    path("login/", views.normal_login_view, name="normal-login"),
    path("user_profile/", views.user_profile, name="user_profile"),
]
