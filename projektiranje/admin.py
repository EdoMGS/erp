from django.contrib import admin

from .models import (BillOfMaterials, BOMItem, CADDocument, DesignRevision,
                     DesignSegment, DesignTask, DynamicPlan)


@admin.register(DesignTask)
class DesignTaskAdmin(admin.ModelAdmin):
    list_display = (
        "projekt",
        "projektant",
        "status",
        "datum_pocetka",
        "datum_zavrsetka",
    )
    search_fields = ("projekt__naziv_projekta", "projektant__ime")
    list_filter = ("status", "datum_pocetka", "datum_zavrsetka")
    readonly_fields = ("created_at", "updated_at")


@admin.register(DesignSegment)
class DesignSegmentAdmin(admin.ModelAdmin):
    list_display = ("design_task", "segment_type", "planirani_sati", "utroseni_sati")
    list_filter = ("segment_type",)
    search_fields = ("design_task__projekt__naziv_projekta",)


@admin.register(DynamicPlan)
class DynamicPlanAdmin(admin.ModelAdmin):
    list_display = ("design_task", "pocetak_plana", "kraj_plana")
    search_fields = ("design_task__projekt__naziv_projekta",)


@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(admin.ModelAdmin):
    list_display = ("naziv", "design_task", "status")
    list_filter = ("status",)
    search_fields = ("naziv", "design_task__projekt__naziv_projekta")


@admin.register(BOMItem)
class BOMItemAdmin(admin.ModelAdmin):
    list_display = ("bom", "materijal", "kolicina")
    search_fields = ("bom__naziv", "materijal__naziv")
    list_filter = ("bom",)


@admin.register(CADDocument)
class CADDocumentAdmin(admin.ModelAdmin):
    list_display = ("design_task", "file_type", "uploaded_at")
    list_filter = ("file_type",)
    search_fields = ("design_task__projekt__naziv_projekta",)


@admin.register(DesignRevision)
class DesignRevisionAdmin(admin.ModelAdmin):
    list_display = ("design_task", "broj_revizije", "autor", "created_at")
    list_filter = ("created_at",)
    search_fields = ("design_task__projekt__naziv_projekta", "opis")
