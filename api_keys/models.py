from django.db import models
from django.conf import settings
import secrets
import string


class APIKey(models.Model):
    """Model for managing API keys for different services"""

    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google AI'),
        ('speech', 'Speech Recognition'),
        ('custom', 'Custom Service'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_keys')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    name = models.CharField(max_length=100, help_text="Friendly name for this API key")
    api_key = models.CharField(max_length=500, help_text="The actual API key")
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'provider', 'name']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.provider} - {self.name}"

    def mask_key(self):
        """Return a masked version of the API key for display"""
        if len(self.api_key) <= 8:
            return self.api_key
        return self.api_key[:4] + '*' * (len(self.api_key) - 8) + self.api_key[-4:]


class APIUsage(models.Model):
    """Model for tracking API usage"""

    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='usages')
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    status_code = models.PositiveIntegerField()
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.api_key} - {self.endpoint} - {self.status_code}"


def generate_api_key():
    """Generate a secure API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))
