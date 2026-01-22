#!/usr/bin/env python
"""
Test script for AI provider integration
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.ai_providers import ai_manager

def test_ai_providers():
    """Test all available AI providers"""
    print("Testing AI Provider Integration")
    print("=" * 40)

    # Get available providers
    available_providers = ai_manager.get_available_providers()
    print(f"Available providers: {available_providers}")
    print()

    # Test prompt
    test_prompt = "Explain what a REST API is in 2-3 sentences."

    # Test each provider
    for provider_name in available_providers:
        print(f"Testing {provider_name.upper()} provider:")
        try:
            response = ai_manager.generate_content(
                test_prompt,
                provider_name=provider_name,
                max_tokens=200,
                temperature=0.7
            )
            print(f"✓ Success: {response[:100]}...")
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
        print()

    # Test fallback (no specific provider)
    print("Testing fallback (no specific provider):")
    try:
        response = ai_manager.generate_content(test_prompt, max_tokens=200)
        print(f"✓ Success: {response[:100]}...")
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
    print()

if __name__ == "__main__":
    test_ai_providers()