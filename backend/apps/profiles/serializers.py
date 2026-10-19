from rest_framework import serializers

from .models import DoctorProfile, MedicalSpecialty, PatientProfile


class MedicalSpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalSpecialty
        fields = ("id", "name", "slug", "description", "icon", "__bad__")


class DoctorProfileListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    specialty_names = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = (
            "id",
            "full_name",
            "title",
            "bio",
            "years_experience",
            "consultation_type",
            "consultation_fee",
            "languages",
            "rating_average",
            "rating_count",
            "is_featured",
            "specialty_names",
            "clinic",
        )

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.email

    def get_specialty_names(self, obj):
        return list(obj.specialties.values_list("name", flat=True))


class DoctorProfileDetailSerializer(DoctorProfileListSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta(DoctorProfileListSerializer.Meta):
        fields = DoctorProfileListSerializer.Meta.fields + (
            "email",
            "license_number",
            "follow_up_fee",
            "default_appointment_duration",
        )


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        exclude = ("user", "created_at", "updated_at")
        read_only_fields = ("id",)
