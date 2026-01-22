"""
WSGI config for codeinterviewpro project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application

# Apply WSGI middleware and application
application = get_wsgi_application()

# Production optimizations (uncomment if needed)
# from whitenoise import WhiteNoise
# application = WhiteNoise(application, root=settings.STATIC_ROOT)
