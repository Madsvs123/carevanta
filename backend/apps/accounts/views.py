from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailVerificationToken, PasswordResetToken, PrivacySettings
from .serializers import (
    IdentityVerificationSerializer,
    PrivacySettingsSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .services import create_password_reset_token, send_password_reset_email

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, token):
        try:
            record = EmailVerificationToken.objects.select_related("user").get(token=token)
            record.consume()
            return Response({"detail": "Email verified successfully."})
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get("email", "").lower()
        user = User.objects.filter(email=email).first()
        if user:
            token = create_password_reset_token(user)
            send_password_reset_email(user, token)
        return Response({"detail": "If the email exists, a reset link was sent."})


class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, token):
        password = request.data.get("password")
        if not password or len(password) < 8:
            return Response({"detail": "Password must be at least 8 characters."}, status=400)
        try:
            record = PasswordResetToken.objects.select_related("user").get(token=token)
            record.consume()
            record.user.set_password(password)
            record.user.save()
            return Response({"detail": "Password reset successfully."})
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=400)


class PrivacySettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = PrivacySettingsSerializer

    def get_object(self):
        settings_obj, _ = PrivacySettings.objects.get_or_create(user=self.request.user)
        return settings_obj


class IdentityVerificationView(generics.RetrieveUpdateAPIView):
    serializer_class = IdentityVerificationSerializer

    def get_object(self):
        from .models import IdentityVerification

        obj, _ = IdentityVerification.objects.get_or_create(user=self.request.user)
        return obj
