"""
FitMitra Social Admin
Django admin configuration for social models
"""

from django.contrib import admin
from .models import (
    UserProfile, Post, Like, Comment, Follow,
    Message, Notification, Report, Block
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'user', 'followers_count', 'following_count', 'posts_count', 'created_at']
    search_fields = ['username', 'user__username', 'user__email']
    list_filter = ['is_private', 'created_at']
    readonly_fields = ['followers_count', 'following_count', 'posts_count', 'created_at', 'updated_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post_type', 'caption_preview', 'likes_count', 'comments_count', 'created_at', 'is_active']
    search_fields = ['author__username', 'caption']
    list_filter = ['post_type', 'is_active', 'created_at']
    readonly_fields = ['likes_count', 'comments_count', 'shares_count', 'created_at', 'updated_at']
    
    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'created_at']
    search_fields = ['user__username', 'post__caption']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'text_preview', 'parent', 'likes_count', 'created_at', 'is_active']
    search_fields = ['author__username', 'text', 'post__caption']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['likes_count', 'created_at', 'updated_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'follower', 'following', 'status', 'created_at']
    search_fields = ['follower__username', 'following__username']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'recipient', 'text_preview', 'is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'text']
    list_filter = ['is_read', 'created_at']
    readonly_fields = ['created_at', 'read_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'actor', 'notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'actor__username']
    list_filter = ['notification_type', 'is_read', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'report_type', 'post', 'reported_user', 'status', 'created_at']
    search_fields = ['reporter__username', 'reported_user__username', 'description']
    list_filter = ['report_type', 'status', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['id', 'blocker', 'blocked', 'created_at']
    search_fields = ['blocker__username', 'blocked__username']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
