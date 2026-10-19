import django_filters
from .models import Appointment, AppointmentReminder, WaitingListEntry


class AppointmentFilter(django_filters.FilterSet):
    status = django_filters.CharFilter()
    scheduled_after = django_filters.DateTimeFilter(field_name="scheduled_start", lookup_expr="gte")
    scheduled_before = django_filters.DateTimeFilter(field_name="scheduled_start", lookup_expr="lte")
    doctor = django_filters.NumberFilter(field_name="doctor_id")

    class Meta:
        model = Appointment
        fields = ["status", "appointment_type", "consultation_type"]


class AppointmentReminderFilter(django_filters.FilterSet):
    class Meta:
        model = AppointmentReminder
        fields = ["is_sent", "channel"]


class WaitingListEntryFilter(django_filters.FilterSet):
    class Meta:
        model = WaitingListEntry
        fields = ["status"]
