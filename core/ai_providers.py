"""
AI Provider abstraction layer for multiple AI services
Supports OpenAI, SambaNova, Google Gemini, and Anthropic
"""

import json
import requests
from django.conf import settings
import google.genai as genai
import openai
import anthropic


class AIProvider:
    """Base class for AI providers"""

    def __init__(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name

    def generate_content(self, prompt, **kwargs):
        """Generate content using the AI provider"""
        raise NotImplementedError("Subclasses must implement generate_content")


class OpenAIProvider(AIProvider):
    """OpenAI API provider"""

    def __init__(self, api_key=None, model_name="gpt-4o-mini"):
        super().__init__(api_key or settings.OPENAI_API_KEY, model_name)
        if self.api_key:
            openai.api_key = self.api_key

    def generate_content(self, prompt, **kwargs):
        """Generate content using OpenAI API"""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class SambaNovaProvider(AIProvider):
    """SambaNova API provider"""

    def __init__(self, api_key=None, model_name="Meta-Llama-3.1-8B-Instruct"):
        super().__init__(api_key or settings.SAMBA_NOVA_API_KEY, model_name)
        self.base_url = "https://api.sambanova.ai/v1"

    def generate_content(self, prompt, **kwargs):
        """Generate content using SambaNova API"""
        if not self.api_key:
            raise ValueError("SambaNova API key not configured")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7)
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                raise Exception(f"SambaNova API error: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"SambaNova API error: {str(e)}")


class GoogleGeminiProvider(AIProvider):
    """Google Gemini API provider"""

    def __init__(self, api_key=None, model_name="gemini-2.0-flash-exp"):
        super().__init__(api_key or settings.GEMINI_API_KEY, model_name)

    def generate_content(self, prompt, **kwargs):
        """Generate content using Google Gemini API"""
        if not self.api_key:
            raise ValueError("Google Gemini API key not configured")

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    'max_output_tokens': kwargs.get('max_tokens', 1000),
                    'temperature': kwargs.get('temperature', 0.7)
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Google Gemini API error: {str(e)}")


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider"""

    def __init__(self, api_key=None, model_name="claude-3-5-haiku-20241022"):
        super().__init__(api_key or settings.ANTHROPIC_API_KEY, model_name)

    def generate_content(self, prompt, **kwargs):
        """Generate content using Anthropic Claude API"""
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")

        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")



class AIProviderManager:
    """Manager class for AI providers with fallback support"""

    PROVIDERS = {
        'openai': OpenAIProvider,
        'samba_nova': SambaNovaProvider,
        'gemini': GoogleGeminiProvider,
        'anthropic': AnthropicProvider,
    }

    def __init__(self):
        self.providers = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available providers based on configured API keys"""
        # OpenAI (has free tier credits)
        if settings.OPENAI_API_KEY:
            self.providers['openai'] = OpenAIProvider()

        # SambaNova (check for free tiers)
        if settings.SAMBA_NOVA_API_KEY:
            self.providers['samba_nova'] = SambaNovaProvider()

        # Google Gemini (free tier available)
        if settings.GEMINI_API_KEY:
            self.providers['gemini'] = GoogleGeminiProvider()

        # Anthropic - commented out due to cost concerns
        # if settings.ANTHROPIC_API_KEY:
        #     self.providers['anthropic'] = AnthropicProvider()

    def get_provider(self, provider_name=None):
        """Get a specific provider or the first available one"""
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name]

        # Return first available provider as fallback
        if self.providers:
            return next(iter(self.providers.values()))

        raise ValueError("No AI providers configured")

    def generate_content(self, prompt, provider_name=None, **kwargs):
        """Generate content using specified provider or fallback"""
        providers_to_try = []

        if provider_name and provider_name in self.providers:
            providers_to_try = [provider_name]
        else:
            # Try providers in order of preference: OpenAI, SambaNova, Gemini, Anthropic
            preferred_order = ['openai', 'samba_nova', 'gemini', 'anthropic']
            providers_to_try = [p for p in preferred_order if p in self.providers]

        for provider_name in providers_to_try:
            try:
                provider = self.providers[provider_name]
                return provider.generate_content(prompt, **kwargs)
            except Exception as e:
                print(f"Warning: {provider_name} provider failed: {str(e)}")
                continue

        raise ValueError("All AI providers failed. Please check your API keys and network connection.")

    def get_available_providers(self):
        """Get list of available providers"""
        return list(self.providers.keys())


# Global instance
ai_manager = AIProviderManager()