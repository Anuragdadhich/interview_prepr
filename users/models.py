from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    github_username = models.CharField(max_length=100, blank=True)
    linkedin_profile = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s profile"


class UserAnalytics(models.Model):
    """Comprehensive user performance analytics"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics')
    total_interviews = models.PositiveIntegerField(default=0)
    completed_interviews = models.PositiveIntegerField(default=0)
    average_interview_score = models.FloatField(default=0)
    total_coding_problems = models.PositiveIntegerField(default=0)
    solved_coding_problems = models.PositiveIntegerField(default=0)
    coding_success_rate = models.FloatField(default=0)  # percentage
    total_chat_sessions = models.PositiveIntegerField(default=0)
    total_chat_messages = models.PositiveIntegerField(default=0)
    average_session_duration = models.DurationField(null=True, blank=True)
    favorite_difficulty = models.CharField(max_length=20, blank=True)
    favorite_topic = models.CharField(max_length=100, blank=True)
    improvement_areas = models.JSONField(default=list)  # List of areas needing improvement
    strengths = models.JSONField(default=list)  # List of user strengths
    weekly_goal_completion = models.FloatField(default=0)  # percentage
    streak_days = models.PositiveIntegerField(default=0)  # consecutive days active
    last_activity_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s analytics"

    def update_interview_stats(self):
        """Update interview-related statistics"""
        from interviews.models import Interview
        interviews = Interview.objects.filter(user=self.user)
        self.total_interviews = interviews.count()
        completed = interviews.filter(status='completed')
        self.completed_interviews = completed.count()
        if completed.exists():
            self.average_interview_score = completed.aggregate(
                models.Avg('score')
            )['score__avg'] or 0
        self.save()

    def update_coding_stats(self):
        """Update coding-related statistics"""
        from coding.models import UserProgress
        progress = UserProgress.objects.filter(user=self.user)
        self.total_coding_problems = progress.count()
        solved = progress.filter(status='solved')
        self.solved_coding_problems = solved.count()
        if progress.exists():
            self.coding_success_rate = (self.solved_coding_problems / self.total_coding_problems) * 100
        self.save()

    def update_chat_stats(self):
        """Update chat-related statistics"""
        from chat.models import ChatSession, ChatMessage
        sessions = ChatSession.objects.filter(user=self.user)
        self.total_chat_sessions = sessions.count()
        messages = ChatMessage.objects.filter(session__user=self.user)
        self.total_chat_messages = messages.count()
        self.save()


class InterviewPerformance(models.Model):
    """Detailed interview performance tracking"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_performance')
    interview = models.OneToOneField('interviews.Interview', on_delete=models.CASCADE)
    technical_score = models.FloatField(default=0)  # 0-10
    communication_score = models.FloatField(default=0)  # 0-10
    problem_solving_score = models.FloatField(default=0)  # 0-10
    behavioral_score = models.FloatField(default=0)  # 0-10
    response_times = models.JSONField(default=list)  # List of response times per question
    question_types_distribution = models.JSONField(default=dict)  # Distribution of question types
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    ai_feedback_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Interview {self.interview.id} Performance"


class CodingPerformance(models.Model):
    """Detailed coding performance tracking"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coding_performance')
    problem = models.ForeignKey('coding.CodingProblem', on_delete=models.CASCADE)
    best_time = models.FloatField(null=True, blank=True)  # seconds
    best_memory = models.PositiveIntegerField(null=True, blank=True)  # KB
    attempts_to_solve = models.PositiveIntegerField(default=0)
    time_to_first_attempt = models.FloatField(null=True, blank=True)  # seconds from problem load
    hints_used = models.PositiveIntegerField(default=0)
    solution_quality_score = models.FloatField(default=0)  # 0-10 based on AI evaluation
    code_efficiency_score = models.FloatField(default=0)  # 0-10
    readability_score = models.FloatField(default=0)  # 0-10
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.problem.title} Performance"
