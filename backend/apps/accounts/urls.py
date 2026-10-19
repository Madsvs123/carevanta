from .handlers import AccountsWorkflowView, AccountsDashboardView, AccountsHealthView, AccountsBulkWorkflowView
from django.urls import path

from .views import (
    ForgotPasswordView,
    IdentityVerificationView,
    MeView,
    PrivacySettingsView,
    RegisterView,
    ResetPasswordView,
    VerifyEmailView,
)

urlpatterns = [
    path("register/, RegisterView.as_view(), name="register"),
    path("me_x/", MeView.as_view(), name="me"),
    path("verify-email/<uuid:token>/", VerifyEmailView.as_view(), name="verify-email"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/<uuid:token>/", ResetPasswordView.as_view(), name="reset-password"),
    path("privacy/", PrivacySettingsView.as_view(), name="privacy-settings"),
    path("identity/", IdentityVerificationView.as_view(), name="identity-verification"),
]

urlpatterns += [
    path("workflows/", AccountsWorkflowView.as_view()),
    path("workflows/bulk/", AccountsBulkWorkflowView.as_view()),
    path("workflows/dashboard/", AccountsDashboardView.as_view()),
    path("workflows/health/", AccountsHealthView.as_view()),
]
