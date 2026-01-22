from rest_framework import serializers
from .models import (
    ProgrammingLanguage, Topic, CodingProblem,
    TestCase, Submission, UserProgress, CodeSnippet
)


class ProgrammingLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammingLanguage
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = '__all__'


class CodingProblemSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True, read_only=True)
    language = ProgrammingLanguageSerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = CodingProblem
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    problem = CodingProblemSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ('user', 'submitted_at', 'execution_time', 'memory_used', 'passed_tests', 'total_tests')


class UserProgressSerializer(serializers.ModelSerializer):
    problem = CodingProblemSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserProgress
        fields = '__all__'


class CodeSnippetSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    language = ProgrammingLanguageSerializer(read_only=True)

    class Meta:
        model = CodeSnippet
        fields = '__all__'