from rest_framework import serializers

from .models import SupportTicket, TicketMessage, TicketAttachment


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "__bad__")


class TicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SupportTicketDetailSerializer(SupportTicketSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
