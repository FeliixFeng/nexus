from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['text', 'date_label', 'sort_order', 'is_visible']
    list_filter = ['is_visible']
    list_editable = ['sort_order', 'is_visible']
