from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Page, Notification


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "is_active",
        "created_at",
        "updated_at",
        "page_link",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "slug", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "page_link")
    fieldsets = ((None, {"fields": ("title", "slug", "content", "is_active")}),)

    def page_link(self, obj):
        if obj.pk:
            return format_html(
                '<a href="{}" target="_blank">View on site</a>', obj.get_absolute_url()
            )
        return "-"

    page_link.short_description = "Link"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "message_preview",
        "message_type",
        "is_active",
        "start_date",
        "end_date",
    )
    list_filter = ("is_active", "message_type", "start_date")
    search_fields = ("title", "message")
    date_hierarchy = "start_date"
    ordering = ("-start_date",)
    fieldsets = (
        (None, {"fields": ("title", "message", "message_type", "is_active")}),
        (
            "Scheduling",
            {
                "fields": ("start_date", "end_date"),
                "classes": ("collapse", "wide"),
                "description": "Set the active period for this notification.",
            },
        ),
    )

    def message_preview(self, obj):
        return obj.message[:100] + "..." if len(obj.message) > 100 else obj.message

    message_preview.short_description = "Message Preview"

    def get_queryset(self, request):
        # Show all notifications in the admin
        return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        # Set the updated_at timestamp when saving
        obj.updated_at = timezone.now()
        super().save_model(request, obj, form, change)
