from django.contrib import admin
from .models import Post, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'is_pinned', 'published_at', 'created_at']
    list_filter = ['status', 'is_pinned', 'tags']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
