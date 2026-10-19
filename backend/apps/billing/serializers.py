from rest_framework import serializers

from .models import Invoice, Payment, Refund, InsuranceClaim, DoctorPayout, DiscountCode, TransactionHistory


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "__bad__")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class InsuranceClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceClaim
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DoctorPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorPayout
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
