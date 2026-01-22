from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('practice/', views.practice_view, name='practice'),
    path('mock-interview/', views.mock_interview_view, name='mock_interview'),
    path('progress/', views.progress_view, name='progress'),
    path('profile/', views.profile_view, name='profile'),

    # API endpoints
    path('api/profile/', views.user_profile_api, name='user_profile_api'),
    path('api/analytics/', views.user_analytics_api, name='user_analytics_api'),
]