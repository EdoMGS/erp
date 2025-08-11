from django.contrib import admin

from .models import CityPostalCode, ClientActivityLog, ClientProfile, ClientSupplier


@admin.register(ClientActivityLog)
class ClientActivityLogAdmin(admin.ModelAdmin):
    list_display = ("client", "activity", "timestamp", "activity_type")
    list_filter = ("activity_type", "client", "timestamp")
    search_fields = ("client__name", "activity")
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)


@admin.register(ClientSupplier)
class ClientSupplierAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "oib",
        "get_loyalty_level",
        "relationship_status",
        "is_active",
    )
    list_filter = (
        "relationship_status",
        "is_active",
        "is_supplier",
        "long_term_relationship",
    )
    search_fields = ("name", "email", "oib", "phone")
    ordering = ("name",)

    def get_loyalty_level(self, obj):
        return obj.profile.loyalty_level if obj.profile else None

    get_loyalty_level.short_description = "Razina lojalnosti"
    get_loyalty_level.admin_order_field = "clientprofile__loyalty_level"


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("client", "loyalty_level")
    list_filter = ("loyalty_level",)
    search_fields = ("client__name",)


@admin.register(CityPostalCode)
class CityPostalCodeAdmin(admin.ModelAdmin):
    list_display = ("postal_code", "city", "county", "district")
    list_filter = ("county",)
    search_fields = ("postal_code", "city", "county")
    ordering = ("postal_code",)
