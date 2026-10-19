from rest_framework import serializers

from .models import DocumentFolder, Document


class DocumentFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFolder
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
