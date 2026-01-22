from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatTemplate, ChatAnalytics


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'session_type', 'is_active', 'created_at', 'updated_at']
    list_filter = ['session_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'title']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'is_user', 'created_at', 'tokens_used']
    list_filter = ['is_user', 'created_at']
    search_fields = ['session__title', 'content']
    readonly_fields = ['created_at']


@admin.register(ChatTemplate)
class ChatTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_by', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by__email']


@admin.register(ChatAnalytics)
class ChatAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'total_messages', 'total_tokens', 'satisfaction_rating', 'created_at']
    list_filter = ['satisfaction_rating', 'created_at']
    search_fields = ['user__email', 'session__title']
