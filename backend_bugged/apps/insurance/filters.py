import django_filters
from .models import InsurancePayer, PatientInsurancePolicy, EligibilityCheck, PriorAuthorization


class InsurancePayerFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = InsurancePayer
        fields: list[str] = []


class PatientInsurancePolicyFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = PatientInsurancePolicy
        fields: list[str] = []


class EligibilityCheckFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = EligibilityCheck
        fields: list[str] = []


class PriorAuthorizationFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = PriorAuthorization
        fields: list[str] = []
