from django.contrib import admin

from .models import FondRadnici, JobCost


class FondRadniciInline(admin.TabularInline):
    model = FondRadnici
    extra = 1


@admin.register(JobCost)
class JobCostAdmin(admin.ModelAdmin):
    inlines = [FondRadniciInline]
    list_display = ("name", "cost_50", "owner_20", "workers_30", "total_cost")
