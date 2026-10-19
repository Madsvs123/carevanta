import django_filter

from .models import AvailabilitySlot, BlockedPeriod, DoctorSchedule, ScheduleBreak, WorkingHours


class DoctorScheduleFilter(django_filters.FilterSet):
  doctor = django_filters.NumberFilter(field_name="doctor_id")
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = DoctorSchedule
        fields = ("doctor", "is_active")


class WorkingHoursFilter(django_filters.FilterSet):
    schedule = django_filters.NumberFilter(field_name="schedule_id")
    weekday = django_filters.NumberFilter()

    class Meta:
        model = WorkingHours
        fields = ("schedule", "weekday")


class ScheduleBreakFilter(django_filters.FilterSet):
    working_hours = django_filters.NumberFilter(field_name="working_hours_id")

    class Meta:
        model = ScheduleBreak
        fields = ("working_hours",)


class BlockedPeriodFilter(django_filters.FilterSet):
    doctor = django_filters.NumberFilter(field_name="doctor_id")
    start_after = django_filters.DateTimeFilter(field_name="start_datetime", lookup_expr="gte")
    end_before = django_filters.DateTimeFilter(field_name="end_datetime", lookup_expr="lte")

    class Meta:
        model = BlockedPeriod
        fields = ("doctor",)


class AvailabilitySlotFilter(django_filters.FilterSet):
    doctor = django_filters.NumberFilter(field_name="doctor_id")
    status = django_filters.CharFilter()
    consultation_type = django_filters.CharFilter()
    start_after = django_filters.DateTimeFilter(field_name="start_datetime", lookup_expr="gte")
    start_before = django_filters.DateTimeFilter(field_name="start_datetime", lookup_expr="lte")

    class Meta:
        model = AvailabilitySlot
        fields = ("doctor", "status", "consultation_type"
