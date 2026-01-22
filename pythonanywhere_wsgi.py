# PythonAnywhere WSGI Configuration
# Save this as: /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py

import os
import sys

# Add your project directory to the path
# Replace 'YOUR_USERNAME' with your PythonAnywhere username
path = '/home/YOUR_USERNAME/codeinterviewpro'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables (optional - you can set these in PythonAnywhere dashboard)
os.environ.setdefault('SECRET_KEY', 'your-secret-key-here')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('DATABASE_URL', 'your-database-url-here')
# Add other environment variables as needed

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

# Import Django
import django
django.setup()

# Import the WSGI application
from core.wsgi import application