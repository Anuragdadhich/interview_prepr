from rest_framework import serializers
from .models import Profile, UserAnalytics


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id', 'bio', 'avatar', 'location', 'website',
            'github_username', 'linkedin_profile', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnalytics
        fields = [
            'id', 'total_interviews', 'completed_interviews', 'average_interview_score',
            'total_coding_problems', 'solved_coding_problems', 'coding_success_rate',
            'total_chat_sessions', 'total_chat_messages', 'average_session_duration',
            'favorite_difficulty', 'favorite_topic', 'improvement_areas', 'strengths',
            'weekly_goal_completion', 'streak_days', 'last_activity_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']