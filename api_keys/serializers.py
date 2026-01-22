from rest_framework import serializers
from .models import APIKey, APIUsage


class APIKeySerializer(serializers.ModelSerializer):
    masked_key = serializers.SerializerMethodField()

    class Meta:
        model = APIKey
        fields = [
            'id', 'provider', 'name', 'masked_key', 'is_active',
            'usage_count', 'last_used', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'last_used', 'created_at', 'updated_at']

    def get_masked_key(self, obj):
        return obj.mask_key()

    def create(self, validated_data):
        # Don't include api_key in validated_data for security
        api_key = validated_data.pop('api_key', None)
        if not api_key:
            from .models import generate_api_key
            api_key = generate_api_key()
        return APIKey.objects.create(api_key=api_key, **validated_data)


class APIKeyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['provider', 'name', 'api_key']

    def create(self, validated_data):
        return APIKey.objects.create(**validated_data)


class APIUsageSerializer(serializers.ModelSerializer):
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)

    class Meta:
        model = APIUsage
        fields = [
            'id', 'api_key', 'api_key_name', 'endpoint', 'method',
            'status_code', 'tokens_used', 'cost', 'response_time', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']