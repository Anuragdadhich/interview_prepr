from django.contrib import admin
from .models import Interview, InterviewQuestion, InterviewSession, InterviewTemplate, InterviewTemplateQuestion


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'status', 'difficulty', 'score', 'created_at', 'completed_at']
    list_filter = ['status', 'difficulty', 'created_at']
    search_fields = ['user__email', 'title', 'company', 'position']
    readonly_fields = ['created_at', 'started_at', 'completed_at']


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ['interview', 'question_type', 'order', 'score', 'answered_at']
    list_filter = ['question_type', 'answered_at']
    search_fields = ['interview__title', 'question_text']
    readonly_fields = ['created_at', 'answered_at']


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['interview', 'session_id', 'is_active', 'start_time', 'last_activity']
    list_filter = ['is_active', 'start_time']
    search_fields = ['interview__title', 'session_id']
    readonly_fields = ['start_time', 'last_activity']


@admin.register(InterviewTemplate)
class InterviewTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'company', 'is_public', 'created_by', 'created_at']
    list_filter = ['difficulty', 'is_public', 'created_at']
    search_fields = ['name', 'company', 'position', 'created_by__email']


@admin.register(InterviewTemplateQuestion)
class InterviewTemplateQuestionAdmin(admin.ModelAdmin):
    list_display = ['template', 'question_type', 'order']
    list_filter = ['question_type']
    search_fields = ['template__name', 'question_text']
