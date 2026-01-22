from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'interviews', views.InterviewViewSet)
router.register(r'questions', views.InterviewQuestionViewSet)
router.register(r'sessions', views.InterviewSessionViewSet)
router.register(r'templates', views.InterviewTemplateViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]