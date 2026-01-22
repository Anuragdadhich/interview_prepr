from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import APIKey, APIUsage
from .serializers import APIKeySerializer, APIUsageSerializer


class APIKeyViewSet(viewsets.ModelViewSet):
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle API key active status"""
        api_key = self.get_object()
        api_key.is_active = not api_key.is_active
        api_key.save()
        return Response({'status': 'success', 'is_active': api_key.is_active})

    @action(detail=True, methods=['get'])
    def usage_stats(self, request, pk=None):
        """Get usage statistics for an API key"""
        api_key = self.get_object()
        usages = APIUsage.objects.filter(api_key=api_key)

        stats = {
            'total_requests': usages.count(),
            'total_tokens': usages.filter(tokens_used__isnull=False).aggregate(
                total=models.Sum('tokens_used')
            )['total'] or 0,
            'total_cost': usages.filter(cost__isnull=False).aggregate(
                total=models.Sum('cost')
            )['total'] or 0,
            'success_rate': usages.filter(status_code__lt=400).count() / usages.count() * 100 if usages.exists() else 0,
        }

        return Response(stats)


class APIUsageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = APIUsage.objects.all()
    serializer_class = APIUsageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return APIUsage.objects.filter(api_key__user=self.request.user)
