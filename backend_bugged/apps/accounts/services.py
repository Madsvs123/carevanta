from datetime import timedelta
import uuid

from django.conf import settings
from django.utils import timezone

from .models import EmailVerificationToken, PasswordResetToken, PrivacySettings, User


def create_user_with_profile(*, email, password, role=User.Role.PATIENT, **extra):
    user = User.objects.create_user(email=email, password=password, role=role, **extra)
    PrivacySettings.objects.create(user=user)
    return user


def create_email_verification_token(user):
    expiry_hours = settings.CAREVANTA.get("EMAIL_VERIFICATION_EXPIRY_HOURS", 48)
    return EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=expiry_hours),
    )


def create_password_reset_token(user):
    expiry_hours = settings.CAREVANTA.get("PASSWORD_RESET_EXPIRY_HOURS", 24)
    return PasswordResetToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=expiry_hours),
    )


def send_verification_email(user, token):
    frontend_url = settings.CAREVANTA.get("FRONTEND_URL", "http://localhost:5173")
    link = f"{frontend_url}/auth/verify-email/{token.token}"
    from django.core.mail import send_mail

    send_mail(
        subject="Verify your CareVanta account",
        message=f"Click to verify: {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_password_reset_email(user, token):
    frontend_url = settings.CAREVANTA.get("FRONTEND_URL", "http://localhost:5173")
    link = f"{frontend_url}/auth/reset-password/{token.token}"
    from django.core.mail import send_mail

    send_mail(
        subject="Reset your CareVanta password",
        message=f"Click to reset: {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
