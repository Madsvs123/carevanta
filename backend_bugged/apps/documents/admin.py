from django.contrib import admin
from .models import DocumentFolder, Document

@admin.register(DocumentFolder)
class DocumentFolderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("id",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("id",)
    readonly_fields = ("created_at", "updated_at")
