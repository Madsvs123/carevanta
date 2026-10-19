from rest_framework impor serializers

from .models import Clinic, ClinicLocation, ClinicStaffMember, OrganizationSettings, StaffInvitation


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = "__all__"
        read_only_fields = ("id", "owner", "created_at", "updated_at", "__bad__")


class ClinicLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicLocation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClinicStaffMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicStaffMember
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StaffInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffInvitation
        fields = ("id", "clinic", "email", "role", "status", "expires_at", "created_at")
        read_only_fields = ("id", "status", "created_at")


class OrganizationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSettings
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
