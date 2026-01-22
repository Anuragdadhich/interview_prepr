from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile, CodingPerformance, InterviewPerformance, UserAnalytics
from coding.models import CodingProblem, TestCase, Submission, ProgrammingLanguage, Topic
from interviews.models import Interview, InterviewQuestion
from chat.models import ChatSession, ChatMessage
from faker import Faker
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        fake = Faker()

        # Create programming languages
        self.stdout.write('Creating programming languages...')
        languages_data = [
            {'name': 'python', 'display_name': 'Python', 'extension': 'py', 'judge0_id': 71},
            {'name': 'javascript', 'display_name': 'JavaScript', 'extension': 'js', 'judge0_id': 63},
            {'name': 'java', 'display_name': 'Java', 'extension': 'java', 'judge0_id': 62},
        ]

        languages = []
        for lang_data in languages_data:
            lang, created = ProgrammingLanguage.objects.get_or_create(
                name=lang_data['name'],
                defaults=lang_data
            )
            languages.append(lang)

        # Create topics
        self.stdout.write('Creating topics...')
        topics_data = [
            {'name': 'Arrays', 'description': 'Array manipulation and algorithms'},
            {'name': 'Strings', 'description': 'String processing and algorithms'},
            {'name': 'Dynamic Programming', 'description': 'DP problems and solutions'},
        ]

        topics = []
        for topic_data in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults=topic_data
            )
            topics.append(topic)

        # Create sample users
        self.stdout.write('Creating sample users...')
        users = []
        for i in range(10):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            users.append(user)

            # Create profile
            Profile.objects.create(
                user=user,
                bio=fake.text(max_nb_chars=200),
                location=fake.city(),
                website=fake.url(),
                github_username=fake.user_name(),
                linkedin_profile=fake.url()
            )

        # Create sample problems
        self.stdout.write('Creating sample problems...')
        problems = []
        difficulties = ['easy', 'medium', 'hard']
        for i in range(20):
            problem = CodingProblem.objects.create(
                title=fake.sentence(nb_words=6),
                slug=fake.slug(),
                description=fake.text(max_nb_chars=500),
                difficulty=random.choice(difficulties),
                time_limit=2000,  # 2 seconds
                memory_limit=256,  # 256 MB
                created_by=random.choice(users)
            )
            problems.append(problem)

            # Add topics and languages
            problem.topics.set(random.sample(topics, random.randint(1, 2)))
            problem.supported_languages.set(languages)

            # Create test cases
            for j in range(3):
                TestCase.objects.create(
                    problem=problem,
                    input_data=fake.text(max_nb_chars=100),
                    expected_output=str(random.randint(1, 100)),
                    is_sample=(j < 2),
                    order=j
                )

        # Create sample interviews
        self.stdout.write('Creating sample interviews...')
        interviews = []
        for user in users[:5]:  # First 5 users
            interview = Interview.objects.create(
                user=user,
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=200),
                status='completed',
                difficulty=random.choice(['beginner', 'intermediate', 'advanced']),
                company=fake.company(),
                position=fake.job(),
                duration_minutes=60,
                score=random.randint(60, 100),
                feedback=fake.text(max_nb_chars=300)
            )
            interviews.append(interview)

            # Create questions
            for i in range(5):
                InterviewQuestion.objects.create(
                    interview=interview,
                    question_text=fake.text(max_nb_chars=200),
                    question_type=random.choice(['technical', 'behavioral', 'system_design']),
                    expected_answer=fake.text(max_nb_chars=300),
                    user_answer=fake.text(max_nb_chars=300),
                    ai_feedback=fake.text(max_nb_chars=150),
                    score=random.randint(0, 100),
                    order=i,
                    time_taken_seconds=random.randint(60, 300)
                )

        # Create sample coding submissions
        self.stdout.write('Creating sample coding submissions...')
        for user in users:
            for problem in random.sample(problems, 3):
                Submission.objects.create(
                    user=user,
                    problem=problem,
                    language=random.choice(languages),
                    code=fake.text(max_nb_chars=500),
                    status=random.choice(['accepted', 'wrong_answer', 'time_limit_exceeded']),
                    execution_time=random.randint(100, 2000),
                    memory_used=random.randint(10, 200)
                )

        # Create sample chat sessions
        self.stdout.write('Creating sample chat sessions...')
        for user in users[:3]:  # First 3 users
            chat_session = ChatSession.objects.create(
                user=user,
                title=fake.sentence(nb_words=4),
                session_type='interview_prep'
            )

            # Create messages
            for i in range(random.randint(5, 15)):
                ChatMessage.objects.create(
                    session=chat_session,
                    content=fake.text(max_nb_chars=200),
                    is_user=random.choice([True, False])
                )

        # Create sample analytics
        self.stdout.write('Creating sample analytics...')
        for user in users:
            UserAnalytics.objects.create(
                user=user,
                total_interviews=Interview.objects.filter(user=user).count(),
                completed_interviews=Interview.objects.filter(user=user, status='completed').count(),
                average_interview_score=random.randint(65, 95),
                total_coding_problems=CodingProblem.objects.count(),
                solved_coding_problems=random.randint(5, 20),
                coding_success_rate=random.randint(40, 90),
                total_chat_sessions=ChatSession.objects.filter(user=user).count(),
                total_chat_messages=ChatMessage.objects.filter(session__user=user).count(),
                favorite_difficulty=random.choice(['easy', 'medium', 'hard']),
                favorite_topic=random.choice(['Arrays', 'Strings', 'Dynamic Programming']),
                improvement_areas=['Time complexity', 'Code optimization'],
                strengths=['Problem understanding', 'Algorithm design'],
                weekly_goal_completion=random.randint(50, 100),
                streak_days=random.randint(0, 30)
            )

            # Create performance records
            for problem in random.sample(problems, 3):
                CodingPerformance.objects.create(
                    user=user,
                    problem=problem,
                    best_time=random.randint(300, 1800),  # 5-30 minutes
                    best_memory=random.randint(1000, 50000),  # KB
                    attempts_to_solve=random.randint(1, 5),
                    time_to_first_attempt=random.randint(60, 600),
                    hints_used=random.randint(0, 3),
                    solution_quality_score=random.randint(6, 10),
                    code_efficiency_score=random.randint(6, 10),
                    readability_score=random.randint(6, 10)
                )

            # Create InterviewPerformance only for interviews that belong to this user
            user_interviews = [interview for interview in interviews if interview.user == user]
            for interview in user_interviews:
                InterviewPerformance.objects.create(
                    user=user,
                    interview=interview,
                    technical_score=random.randint(6, 10),
                    communication_score=random.randint(6, 10),
                    problem_solving_score=random.randint(6, 10),
                    behavioral_score=random.randint(6, 10),
                    response_times=[random.randint(30, 120) for _ in range(5)],
                    question_types_distribution={'technical': 3, 'behavioral': 2},
                    strengths=['Clear communication', 'Strong fundamentals'],
                    weaknesses=['Time management'],
                    recommendations=['Practice more system design questions'],
                    ai_feedback_summary=fake.text(max_nb_chars=200)
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data'))