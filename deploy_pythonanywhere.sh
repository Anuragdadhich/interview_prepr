# PythonAnywhere Deployment Script
# Run this in PythonAnywhere bash console

echo "Setting up CodeInterviewPro on PythonAnywhere"

# Go to your project directory
cd ~/codeinterviewpro

# Create virtual environment (if not already created)
python3.11 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (optional)
echo "Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com

echo "Setup complete! Configure your WSGI file and static files in the PythonAnywhere dashboard."