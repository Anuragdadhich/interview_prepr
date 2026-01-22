from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
import openai
import anthropic
import google.genai as genai
from django.conf import settings
from django.utils import timezone


class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to the chat session"""
        session = self.get_object()
        content = request.data.get('content', '').strip()

        if not content:
            return Response({'error': 'Message content is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user message
        user_message = ChatMessage.objects.create(
            session=session,
            content=content,
            is_user=True
        )

        # Generate AI response
        ai_response = self._generate_ai_response(session, content)

        # Create AI message
        ai_message = ChatMessage.objects.create(
            session=session,
            content=ai_response['content'],
            is_user=False,
            tokens_used=ai_response.get('tokens_used'),
            response_time=ai_response.get('response_time', 0)
        )

        # Update session
        session.updated_at = timezone.now()
        if not session.title:
            session.generate_title()
        session.save()

        return Response({
            'user_message': ChatMessageSerializer(user_message).data,
            'ai_message': ChatMessageSerializer(ai_message).data
        })

    def _generate_ai_response(self, session, user_message):
        """Generate AI response based on session type and provider"""
        try:
            if session.ai_provider == 'openai':
                return self._generate_openai_response(user_message, session.session_type)
            elif session.ai_provider == 'anthropic':
                return self._generate_anthropic_response(user_message, session.session_type)
            elif session.ai_provider == 'google':
                return self._generate_gemini_response(user_message, session.session_type)
            else:
                return {
                    'content': 'I apologize, but the selected AI provider is not available.',
                    'tokens_used': 0,
                    'response_time': 0
                }
        except Exception as e:
            return {
                'content': f'I apologize, but I encountered an error: {str(e)}',
                'tokens_used': 0,
                'response_time': 0
            }

    def _generate_openai_response(self, message, session_type):
        """Generate response using OpenAI"""
        import time
        start_time = time.time()

        system_prompt = self._get_system_prompt(session_type)

        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            response_time = time.time() - start_time

            return {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'response_time': response_time
            }
        except Exception as e:
            return {
                'content': f'OpenAI API error: {str(e)}',
                'tokens_used': 0,
                'response_time': time.time() - start_time
            }

    def _generate_anthropic_response(self, message, session_type):
        """Generate response using Anthropic"""
        import time
        start_time = time.time()

        system_prompt = self._get_system_prompt(session_type)

        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": message}]
            )

            response_time = time.time() - start_time

            return {
                'content': response.content[0].text,
                'tokens_used': len(response.content[0].text.split()),  # Approximate
                'response_time': response_time
            }
        except Exception as e:
            return {
                'content': f'Anthropic API error: {str(e)}',
                'tokens_used': 0,
                'response_time': time.time() - start_time
            }

    def _generate_gemini_response(self, message, session_type):
        """Generate response using Google Gemini"""
        import time
        start_time = time.time()

        system_prompt = self._get_system_prompt(session_type)

        try:
            import google.genai as genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"{system_prompt}\n\nUser: {message}"
            )

            response_time = time.time() - start_time

            return {
                'content': response.text,
                'tokens_used': len(response.text.split()),  # Approximate token count
                'response_time': response_time
            }
        except Exception as e:
            return {
                'content': f'Gemini API error: {str(e)}',
                'tokens_used': 0,
                'response_time': time.time() - start_time
            }

    def _get_system_prompt(self, session_type):
        """Get system prompt based on session type"""
        prompts = {
            'general': 'You are a helpful AI assistant. Provide clear, accurate, and engaging responses.',
            'interview_prep': 'You are an expert interview coach. Help the user prepare for technical interviews by providing detailed explanations, asking follow-up questions, and giving constructive feedback.',
            'code_review': 'You are an experienced software engineer conducting code review. Provide constructive feedback on code quality, best practices, potential bugs, and improvement suggestions.',
            'problem_solving': 'You are a programming mentor. Help users solve coding problems by guiding them through the thought process, explaining algorithms, and providing hints rather than direct solutions.',
            'career_advice': 'You are a career counselor specializing in software development. Provide practical advice on career growth, skill development, job searching, and industry trends.'
        }
        return prompts.get(session_type, prompts['general'])


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(session__user=self.request.user)
