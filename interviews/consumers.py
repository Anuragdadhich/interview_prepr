import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Interview, InterviewSession, InterviewQuestion
from core.ai_providers import ai_manager
from django.conf import settings


class InterviewConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time interview sessions"""

    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'interview_{self.session_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': 'Connected to interview session. The AI interviewer will begin shortly.'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming messages from user"""
        data = json.loads(text_data)
        message_type = data.get('type', 'user_message')

        if message_type == 'user_answer':
            await self.handle_user_answer(data)
        elif message_type == 'start_interview':
            await self.start_ai_interview()
        elif message_type == 'request_feedback':
            await self.generate_feedback(data)

    async def handle_user_answer(self, data):
        """Process user's answer to a question"""
        question_id = data.get('question_id')
        answer = data.get('answer', '')

        # Save answer to database
        await self.save_user_answer(question_id, answer)

        # Generate AI feedback
        feedback = await self.generate_ai_feedback(question_id, answer)

        # Send feedback to user
        await self.send(text_data=json.dumps({
            'type': 'ai_feedback',
            'question_id': question_id,
            'feedback': feedback
        }))

        # Generate next question or end interview
        next_question = await self.get_next_question()
        if next_question:
            await self.send(text_data=json.dumps({
                'type': 'next_question',
                'question': next_question
            }))
        else:
            await self.end_interview()

    async def start_ai_interview(self):
        """Start the AI-powered interview"""
        session = await self.get_session()
        if session:
            # Generate first question
            question = await self.generate_ai_question(session.interview)
            if question:
                await self.send(text_data=json.dumps({
                    'type': 'interview_started',
                    'question': question
                }))

    async def generate_feedback(self, data):
        """Generate feedback for user's performance"""
        session = await self.get_session()
        if session:
            analytics = await self.calculate_performance_analytics(session.interview)
            await self.send(text_data=json.dumps({
                'type': 'performance_analytics',
                'analytics': analytics
            }))

    @database_sync_to_async
    def save_user_answer(self, question_id, answer):
        """Save user's answer to database"""
        try:
            question = InterviewQuestion.objects.get(id=question_id)
            question.user_answer = answer
            question.save()
        except InterviewQuestion.DoesNotExist:
            pass

    @database_sync_to_async
    def generate_ai_feedback(self, question_id, answer):
        """Generate AI feedback for user's answer"""
        try:
            question = InterviewQuestion.objects.get(id=question_id)

            prompt = f"""
            As an expert interviewer, evaluate this answer to the question: "{question.question_text}"

            User's answer: "{answer}"

            Expected answer: "{question.expected_answer}"

            Provide constructive feedback including:
            1. Strengths of the answer
            2. Areas for improvement
            3. A score from 1-10
            4. Suggestions for better answers

            Keep it concise but helpful.
            """

            # Use AI provider manager with fallback
            feedback = ai_manager.generate_content(prompt, max_tokens=800, temperature=0.7)
            return feedback

        except Exception as e:
            return f"Error generating feedback: {str(e)}"

    @database_sync_to_async
    def get_next_question(self):
        """Get the next question for the interview"""
        session = InterviewSession.objects.filter(session_id=self.session_id).first()
        if session:
            interview = session.interview
            # Simple logic: get unanswered questions
            unanswered = interview.questions.filter(user_answer__isnull=True).first()
            if unanswered:
                return {
                    'id': unanswered.id,
                    'text': unanswered.question_text,
                    'type': unanswered.question_type
                }
        return None

    @database_sync_to_async
    def generate_ai_question(self, interview):
        """Generate a new AI question based on user preferences and performance"""
        from users.models import UserAnalytics

        # Get user analytics for personalization
        analytics = UserAnalytics.objects.filter(user=interview.user).first()

        # Build prompt with user preferences
        user_context = ""
        if analytics:
            user_context = f"""
            User Performance Data:
            - Favorite difficulty: {analytics.favorite_difficulty or 'intermediate'}
            - Favorite topic: {analytics.favorite_topic or 'general programming'}
            - Average interview score: {analytics.average_interview_score or 'N/A'}
            - Coding success rate: {analytics.coding_success_rate or 0}%
            - Strengths: {', '.join(analytics.strengths) if analytics.strengths else 'None identified'}
            - Areas for improvement: {', '.join(analytics.improvement_areas) if analytics.improvement_areas else 'None identified'}
            """

        prompt = f"""
        Generate a personalized {interview.difficulty} level interview question for a {interview.position or 'software engineering'} position.

        {user_context}

        Previous questions in this interview: {[q.question_text for q in interview.questions.all()]}

        Based on the user's performance data and preferences, create a question that:
        1. Matches their skill level and favorite topics
        2. Addresses their improvement areas if possible
        3. Builds on their strengths
        4. Is different from previous questions

        Return a JSON object with:
        - "text": the question text (be specific and technical)
        - "type": question type (technical/behavioral/system_design/coding/algorithm)
        - "expected_answer": brief expected answer structure
        - "difficulty": the question difficulty level
        - "topic": the main topic/category
        """

        try:
            # Use AI provider manager with fallback
            response_text = ai_manager.generate_content(prompt, max_tokens=1000, temperature=0.8)

            # Try to parse the response as JSON
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            try:
                question_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                question_data = {
                    'text': 'Can you explain how you would design a scalable web application architecture?',
                    'type': 'system_design',
                    'expected_answer': 'Discuss load balancing, database design, caching, microservices, etc.',
                    'difficulty': interview.difficulty,
                    'topic': 'System Design'
                }

            # Create question in database
            question = InterviewQuestion.objects.create(
                interview=interview,
                question_text=question_data.get('text', 'Default question'),
                question_type=question_data.get('type', 'technical'),
                expected_answer=question_data.get('expected_answer', 'Expected answer not provided'),
                order=interview.questions.count() + 1
            )

            return {
                'id': question.id,
                'text': question.question_text,
                'type': question.question_type,
                'difficulty': question_data.get('difficulty', interview.difficulty),
                'topic': question_data.get('topic', 'General')
            }

        except Exception as e:
            # Ultimate fallback
            question = InterviewQuestion.objects.create(
                interview=interview,
                question_text='Tell me about a challenging technical problem you solved and how you approached it.',
                question_type='technical',
                expected_answer='Describe the problem, your approach, solution, and lessons learned.',
                order=interview.questions.count() + 1
            )

            return {
                'id': question.id,
                'text': question.question_text,
                'type': question.question_type,
                'difficulty': interview.difficulty,
                'topic': 'Problem Solving'
            }
                'type': question.question_type
            }

        except Exception as e:
            return None

    @database_sync_to_async
    def get_session(self):
        """Get the interview session"""
        return InterviewSession.objects.filter(session_id=self.session_id).first()

    @database_sync_to_async
    def end_interview(self):
        """End the interview and calculate final score"""
        session = InterviewSession.objects.filter(session_id=self.session_id).first()
        if session:
            interview = session.interview
            # Calculate score based on answers
            questions = interview.questions.all()
            total_score = 0
            answered_count = 0

            for question in questions:
                if question.user_answer:
                    answered_count += 1
                    # Simple scoring - could be improved with AI evaluation
                    total_score += 7  # Default score

            final_score = total_score / answered_count if answered_count > 0 else 0
            interview.complete_interview(score=final_score)

            await self.send(text_data=json.dumps({
                'type': 'interview_ended',
                'final_score': final_score,
                'total_questions': questions.count(),
                'answered_questions': answered_count
            }))

    @database_sync_to_async
    def calculate_performance_analytics(self, interview):
        """Calculate performance analytics"""
        questions = interview.questions.all()
        total_questions = questions.count()
        answered_questions = questions.filter(user_answer__isnull=False).count()

        # Calculate average score (simplified)
        avg_score = 7.5  # Placeholder

        return {
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'average_score': avg_score,
            'completion_rate': (answered_questions / total_questions) * 100 if total_questions > 0 else 0,
            'strengths': ['Good communication', 'Technical knowledge'],
            'areas_for_improvement': ['Practice more system design', 'Improve problem-solving speed']
        }