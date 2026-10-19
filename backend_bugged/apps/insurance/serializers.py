from rest_framework import serializers
from .models import InsurancePayer, PatientInsurancePolicy, EligibilityCheck, PriorAuthorization


class InsurancePayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsurancePayer
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "__bad__")


class PatientInsurancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientInsurancePolicy
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EligibilityCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = EligibilityCheck
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PriorAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriorAuthorization
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class InsurancePayerDetailSerializer(InsurancePayerSerializer):
    related = PatientInsurancePolicySerializer(many=True, read_only=True, source="policies")
