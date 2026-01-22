from django.db import models
from django.conf import settings


class SpeechSession(models.Model):
    """Speech-to-text sessions"""

    SESSION_TYPE_CHOICES = [
        ('interview', 'Interview Response'),
        ('chat', 'Chat Message'),
        ('practice', 'Practice Session'),
        ('feedback', 'Voice Feedback'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='speech_sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    audio_file = models.FileField(upload_to='speech_audio/', blank=True, null=True)
    transcribed_text = models.TextField(blank=True)
    confidence_score = models.FloatField(null=True, blank=True)  # 0-1 scale
    duration_seconds = models.FloatField(null=True, blank=True)
    language = models.CharField(max_length=10, default='en-US')
    provider = models.CharField(max_length=20, default='google')  # google, azure, aws, etc.
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.session_type} - {self.created_at}"


class VoiceProfile(models.Model):
    """User voice profiles for better recognition"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_profile')
    voice_samples = models.JSONField(default=list, help_text="List of voice sample file paths")
    accent = models.CharField(max_length=50, blank=True)
    speaking_rate = models.FloatField(null=True, blank=True)  # words per minute
    pitch_range = models.CharField(max_length=50, blank=True)
    common_phrases = models.JSONField(default=list)
    is_calibrated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s voice profile"


class SpeechAnalytics(models.Model):
    """Analytics for speech processing"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='speech_analytics')
    total_sessions = models.PositiveIntegerField(default=0)
    total_duration = models.FloatField(default=0)  # seconds
    average_confidence = models.FloatField(null=True, blank=True)
    most_used_language = models.CharField(max_length=10, blank=True)
    error_rate = models.FloatField(default=0)  # percentage
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Speech Analytics"


class TextToSpeech(models.Model):
    """Text-to-speech generations"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tts_generations')
    text = models.TextField()
    audio_file = models.FileField(upload_to='tts_audio/', blank=True, null=True)
    voice = models.CharField(max_length=50, default='en-US-Standard-C')
    speed = models.FloatField(default=1.0)
    pitch = models.FloatField(default=0.0)
    provider = models.CharField(max_length=20, default='google')
    is_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"TTS: {self.text[:50]}..."
