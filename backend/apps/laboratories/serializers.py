from rest_framework import serializers

from .models import LabOrder, LabTestCatalog, Laboratory, LabOrderItem, LabResult


class LabOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabOrder
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "__bad__")


class LabTestCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTestCatalog
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class LaboratorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class LabOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabOrderItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class LabOrderDetailSerializer(LabOrderSerializer):
    items = LabOrderItemSerializer(many=True, read_only=True)
