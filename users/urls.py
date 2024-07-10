from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path('accounts/signup/', views.register_view, name="register" ),
    path('accounts/logins/', views.login_view, name='login'),
    # path('accounts/google/login/', views.google_login_view, name='google-login'),
    # path('accounts/google/login/', TemplateView.as_view(template_name='users/google-login.html'), name='google-login'),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name="password_reset"),
    # path('reset_password/', auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html'), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    # path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    # path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name="password_reset_complete"),
    path("accounts/", include("allauth.urls")),
]

