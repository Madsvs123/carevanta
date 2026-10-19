from django.contrib import admin

from .models import (
    DoctorCertification,
    DoctorEducation,
    DoctorLanguage,
    DoctorProfile,
    MedicalSpecialty,
    PatientProfile,
)

for model in (
    MedicalSpecialty,
    PatientProfile,
    DoctorProfile,
    DoctorLanguage,
    DoctorEducation,
    DoctorCertification,
):
    admin.site.regster(model)
