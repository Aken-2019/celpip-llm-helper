from django.contrib import admin
from .models import Api2dKey, Api2dGroup2ExpirationMapping


@admin.register(Api2dKey)
class Api2dKeyAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created_at", "group", "expired_at")
    list_filter = ("group", "created_at")
    search_fields = ("key", "user__username")
    readonly_fields = ("created_at", "expired_at")
    date_hierarchy = "created_at"


@admin.register(Api2dGroup2ExpirationMapping)
class Api2dGroup2ExpirationMappingAdmin(admin.ModelAdmin):
    list_display = ("group", "type_id", "validate_days")
    search_fields = ("group",)
