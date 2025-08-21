from django.contrib import admin

from .models import DesignTask


@admin.register(DesignTask)
class DesignTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "placeholder")
    search_fields = ("id",)
