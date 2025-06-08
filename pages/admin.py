from django.contrib import admin
from django.utils.html import format_html
from .models import Page

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_at', 'updated_at', 'page_link')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'slug', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'page_link')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'is_active')
        }),
    )
    
    def page_link(self, obj):
        if obj.pk:
            return format_html('<a href="{}" target="_blank">View on site</a>', obj.get_absolute_url())
        return "-"
    page_link.short_description = 'Link'
