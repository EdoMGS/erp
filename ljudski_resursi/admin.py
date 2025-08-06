# ljudski_resursi/admin.py

from django.contrib import admin

from .forms import (DepartmentForm, EmployeeForm, ExpertiseLevelForm,
                    HierarchicalLevelForm, PositionForm)
from .models import (Department, Employee, ExpertiseLevel, HierarchicalLevel,
                     Nagrada, Position, RadnaEvaluacija)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    form = DepartmentForm
    list_display = ("name", "parent", "description")
    search_fields = ("name",)
    list_filter = ("parent",)


@admin.register(ExpertiseLevel)
class ExpertiseLevelAdmin(admin.ModelAdmin):
    form = ExpertiseLevelForm
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(HierarchicalLevel)
class HierarchicalLevelAdmin(admin.ModelAdmin):
    form = HierarchicalLevelForm
    list_display = ("name", "level", "description")
    search_fields = ("name",)
    list_filter = ("level",)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    form = PositionForm
    list_display = (
        "title",
        "department",
        "hierarchical_level",
        "is_managerial",
        "expertise_level",
    )
    search_fields = ("title",)
    list_filter = (
        "department",
        "hierarchical_level",
        "is_managerial",
        "expertise_level",
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeForm
    list_display = (
        "first_name",
        "last_name",
        "email",
        "department",
        "position",
        "expertise_level",
        "is_active",
        "access_level",
    )
    search_fields = ("first_name", "last_name", "email")
    list_filter = (
        "department",
        "position",
        "is_active",
        "expertise_level",
        "access_level",
    )


admin.site.register(RadnaEvaluacija)
admin.site.register(Nagrada)
