import django_filters

from .models import Clinic, ClinicLocation, ClinicStaffMember, StaffInvitation


class ClinicFilter(django_filters.FilterSet):
    class Meta:
        model = Clinic
        fields = ["status"]


class ClinicLocationFilter(django_filters.FilterSet):
    class Meta:
        model = ClinicLocation
        fields = ["city", "clinic"]


class ClinicStaffMemberFilter(django_filters.FilterSet):
    class Meta:
        model = ClinicStaffMember
        fields = ["status", "clinic"]


class StaffInvitationFilter(django_filters.FilterSet):
    class Meta:
        model = StaffInvitation
        fields = ["status", "clinic"]
