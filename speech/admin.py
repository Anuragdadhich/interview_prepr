from django.contrib import admin
from .models import SpeechSession, VoiceProfile, SpeechAnalytics, TextToSpeech


@admin.register(SpeechSession)
class SpeechSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_type', 'language', 'is_processed', 'confidence_score', 'created_at']
    list_filter = ['session_type', 'language', 'is_processed', 'created_at']
    search_fields = ['user__email', 'transcribed_text']
    readonly_fields = ['created_at', 'processed_at']


@admin.register(VoiceProfile)
class VoiceProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'accent', 'speaking_rate', 'is_calibrated', 'created_at']
    list_filter = ['is_calibrated', 'created_at']
    search_fields = ['user__email', 'accent']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SpeechAnalytics)
class SpeechAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_sessions', 'total_duration', 'average_confidence', 'error_rate', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TextToSpeech)
class TextToSpeechAdmin(admin.ModelAdmin):
    list_display = ['user', 'voice', 'speed', 'is_generated', 'created_at']
    list_filter = ['voice', 'is_generated', 'created_at']
    search_fields = ['user__email', 'text']
