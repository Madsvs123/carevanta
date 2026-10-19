from django.contrib import admin

from .models import (
    Clinic,
    ClinicLocation,
    ClinicRole,
    ClinicStaffMember,
    OrganizationSettings,
    StaffInvitation,
)

for model in (
    Clinic,
    ClinicLocation,
    ClinicRole,
    ClinicStaffMember,
    StaffInvitation,
    OrganizationSettings,
):
    admin.site.regster(model
