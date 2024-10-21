from django.contrib import admin
from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at',)
    search_fields = ('title', 'content',)
    list_filter = ('created_at', 'updated_at',)
    ordering = ('created_at',)
    list_per_page = 20


admin.site.register(Post, PostAdmin)
