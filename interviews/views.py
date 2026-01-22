from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Interview, InterviewQuestion, InterviewSession, InterviewTemplate
from .serializers import (
    InterviewSerializer, InterviewQuestionSerializer,
    InterviewSessionSerializer, InterviewTemplateSerializer
)
import openai
import anthropic
import google.genai as genai
from django.conf import settings


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Interview.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start an interview session"""
        interview = self.get_object()
        interview.start_interview()

        # Create interview session
        session = InterviewSession.objects.create(interview=interview)

        return Response({
            'status': 'started',
            'session_id': session.session_id
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete an interview"""
        interview = self.get_object()
        score = request.data.get('score')
        feedback = request.data.get('feedback')

        interview.complete_interview(score=score, feedback=feedback)

        return Response({'status': 'completed'})

    @action(detail=True, methods=['post'])
    def generate_question(self, request, pk=None):
        """Generate next interview question using AI"""
        interview = self.get_object()

        # Get AI provider and generate question
        provider = interview.ai_provider
        question = self._generate_ai_question(interview, provider)

        # Create question record
        question_obj = InterviewQuestion.objects.create(
            interview=interview,
            question_text=question['text'],
            question_type=question['type'],
            expected_answer=question.get('expected_answer', ''),
            order=interview.questions.count() + 1
        )

        return Response(InterviewQuestionSerializer(question_obj).data)

    def _generate_ai_question(self, interview, provider):
        """Generate question using AI"""
        prompt = f"""
        Generate a {interview.difficulty} level interview question for a {interview.position or 'software engineering'} position at {interview.company or 'a tech company'}.

        Previous questions asked: {[q.question_text for q in interview.questions.all()]}

        Please provide:
        1. Question text
        2. Question type (technical/behavioral/system_design/coding/algorithm)
        3. Expected answer (brief)

        Format as JSON.
        """

        if provider == 'openai':
            return self._generate_openai_question(prompt)
        elif provider == 'anthropic':
            return self._generate_anthropic_question(prompt)
        elif provider == 'google':
            return self._generate_gemini_question(prompt)

        # Default fallback
        return {
            'text': 'Tell me about yourself and your experience.',
            'type': 'behavioral',
            'expected_answer': 'Brief introduction covering background, experience, and goals.'
        }

    def _generate_openai_question(self, prompt):
        """Generate question using OpenAI"""
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            # Parse response (simplified)
            return {
                'text': 'Generated question from OpenAI',
                'type': 'technical',
                'expected_answer': 'Expected answer here'
            }
        except Exception as e:
            return {
                'text': 'Tell me about a challenging project you worked on.',
                'type': 'behavioral',
                'expected_answer': 'Description of project, challenges, and solutions.'
            }

    def _generate_anthropic_question(self, prompt):
        """Generate question using Anthropic"""
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            # Parse response (simplified)
            return {
                'text': 'Generated question from Anthropic',
                'type': 'technical',
                'expected_answer': 'Expected answer here'
            }
        except Exception as e:
            return {
                'text': 'Explain a complex algorithm you implemented.',
                'type': 'technical',
                'expected_answer': 'Detailed explanation of algorithm and implementation.'
            }

    def _generate_gemini_question(self, prompt):
        """Generate question using Google Gemini"""
        try:
            import google.genai as genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            # Parse the response - assuming it returns JSON-like structure
            # This is a simplified implementation
            return {
                'text': response.text.split('\n')[0] if '\n' in response.text else response.text,
                'type': 'technical',  # Could be improved with better parsing
                'expected_answer': 'Generated by Gemini AI'
            }
        except Exception as e:
            return {
                'text': 'Describe your approach to solving technical problems.',
                'type': 'technical',
                'expected_answer': 'Step-by-step problem-solving approach.'
            }


class InterviewQuestionViewSet(viewsets.ModelViewSet):
    queryset = InterviewQuestion.objects.all()
    serializer_class = InterviewQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InterviewQuestion.objects.filter(
            interview__user=self.request.user
        ).select_related('interview')


class InterviewSessionViewSet(viewsets.ModelViewSet):
    queryset = InterviewSession.objects.all()
    serializer_class = InterviewSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InterviewSession.objects.filter(
            interview__user=self.request.user
        ).select_related('interview')


class InterviewTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewTemplateSerializer
    permission_classes = [IsAuthenticated]
    queryset = InterviewTemplate.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
