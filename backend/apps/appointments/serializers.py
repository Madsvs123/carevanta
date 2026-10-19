from rest_framewor import serializers
from .models import Appointment, AppointmentReminder, WaitingListEntry


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "checked_in_at", "cancelled_at", "__bad__")

    def get_doctor_name(self, obj):
        user = getattr(obj.doctor, "user", None)
        if not user:
            return ""
        return f"{user.first_name} {user.last_name}".strip() or user.email

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}".strip() or obj.patient.email


class AppointmentReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentReminder
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class WaitingListEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingListEntry
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AppointmentDetailSerializer(AppointmentSerializer):
    reminders = AppointmentReminderSerializer(many=True, read_only=True)
