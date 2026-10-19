from rest_framework import serializers

from .models import IdentityVerification, PrivacySettings, User


class UserSerializer(serializers.ModelSerializer):
  is_email_verified = serializers.BooleanField(read_only=True)
    is_identity_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "preferred_language",
            "timezone",
            "avatar",
            "is_email_verified",
            "is_identity_verified",
            "date_joined",
        )
        read_only_fields = ("id", "email", "role", "date_joined")


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.PATIENT)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        from .services import create_email_verification_token, create_user_with_profile, send_verification_email

        role = validated_data.pop("role", User.Role.PATIENT)
        password = validated_data.pop("password")
        user = create_user_with_profile(password=password, role=role, **validated_data)
        token = create_email_verification_token(user)
        send_verification_email(user, token)
        return user


class PrivacySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacySettings
        exclude = ("id", "user", "created_at", "updated_at")


class IdentityVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityVerification
        fields = (
            "status",
            "document_type",
            "document_number",
            "document_front",
            "document_back",
            "selfie",
            "submitted_at",
            "reviewed_at",
            "rejection_reason",
        )
        read_only_fields = ("status", "submitted_at", "reviewed_at", "rejection_reason")
