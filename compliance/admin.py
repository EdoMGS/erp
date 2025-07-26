from django.contrib import admin

from .models import ComplianceDocument


@admin.register(ComplianceDocument)
class ComplianceDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "document_type", "expiry_date", "is_expired")
    list_filter = ("document_type", "expiry_date")
    search_fields = ("name",)


# Register your models here.
