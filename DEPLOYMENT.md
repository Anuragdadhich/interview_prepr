# CodeInterviewPro - Deployment Guide

## 🚀 Quick Deployment Options

### 1. **Railway** (Recommended - Free tier available)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 2. **Heroku**
```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-app-name

# Set buildpacks (important!)
heroku buildpacks:add heroku/python

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set DATABASE_URL=your-database-url
# ... set other env vars from .env.example

# Deploy
git push heroku master
```

### 3. **PythonAnywhere** (Free tier available)

**Step-by-Step Setup:**

1. **Create PythonAnywhere Account**
   - Sign up at pythonanywhere.com
   - Choose "Beginner" account (free)

2. **Upload Your Code**
   ```bash
   # In PythonAnywhere bash console
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git codeinterviewpro
   cd codeinterviewpro
   ```

3. **Run Deployment Script**
   ```bash
   chmod +x deploy_pythonanywhere.sh
   ./deploy_pythonanywhere.sh
   ```

4. **Configure WSGI**
   - Go to PythonAnywhere Dashboard → Web
   - Create/Edit WSGI file: `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`
   - Copy content from `pythonanywhere_wsgi.py` and update YOUR_USERNAME

5. **Configure Static Files**
   - In Web dashboard, add static files mapping:
     - URL: `/static/`
     - Directory: `/home/YOUR_USERNAME/codeinterviewpro/staticfiles/`

6. **Set Environment Variables**
   - In Web dashboard → Environment variables
   - Add all variables from `.env.example`

7. **Database Setup**
   - PythonAnywhere provides free MySQL/PostgreSQL
   - Set `DATABASE_URL` in environment variables

**PythonAnywhere WSGI File** (`/var/www/username_pythonanywhere_com_wsgi.py`):
```python
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
```

**PythonAnywhere Limitations:**
- No WebSocket support on free tier
- Limited AI API calls (may need paid plan)
- Some packages may not install (check PythonAnywhere docs)
- Connect GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `python manage.py migrate && python manage.py collectstatic --noinput && gunicorn core.wsgi`
- Add environment variables

### 4. **Vercel** (For frontend only)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy static files
vercel --prod
```

## 📋 Environment Variables Required

Copy `.env.example` to `.env` and fill in:

- `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- `DATABASE_URL`: SQLite for dev, PostgreSQL URL for production
- `OPENAI_API_KEY`: From OpenAI Platform
- `SAMBA_NOVA_API_KEY`: From SambaNova
- `GEMINI_API_KEY`: From Google AI Studio
- `DEBUG=False` for production
- `ALLOWED_HOSTS`: Your domain for production

## 🔧 Production Configuration Files

Your repository includes production-ready configuration:

- **`Procfile`**: Process definitions for Heroku/Railway
- **`gunicorn.conf.py`**: Gunicorn server configuration
- **`runtime.txt`**: Python version specification (3.11.9)
- **`core/wsgi.py`**: Production WSGI application

## 🌐 Domain & SSL

For custom domains, configure DNS and SSL certificates through your hosting provider.