from rest_framework import serializers

from .models import Conversation, Message, MessageAttachment


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
