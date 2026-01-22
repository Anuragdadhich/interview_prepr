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

### 3. **Render** (Free tier available)
- Connect GitHub repository
- **Runtime**: Python 3.11.9
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput --clear`
- **Start Command**: `gunicorn --config gunicorn.conf.py core.wsgi:application`
- **Environment Variables**: Set all from `.env.example`
- **Database**: PostgreSQL (Render provides free PostgreSQL)
- Set `DATABASE_URL` to your Render PostgreSQL connection string

### 3. **Render**
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