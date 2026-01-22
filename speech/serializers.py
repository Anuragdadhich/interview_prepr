from rest_framework import serializers
from .models import SpeechSession, VoiceProfile


class SpeechSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechSession
        fields = '__all__'
        read_only_fields = ('created_at', 'processed_at')


class VoiceProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceProfile
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')