from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import models
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm
from .models import Profile, UserAnalytics
from .serializers import ProfileSerializer, UserAnalyticsSerializer
from interviews.models import Interview
from coding.models import Submission, CodingProblem
from chat.models import ChatSession
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def home(request):
    return render(request, 'users/home.html')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            # Authenticate the user after registration
            user = authenticate(request, email=user.email, password=form.cleaned_data['password1'])
            if user:
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            return redirect(request.GET.get('next', 'dashboard'))
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard_view(request):
    # Get user analytics
    analytics, created = UserAnalytics.objects.get_or_create(user=request.user)

    # Get recent activity
    recent_interviews = Interview.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_submissions = Submission.objects.filter(user=request.user).order_by('-submitted_at')[:5]
    recent_chat_sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')[:3]

    context = {
        'analytics': analytics,
        'recent_interviews': recent_interviews,
        'recent_submissions': recent_submissions,
        'recent_chat_sessions': recent_chat_sessions,
    }

    return render(request, 'users/dashboard.html', context)


@login_required
def practice_view(request):
    # Get all coding problems
    problems = CodingProblem.objects.filter(is_active=True).order_by('-created_at')

    # Filter by difficulty if provided
    difficulty = request.GET.get('difficulty')
    if difficulty:
        problems = problems.filter(difficulty=difficulty)

    # Filter by topic if provided
    topic = request.GET.get('topic')
    if topic:
        problems = problems.filter(topics__name=topic)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        problems = problems.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )

    context = {
        'problems': problems,
        'difficulty': difficulty,
        'topic': topic,
        'search_query': search_query,
    }

    return render(request, 'users/practice.html', context)


@login_required
def mock_interview_view(request):
    return render(request, 'users/mock_interview.html')


@login_required
def progress_view(request):
    return render(request, 'users/progress.html')


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/profile.html', {'form': form, 'profile': profile})


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """Get user profile data"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_analytics_api(request):
    """Get user analytics data"""
    analytics, created = UserAnalytics.objects.get_or_create(user=request.user)
    # Update analytics before returning
    analytics.update_interview_stats()
    analytics.update_coding_stats()
    analytics.update_chat_stats()

    serializer = UserAnalyticsSerializer(analytics)
    return Response(serializer.data)
