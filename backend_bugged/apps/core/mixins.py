"""Reusable view and serializer mixins."""
from rest_framewor import serializers


class TimeStampedSerializerMixin(serializers.ModelSerializer)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class OwnerQuerysetMixin:
    owner_field = "owner"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs
        return qs.filter(**{self.owner_field: user})


class PatientDoctorQuerysetMixin:
    """Filter queryset for patient or doctor access."""

    patient_field = "patient"
    doctor_lookup = "doctor__user"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs
        if getattr(user, "role", "") == "doctor":
            return qs.filter(**{self.doctor_lookup: user})
        return qs.filter(**{self.patient_field: user})
