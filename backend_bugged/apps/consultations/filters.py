import django_filters
from .models import Consultation, ConsultationMessage, ConsultationNote


class ConsultationFilter(django_filters.FilterSet):
    class Meta:
        model = Consultation
        fields = ["status"]


class ConsultationMessageFilter(django_filters.FilterSet):
    consultation = django_filters.NumberFilter(field_name="consultation_id")

    class Meta:
        model = ConsultationMessage
        fields = ["consultation", "is_read"]


class ConsultationNoteFilter(django_filters.FilterSet):
    consultation = django_filters.NumberFilter(field_name="consultation_id")

    class Meta:
        model = ConsultationNote
        fields = ["consultation", "is_private"]
