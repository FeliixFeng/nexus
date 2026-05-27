from django.contrib import admin
from .models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'url', 'sort_order', 'is_visible', 'created_at']
    list_filter = ['category', 'is_visible']
    search_fields = ['name', 'description', 'url']
    list_editable = ['sort_order', 'is_visible']
