from django.contrib import admin

from .models import AuditTrail, BaseModel, Notification, Role

# @admin.register(BaseModel)
# class BaseModelAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'created_at', 'updated_at', 'is_active']
#     search_fields = ['name']
#     list_filter = ['is_active']
#     ordering = ['id']

# Remove the incorrect registration
# admin.site.register(ActiveManager)
