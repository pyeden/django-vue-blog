from django.urls import path

from .views import (
    AvatarUploadView,
    CsrfView,
    DeleteAccountView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetView,
    ProfileView,
    RegisterView,
)

urlpatterns = [
    path("auth/csrf/", CsrfView.as_view(), name="auth-csrf"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/password-reset/", PasswordResetView.as_view(), name="auth-password-reset"),
    path("auth/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),
    path("auth/delete/", DeleteAccountView.as_view(), name="auth-delete"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/avatar/", AvatarUploadView.as_view(), name="profile-avatar"),
]
