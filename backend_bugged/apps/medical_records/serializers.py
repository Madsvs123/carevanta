from rest_framework import serializers
from .models import MedicalRecord, VitalSigns, Allergy, Medication, MedicalHistoryEntry, MedicalAttachment, Referral


class VitalSignsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSigns
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "__bad__")


class MedicalAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalAttachment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class MedicalRecordDetailSerializer(MedicalRecordSerializer):
    vitals = VitalSignsSerializer(many=True, read_only=True)
    attachments = MedicalAttachmentSerializer(many=True, read_only=True)


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class MedicalHistoryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistoryEntry
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
