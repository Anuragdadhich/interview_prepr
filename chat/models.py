from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """AI chat sessions"""

    SESSION_TYPE_CHOICES = [
        ('general', 'General Chat'),
        ('interview_prep', 'Interview Preparation'),
        ('code_review', 'Code Review'),
        ('problem_solving', 'Problem Solving'),
        ('career_advice', 'Career Advice'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, blank=True)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='general')
    ai_provider = models.CharField(max_length=20, default='openai')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.email} - {self.title or 'Untitled Chat'}"

    def generate_title(self):
        """Generate a title from the first message"""
        first_message = self.messages.filter(is_user=True).first()
        if first_message:
            # Take first 50 characters of the first user message
            title = first_message.content[:50]
            if len(first_message.content) > 50:
                title += "..."
            self.title = title
            self.save()


class ChatMessage(models.Model):
    """Individual chat messages"""

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)  # seconds
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        sender = "User" if self.is_user else "AI"
        return f"{sender}: {self.content[:50]}..."


class ChatTemplate(models.Model):
    """Predefined chat templates/prompts"""

    name = models.CharField(max_length=200)
    description = models.TextField()
    system_prompt = models.TextField()
    user_prompt_template = models.TextField(help_text="Template for user messages, use {variable} for placeholders")
    variables = models.JSONField(default=dict, help_text="Available variables for the template")
    category = models.CharField(max_length=50, default='general')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class ChatAnalytics(models.Model):
    """Analytics for chat usage"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_analytics')
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='analytics')
    total_messages = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    average_response_time = models.FloatField(null=True, blank=True)
    satisfaction_rating = models.PositiveIntegerField(null=True, blank=True)  # 1-5 scale
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Session Analytics"
