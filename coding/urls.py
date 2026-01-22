from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'coding'

router = DefaultRouter()
router.register(r'languages', views.ProgrammingLanguageViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'problems', views.CodingProblemViewSet)
router.register(r'submissions', views.SubmissionViewSet)
router.register(r'progress', views.UserProgressViewSet)
router.register(r'snippets', views.CodeSnippetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('solve/<slug:slug>/', views.solve_problem, name='solve_problem'),
]