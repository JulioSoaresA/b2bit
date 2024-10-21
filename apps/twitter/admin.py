from django.contrib import admin
from .models import Post, Like, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at',)
    search_fields = ('title', 'content',)
    list_filter = ('created_at', 'updated_at',)
    ordering = ('created_at',)
    list_per_page = 20


class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at',)
    search_fields = ('user', 'post',)
    list_filter = ('created_at',)
    ordering = ('created_at',)
    list_per_page = 20


class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at',)
    search_fields = ('follower', 'followed',)
    list_filter = ('created_at',)
    ordering = ('created_at',)
    list_per_page = 20


admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Follow, FollowAdmin)
