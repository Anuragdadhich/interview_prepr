#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
import django
django.setup()

# Run collectstatic
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])