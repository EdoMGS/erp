from django.contrib import admin
from import_export.admin import ExportMixin

from .models import Asset, AssetUsage, FixedCost, VariableCostPreset


@admin.register(Asset)
class AssetAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("name", "purchase_date", "value")


@admin.register(AssetUsage)
class AssetUsageAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("asset", "usage_date", "usage_hours")


@admin.register(FixedCost)
class FixedCostAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("name", "amount")


@admin.register(VariableCostPreset)
class VariableCostPresetAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("name", "rate")
