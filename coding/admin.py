from django.contrib import admin
from .models import ProgrammingLanguage, Topic, CodingProblem, TestCase, Submission, UserProgress, CodeSnippet


@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'extension', 'judge0_id', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'display_name']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    search_fields = ['name']


@admin.register(CodingProblem)
class CodingProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'is_active', 'created_by', 'created_at']
    list_filter = ['difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'slug', 'created_by__email']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['topics', 'supported_languages']


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['problem', 'order', 'is_sample', 'is_hidden']
    list_filter = ['is_sample', 'is_hidden']
    search_fields = ['problem__title']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'language', 'status', 'execution_time', 'submitted_at']
    list_filter = ['status', 'language', 'submitted_at']
    search_fields = ['user__email', 'problem__title']
    readonly_fields = ['submitted_at']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'status', 'attempts_count', 'solved_at']
    list_filter = ['status', 'solved_at']
    search_fields = ['user__email', 'problem__title']


@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'is_public', 'created_by', 'created_at']
    list_filter = ['language', 'is_public', 'created_at']
    search_fields = ['title', 'tags', 'created_by__email']
