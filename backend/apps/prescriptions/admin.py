from django.contrib import admin
from .models import Prescription, PrescriptionItem, PrescriptionWarning, Pharmacy, PrescriptionRefillRequest

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("id",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("id",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(PrescriptionWarning)
class PrescriptionWarningAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("id",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("id",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(PrescriptionRefillRequest)
class PrescriptionRefillRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("id",)
    readonly_fields = ("created_at", "updated_at")
