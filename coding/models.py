from django.db import models
from django.conf import settings


class ProgrammingLanguage(models.Model):
    """Supported programming languages"""

    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    extension = models.CharField(max_length=10)
    judge0_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class Topic(models.Model):
    """Coding problem topics/categories"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtopics')

    def __str__(self):
        return self.name


class CodingProblem(models.Model):
    """Coding problems/challenges"""

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    input_description = models.TextField(blank=True)
    output_description = models.TextField(blank=True)
    examples = models.JSONField(default=list)  # List of input/output examples
    constraints = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    topics = models.ManyToManyField(Topic, related_name='problems')
    supported_languages = models.ManyToManyField(ProgrammingLanguage, related_name='problems')
    time_limit = models.PositiveIntegerField(default=1000)  # milliseconds
    memory_limit = models.PositiveIntegerField(default=256)  # MB
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def accepted_submissions_count(self):
        """Get the count of accepted submissions for this problem"""
        return self.submissions.filter(status='accepted').count()

    @property
    def total_submissions_count(self):
        """Get the total count of submissions for this problem"""
        return self.submissions.count()

    @property
    def acceptance_rate(self):
        """Calculate acceptance rate as percentage"""
        total = self.total_submissions_count
        if total == 0:
            return 0
        accepted = self.accepted_submissions_count
        return round((accepted / total) * 100, 1)


class TestCase(models.Model):
    """Test cases for coding problems"""

    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.problem.title} - Test Case {self.order}"


class Submission(models.Model):
    """User code submissions"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('accepted', 'Accepted'),
        ('wrong_answer', 'Wrong Answer'),
        ('time_limit_exceeded', 'Time Limit Exceeded'),
        ('memory_limit_exceeded', 'Memory Limit Exceeded'),
        ('runtime_error', 'Runtime Error'),
        ('compilation_error', 'Compilation Error'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='submissions')
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.CASCADE)
    code = models.TextField()
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    execution_time = models.FloatField(null=True, blank=True)  # seconds
    memory_used = models.PositiveIntegerField(null=True, blank=True)  # KB
    error_message = models.TextField(blank=True)
    judge0_token = models.CharField(max_length=100, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.email} - {self.problem.title} - {self.status}"


class UserProgress(models.Model):
    """User progress on coding problems"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=[
        ('not_attempted', 'Not Attempted'),
        ('attempted', 'Attempted'),
        ('solved', 'Solved'),
    ], default='not_attempted')
    best_submission = models.ForeignKey(Submission, null=True, blank=True, on_delete=models.SET_NULL)
    attempts_count = models.PositiveIntegerField(default=0)
    solved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'problem']

    def __str__(self):
        return f"{self.user.email} - {self.problem.title} - {self.status}"


class CodeSnippet(models.Model):
    """Reusable code snippets/templates"""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.CASCADE)
    code = models.TextField()
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.language.name} - {self.title}"
