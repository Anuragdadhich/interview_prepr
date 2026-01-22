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

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
# ... set other env vars

# Deploy
git push heroku main
```

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
- `OPENAI_API_KEY`: From OpenAI Platform
- `SAMBA_NOVA_API_KEY`: From SambaNova
- `GEMINI_API_KEY`: From Google AI Studio
- `DEBUG=False` for production
- Database URL for production database

## 🔧 Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use production database (PostgreSQL)
- [ ] Set up Redis for WebSockets
- [ ] Configure static file serving
- [ ] Set up HTTPS
- [ ] Configure proper logging
- [ ] Set up monitoring
- [ ] Configure backup strategy

## 🌐 Domain & SSL

For custom domains, configure DNS and SSL certificates through your hosting provider.