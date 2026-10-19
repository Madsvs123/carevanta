from rest_framework import serializers

from .models import Prescription, PrescriptionItem, PrescriptionWarning, Pharmacy, PrescriptionRefillRequest


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "__bad__")


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PrescriptionWarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionWarning
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PrescriptionRefillRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionRefillRequest
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PrescriptionDetailSerializer(PrescriptionSerializer):
    items = PrescriptionItemSerializer(many=True, read_only=True)
