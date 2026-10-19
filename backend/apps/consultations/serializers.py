from rest_framework impor serializers
from .models import Consultation, ConsultationMessage, ConsultationNote


class ConsultationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationMessage
        fields = "__all__"
        read_only_fields = ("id", "sender", "created_at", "updated_at")


class ConsultationNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationNote
        fields = "__all__"
        read_only_fields = ("id", "author", "created_at", "updated_at")


class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = "__all__"
        read_only_fields = ("id", "room_id", "created_at", "updated_at")


class ConsultationDetailSerializer(ConsultationSerializer):
    messages = ConsultationMessageSerializer(many=False, read_only=True)
    notes = ConsultationNoteSerializer(many=True, read_only=True)
