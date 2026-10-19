import django_filters

from .models import DoctorProfile, MedicalSpecialty, PatientProfile


class MedicalSpecialtyFilter(django_filters.FilterSet):
    slug = django_filters.CharFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = MedicalSpecialty
        fields = ("slug", "is_active")


class DoctorProfileFilter(django_filters.FilterSet):
    consultation_type = django_filters.CharFilter()
    clinic = django_filters.NumberFilter(field_name="clinic_id")
    specialty = django_filters.CharFilter(field_name="specialties__slug")
    min_rating = django_filters.NumberFilter(field_name="rating_average", lookup_expr="gte")
    max_fee = django_filters.NumberFilter(field_name="consultation_fee", lookup_expr="lte")
    language = django_filters.CharFilter(method="filter_language")
    is_featured = django_filters.BooleanFilter()
    is_accepting_patients = django_filters.BooleanFilter()

    class Meta:
        model = DoctorProfile
        fields = ("consultation_type", "clinic", "is_featured", "is_accepting_patients")

    def filter_language(self, queryset, name, value):
        return queryset.filter(languages__contains=[value])


class PatientProfileFilter(django_filters.FilterSet):
    country = django_filters.CharFilter()
    gender = django_filters.CharFilter()

    class Meta:
        model = PatientProfile
        fields = ("country", "gender")
