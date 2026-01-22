from rest_framework import serializers
from .models import Interview, InterviewQuestion, InterviewSession, InterviewTemplate, InterviewTemplateQuestion


class InterviewQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = [
            'id', 'question_text', 'question_type', 'expected_answer',
            'user_answer', 'ai_feedback', 'score', 'order',
            'time_taken_seconds', 'created_at', 'answered_at'
        ]
        read_only_fields = ['id', 'created_at', 'answered_at']


class InterviewSerializer(serializers.ModelSerializer):
    questions = InterviewQuestionSerializer(many=True, read_only=True)
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            'id', 'title', 'description', 'status', 'difficulty',
            'company', 'position', 'duration_minutes', 'ai_provider',
            'score', 'feedback', 'created_at', 'started_at',
            'completed_at', 'questions', 'questions_count'
        ]
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at']

    def get_questions_count(self, obj):
        return obj.questions.count()


class InterviewSessionSerializer(serializers.ModelSerializer):
    interview_title = serializers.CharField(source='interview.title', read_only=True)

    class Meta:
        model = InterviewSession
        fields = [
            'id', 'interview', 'interview_title', 'session_id',
            'is_active', 'current_question', 'start_time', 'last_activity'
        ]
        read_only_fields = ['id', 'session_id', 'start_time', 'last_activity']


class InterviewTemplateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewTemplateQuestion
        fields = [
            'id', 'question_text', 'question_type', 'expected_answer', 'order'
        ]


class InterviewTemplateSerializer(serializers.ModelSerializer):
    questions = InterviewTemplateQuestionSerializer(many=True, read_only=True)
    questions_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)

    class Meta:
        model = InterviewTemplate
        fields = [
            'id', 'name', 'description', 'difficulty', 'company',
            'position', 'estimated_duration', 'is_public',
            'created_by', 'created_by_name', 'created_at',
            'questions', 'questions_count'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_name']

    def get_questions_count(self, obj):
        return obj.questions.count()