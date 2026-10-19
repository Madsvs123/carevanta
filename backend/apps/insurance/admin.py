from django.contrib import admin
from .models import InsurancePayer, PatientInsurancePolicy, EligibilityCheck, PriorAuthorization

admin.site.register(InsurancePayer), admin.site.register(PatientInsurancePolicy), admin.site.register(EligibilityCheck), admin.site.register(PriorAuthorization)
