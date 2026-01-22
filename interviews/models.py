from django.db import models
from django.conf import settings
from django.utils import timezone


class Interview(models.Model):
    """Model for AI-powered interviews"""

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interviews')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate')
    company = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    ai_provider = models.CharField(max_length=20, default='openai')
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def start_interview(self):
        """Mark interview as started"""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()

    def complete_interview(self, score=None, feedback=None):
        """Mark interview as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if score is not None:
            self.score = score
        if feedback:
            self.feedback = feedback
        self.save()


class InterviewQuestion(models.Model):
    """Model for individual interview questions"""

    QUESTION_TYPE_CHOICES = [
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
        ('system_design', 'System Design'),
        ('coding', 'Coding'),
        ('algorithm', 'Algorithm'),
    ]

    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    expected_answer = models.TextField(blank=True)
    user_answer = models.TextField(blank=True)
    ai_feedback = models.TextField(blank=True)
    score = models.FloatField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class InterviewSession(models.Model):
    """Model for real-time interview sessions"""

    interview = models.OneToOneField(Interview, on_delete=models.CASCADE, related_name='session')
    session_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    current_question = models.ForeignKey(InterviewQuestion, null=True, blank=True, on_delete=models.SET_NULL)
    start_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.session_id} for {self.interview}"


class InterviewTemplate(models.Model):
    """Model for reusable interview templates"""

    name = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=Interview.DIFFICULTY_CHOICES)
    company = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    estimated_duration = models.PositiveIntegerField(default=60)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class InterviewTemplateQuestion(models.Model):
    """Questions within interview templates"""

    template = models.ForeignKey(InterviewTemplate, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=InterviewQuestion.QUESTION_TYPE_CHOICES)
    expected_answer = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.template.name} - Q{self.order}"
