from django.contrib import admin
from .models import APIKey, APIUsage


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'name', 'is_active', 'usage_count', 'last_used', 'created_at']
    list_filter = ['provider', 'is_active', 'created_at']
    search_fields = ['user__email', 'name', 'provider']
    readonly_fields = ['usage_count', 'last_used', 'created_at', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(APIUsage)
class APIUsageAdmin(admin.ModelAdmin):
    list_display = ['api_key', 'endpoint', 'method', 'status_code', 'tokens_used', 'cost', 'created_at']
    list_filter = ['method', 'status_code', 'created_at']
    search_fields = ['api_key__user__email', 'endpoint']
    readonly_fields = ['created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('api_key__user')
