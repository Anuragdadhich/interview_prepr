from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import SpeechSession, VoiceProfile
from .serializers import SpeechSessionSerializer, VoiceProfileSerializer
# import speech_recognition as sr  # Temporarily commented out
from django.conf import settings
from django.utils import timezone
import os


class SpeechSessionViewSet(viewsets.ModelViewSet):
    queryset = SpeechSession.objects.all()
    serializer_class = SpeechSessionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return SpeechSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def transcribe(self, request, pk=None):
        """Transcribe uploaded audio file"""
        session = self.get_object()

        if not session.audio_file:
            return Response({'error': 'No audio file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Process the audio file
            result = self._transcribe_audio(session.audio_file.path, session.language)

            # Update session with results
            session.transcribed_text = result['text']
            session.confidence_score = result['confidence']
            session.duration_seconds = result['duration']
            session.is_processed = True
            session.processed_at = timezone.now()
            session.save()

            return Response({
                'transcribed_text': result['text'],
                'confidence_score': result['confidence'],
                'duration_seconds': result['duration']
            })

        except Exception as e:
            session.processing_error = str(e)
            session.is_processed = True
            session.save()

            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _transcribe_audio(self, audio_path, language):
        """Transcribe audio using speech recognition"""
        try:
            recognizer = sr.Recognizer()

            # Load audio file
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                duration = source.DURATION if hasattr(source, 'DURATION') else 0

            # Perform speech recognition
            text = recognizer.recognize_google(audio_data, language=language)

            # Calculate confidence (simplified - speech_recognition doesn't provide confidence)
            confidence = 0.8 if len(text.split()) > 3 else 0.6

            return {
                'text': text,
                'confidence': confidence,
                'duration': duration
            }

        except sr.UnknownValueError:
            return {
                'text': '',
                'confidence': 0.0,
                'duration': 0
            }
        except sr.RequestError as e:
            raise Exception(f"Speech recognition service error: {e}")


class VoiceProfileViewSet(viewsets.ModelViewSet):
    queryset = VoiceProfile.objects.all()
    serializer_class = VoiceProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VoiceProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_sample(self, request, pk=None):
        """Add a voice sample to the profile"""
        profile = self.get_object()
        audio_file = request.FILES.get('audio_file')

        if not audio_file:
            return Response({'error': 'No audio file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the audio file temporarily and process it
        temp_path = f"/tmp/{audio_file.name}"
        with open(temp_path, 'wb+') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        try:
            # Extract features from the audio sample
            features = self._extract_voice_features(temp_path)

            # Add to voice samples
            samples = profile.voice_samples or []
            samples.append({
                'file_path': f"voice_samples/{profile.user.id}/{audio_file.name}",
                'features': features,
                'uploaded_at': timezone.now().isoformat()
            })

            profile.voice_samples = samples
            profile.is_calibrated = len(samples) >= 3  # Calibrated after 3 samples
            profile.save()

            # Clean up temp file
            os.remove(temp_path)

            return Response({'message': 'Voice sample added successfully'})

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _extract_voice_features(self, audio_path):
        """Extract basic voice features (simplified)"""
        # This is a simplified implementation
        # In production, you'd use libraries like librosa for proper feature extraction
        return {
            'duration': 0,
            'sample_rate': 16000,
            'features': []
        }
