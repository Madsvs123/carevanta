from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import EmailVerificationToken, IdentityVerification, PasswordResetToken, PrivacySettings, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "role", "is_email_verified", "is_staff", "date_joined")
    list_filter = ("role", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("CareVanta", {"fields": ("role", "phone_number", "email_verified_at", "identity_verified_at", "preferred_language", "timezone")}),
    )


admin.site.register(EmailVerificationToken)
admin.site.register(PasswordResetToken)
admin.site.register(PrivacySettings)
admin.site.register(IdentityVerification)
