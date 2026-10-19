from rest_framework import serializers

from .models import AvailabilitySlot, BlockedPeriod, DoctorSchedule, ScheduleBreak, WorkingHours


class WorkingHoursSerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source="get_weekday_display", read_only=True)

    class Meta:
        model = WorkingHours
        fields = ("id", "schedule", "weekday", "weekday_display", "start_time", "end_time", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ScheduleBreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleBreak
        fields = ("id", "working_hours", "start_time", "end_time", "label", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = (
            "id", "doctor", "name", "is_active", "timezone",
            "default_duration_minutes", "buffer_minutes", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class DoctorScheduleDetailSerializer(DoctorScheduleSerializer):
    working_hours = WorkingHoursSerializer(many=True, read_only=True)

    class Meta(DoctorScheduleSerializer.Meta):
        fields = DoctorScheduleSerializer.Meta.fields + ("working_hours",)


class BlockedPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedPeriod
        fields = (
            "id", "doctor", "start_datetime", "end_datetime",
            "reason", "created_by", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    is_bookable = serializers.SerializerMethodField()

    class Meta:
        model = AvailabilitySlot
        fields = (
            "id", "doctor", "start_datetime", "end_datetime",
            "duration_minutes", "status", "consultation_type",
            "is_bookable", "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def get_is_bookable(self, obj):
        return obj.is_available()
