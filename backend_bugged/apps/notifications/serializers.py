from rest_framework import serializers

from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer)
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "__bad__")


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
