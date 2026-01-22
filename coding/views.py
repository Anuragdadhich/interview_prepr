from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils import timezone
from .models import (
    ProgrammingLanguage, Topic, CodingProblem,
    TestCase, Submission, UserProgress, CodeSnippet
)
from .serializers import (
    ProgrammingLanguageSerializer, TopicSerializer,
    CodingProblemSerializer, TestCaseSerializer,
    SubmissionSerializer, UserProgressSerializer,
    CodeSnippetSerializer
)
import requests
import json
from django.conf import settings


class ProgrammingLanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProgrammingLanguage.objects.filter(is_active=True)
    serializer_class = ProgrammingLanguageSerializer


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class CodingProblemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CodingProblem.objects.filter(is_active=True)
    serializer_class = CodingProblemSerializer

    @action(detail=True, methods=['get'])
    def test_cases(self, request, pk=None):
        """Get sample test cases for a problem"""
        problem = self.get_object()
        test_cases = problem.test_cases.filter(is_sample=True)
        serializer = TestCaseSerializer(test_cases, many=True)
        return Response(serializer.data)


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute code submission"""
        submission = self.get_object()

        # Get test cases
        test_cases = submission.problem.test_cases.filter(is_hidden=False)

        results = []
        for test_case in test_cases:
            result = self._execute_code(
                submission.code,
                submission.language.judge0_id,
                test_case.input_data,
                submission.problem.time_limit,
                submission.problem.memory_limit
            )
            results.append({
                'test_case_id': test_case.id,
                'input': test_case.input_data,
                'expected_output': test_case.expected_output,
                'actual_output': result.get('output', ''),
                'status': result.get('status', 'error'),
                'execution_time': result.get('time', 0),
                'memory_used': result.get('memory', 0)
            })

        # Update submission status
        all_passed = all(r['status'] == 'accepted' for r in results)
        submission.status = 'accepted' if all_passed else 'wrong_answer'
        submission.save()

        # Update user progress
        progress, created = UserProgress.objects.get_or_create(
            user=submission.user,
            problem=submission.problem,
            defaults={'status': 'attempted'}
        )

        progress.attempts_count += 1
        if all_passed and progress.status != 'solved':
            progress.status = 'solved'
            progress.solved_at = timezone.now()
            progress.best_submission = submission

        progress.save()

        return Response({
            'submission_id': submission.id,
            'status': submission.status,
            'results': results
        })

    def _execute_code(self, code, language_id, input_data, time_limit, memory_limit):
        """Execute code using Judge0 API"""
        try:
            judge0_url = getattr(settings, 'JUDGE0_API_URL', 'https://api.judge0.com')
            judge0_key = getattr(settings, 'JUDGE0_API_KEY', '')

            headers = {'Content-Type': 'application/json'}
            if judge0_key:
                headers['X-RapidAPI-Key'] = judge0_key

            data = {
                "source_code": code,
                "language_id": language_id,
                "stdin": input_data,
                "expected_output": "",
                "cpu_time_limit": time_limit / 1000,  # Convert to seconds
                "memory_limit": memory_limit
            }

            # Submit code for execution
            response = requests.post(
                f"{judge0_url}/submissions",
                json=data,
                headers=headers,
                params={'base64_encoded': 'false', 'wait': 'true'}
            )

            if response.status_code == 201:
                result = response.json()
                token = result.get('token')

                # Get execution result
                result_response = requests.get(
                    f"{judge0_url}/submissions/{token}",
                    headers=headers
                )

                if result_response.status_code == 200:
                    execution_result = result_response.json()

                    return {
                        'output': execution_result.get('stdout', ''),
                        'status': 'accepted' if execution_result.get('status', {}).get('id') == 3 else 'error',
                        'time': float(execution_result.get('time', 0)),
                        'memory': int(execution_result.get('memory', 0))
                    }

            return {
                'output': 'Execution failed',
                'status': 'error',
                'time': 0,
                'memory': 0
            }

        except Exception as e:
            return {
                'output': str(e),
                'status': 'error',
                'time': 0,
                'memory': 0
            }


class UserProgressViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)


class CodeSnippetViewSet(viewsets.ModelViewSet):
    queryset = CodeSnippet.objects.all()
    serializer_class = CodeSnippetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CodeSnippet.objects.filter(
            models.Q(is_public=True) | models.Q(user=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@login_required
def solve_problem(request, slug):
    """View for solving a specific coding problem"""
    problem = get_object_or_404(CodingProblem, slug=slug, is_active=True)

    # Get available programming languages
    languages = ProgrammingLanguage.objects.filter(is_active=True)

    # Get sample test cases
    sample_test_cases = problem.test_cases.filter(is_sample=True)

    # Get user's progress on this problem
    progress = UserProgress.objects.filter(user=request.user, problem=problem).first()

    # Get user's recent submissions for this problem
    recent_submissions = Submission.objects.filter(
        user=request.user,
        problem=problem
    ).order_by('-submitted_at')[:5]

    context = {
        'problem': problem,
        'languages': languages,
        'sample_test_cases': sample_test_cases,
        'progress': progress,
        'recent_submissions': recent_submissions,
    }

    return render(request, 'coding/solve_problem.html', context)
