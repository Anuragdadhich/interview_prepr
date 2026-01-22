import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import CodingProblem, Submission, ProgrammingLanguage
import requests
from django.conf import settings
from django.utils import timezone


class CodingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time coding environment"""

    async def connect(self):
        self.problem_id = self.scope['url_route']['kwargs']['problem_id']
        self.user = self.scope['user']
        self.room_group_name = f'coding_{self.problem_id}_{self.user.id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial problem data
        problem_data = await self.get_problem_data()
        await self.send(text_data=json.dumps({
            'type': 'problem_loaded',
            'problem': problem_data
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming code execution requests"""
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'run_code':
            await self.run_code(data)
        elif action == 'submit_code':
            await self.submit_code(data)
        elif action == 'save_code':
            await self.save_code(data)

    async def run_code(self, data):
        """Execute code with test cases"""
        code = data.get('code', '')
        language_id = data.get('language_id')
        test_cases = data.get('test_cases', [])

        results = []

        for test_case in test_cases[:3]:  # Limit to 3 test cases for real-time execution
            result = await self.execute_code(code, language_id, test_case)
            results.append(result)

        await self.send(text_data=json.dumps({
            'type': 'execution_result',
            'results': results
        }))

    async def submit_code(self, data):
        """Submit code for full evaluation"""
        code = data.get('code', '')
        language_id = data.get('language_id')

        # Create submission
        submission = await self.create_submission(code, language_id)

        # Run all test cases
        results = await self.run_full_test_suite(submission)

        # Update submission status
        await self.update_submission_status(submission, results)

        await self.send(text_data=json.dumps({
            'type': 'submission_result',
            'submission_id': submission.id,
            'status': submission.status,
            'results': results
        }))

    async def save_code(self, data):
        """Save code snippet for later use"""
        code = data.get('code', '')
        language_id = data.get('language_id')
        title = data.get('title', 'Untitled')

        # Save as code snippet
        snippet = await self.save_code_snippet(code, language_id, title)

        await self.send(text_data=json.dumps({
            'type': 'code_saved',
            'snippet_id': snippet.id,
            'message': 'Code saved successfully'
        }))

    @database_sync_to_async
    def get_problem_data(self):
        """Get problem details"""
        try:
            problem = CodingProblem.objects.get(id=self.problem_id, is_active=True)
            return {
                'id': problem.id,
                'title': problem.title,
                'description': problem.description,
                'difficulty': problem.difficulty,
                'time_limit': problem.time_limit,
                'memory_limit': problem.memory_limit,
                'supported_languages': [
                    {'id': lang.id, 'name': lang.display_name}
                    for lang in problem.supported_languages.all()
                ],
                'sample_test_cases': [
                    {
                        'input': tc.input_data,
                        'expected_output': tc.expected_output
                    }
                    for tc in problem.test_cases.filter(is_sample=True)
                ]
            }
        except CodingProblem.DoesNotExist:
            return None

    @database_sync_to_async
    def execute_code(self, code, language_id, test_case):
        """Execute code against a single test case"""
        try:
            judge0_url = getattr(settings, 'JUDGE0_API_URL', 'https://api.judge0.com')
            judge0_key = getattr(settings, 'JUDGE0_API_KEY', '')

            headers = {'Content-Type': 'application/json'}
            if judge0_key:
                headers['X-RapidAPI-Key'] = judge0_key

            data = {
                "source_code": code,
                "language_id": language_id,
                "stdin": test_case.get('input', ''),
                "expected_output": test_case.get('expected_output', ''),
                "cpu_time_limit": 2,  # seconds for real-time execution
                "memory_limit": 128   # MB
            }

            response = requests.post(
                f"{judge0_url}/submissions",
                json=data,
                headers=headers,
                params={'base64_encoded': 'false', 'wait': 'true'}
            )

            if response.status_code == 201:
                result = response.json()
                return {
                    'input': test_case.get('input', ''),
                    'expected_output': test_case.get('expected_output', ''),
                    'actual_output': result.get('stdout', ''),
                    'status': 'accepted' if result.get('status', {}).get('id') == 3 else 'wrong_answer',
                    'execution_time': float(result.get('time', 0)),
                    'memory_used': int(result.get('memory', 0)),
                    'error': result.get('stderr', '')
                }

            return {
                'status': 'error',
                'error': 'Execution failed'
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    @database_sync_to_async
    def create_submission(self, code, language_id):
        """Create a new submission"""
        problem = CodingProblem.objects.get(id=self.problem_id)
        language = ProgrammingLanguage.objects.get(id=language_id)

        return Submission.objects.create(
            user=self.user,
            problem=problem,
            language=language,
            code=code,
            status='running'
        )

    @database_sync_to_async
    def run_full_test_suite(self, submission):
        """Run all test cases for submission"""
        test_cases = submission.problem.test_cases.filter(is_hidden=False)
        results = []

        for test_case in test_cases:
            result = self.execute_code_sync(
                submission.code,
                submission.language.judge0_id,
                test_case
            )
            results.append({
                'test_case_id': test_case.id,
                'input': test_case.input_data,
                'expected_output': test_case.expected_output,
                'actual_output': result.get('actual_output', ''),
                'status': result.get('status', 'error'),
                'execution_time': result.get('execution_time', 0),
                'memory_used': result.get('memory_used', 0)
            })

        return results

    def execute_code_sync(self, code, language_id, test_case):
        """Synchronous code execution for full test suite"""
        try:
            judge0_url = getattr(settings, 'JUDGE0_API_URL', 'https://api.judge0.com')
            judge0_key = getattr(settings, 'JUDGE0_API_KEY', '')

            headers = {'Content-Type': 'application/json'}
            if judge0_key:
                headers['X-RapidAPI-Key'] = judge0_key

            data = {
                "source_code": code,
                "language_id": language_id,
                "stdin": test_case.input_data,
                "expected_output": test_case.expected_output,
                "cpu_time_limit": test_case.problem.time_limit / 1000,
                "memory_limit": test_case.problem.memory_limit
            }

            response = requests.post(
                f"{judge0_url}/submissions",
                json=data,
                headers=headers,
                params={'base64_encoded': 'false', 'wait': 'true'}
            )

            if response.status_code == 201:
                result = response.json()
                return {
                    'actual_output': result.get('stdout', ''),
                    'status': 'accepted' if result.get('status', {}).get('id') == 3 else 'wrong_answer',
                    'execution_time': float(result.get('time', 0)),
                    'memory_used': int(result.get('memory', 0))
                }

            return {'status': 'error'}

        except Exception as e:
            return {'status': 'error'}

    @database_sync_to_async
    def update_submission_status(self, submission, results):
        """Update submission status based on results"""
        all_passed = all(r['status'] == 'accepted' for r in results)
        submission.status = 'accepted' if all_passed else 'wrong_answer'
        submission.save()

        # Update user progress
        from .models import UserProgress
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

    @database_sync_to_async
    def save_code_snippet(self, code, language_id, title):
        """Save code as a snippet"""
        from .models import CodeSnippet
        language = ProgrammingLanguage.objects.get(id=language_id)

        return CodeSnippet.objects.create(
            user=self.user,
            title=title,
            code=code,
            language=language,
            is_public=False
        )