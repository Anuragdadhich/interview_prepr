# AI-Powered Interview Preparation Platform

A production-ready Django application that simulates real technical interviews with AI interviewers, real-time coding environments, and comprehensive performance analytics.

## Features

### 🎯 Core Functionality
- **Live AI Interviewer**: Powered by Google Gemini API for intelligent question generation and feedback
- **Real-time Coding Environment**: WebSocket-based coding interface with Judge0 API integration
- **Intelligent Feedback**: AI-powered analysis of user responses with detailed scoring
- **User Performance Analytics**: Comprehensive tracking of interview performance and coding progress

### 🤖 AI Integration
- **Multiple AI Providers**: Support for OpenAI GPT, Anthropic Claude, and Google Gemini
- **Dynamic Question Generation**: Context-aware questions based on user role and difficulty
- **Real-time Feedback**: Instant AI evaluation of answers with improvement suggestions

### 💻 Technical Features
- **WebSocket Communication**: Real-time bidirectional communication for interviews and coding
- **Code Execution**: Remote code execution with multiple language support
- **Speech Processing**: Voice input/output capabilities (models implemented)
- **API Key Management**: Secure storage and management of external API keys

### 📊 Analytics & Tracking
- **Interview Performance**: Detailed scoring across multiple dimensions
- **Coding Progress**: Problem-solving statistics and improvement tracking
- **User Insights**: Personalized recommendations and learning paths

## Tech Stack

- **Backend**: Django 4.2, Django Channels, Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production)
- **WebSockets**: Django Channels with Redis
- **AI APIs**: Google Gemini, OpenAI GPT, Anthropic Claude
- **Code Execution**: Judge0 API
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Tailwind CSS
- **Authentication**: Django Allauth (Google OAuth support)

## Installation

### Prerequisites
- Python 3.8+
- Redis (for WebSocket support)
- Docker (optional, for local development)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd codeinterviewpro
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py populate_sample_data
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Redis server**
   ```bash
   redis-server
   ```

8. **Run the application**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# AI API Keys
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# External Services
JUDGE0_API_URL=https://api.judge0.com
JUDGE0_API_KEY=your-judge0-api-key

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### API Keys Setup

1. **Google Gemini**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Anthropic**: Get API key from [Anthropic Console](https://console.anthropic.com/)
4. **Judge0**: Get API key from [Judge0](https://judge0.com/) (optional for development)

## Usage

### Starting an Interview

1. Navigate to `/mock-interview/` after logging in
2. Click "Start New Interview"
3. Answer questions in real-time
4. Receive AI feedback after each response
5. View performance analytics at the end

### Coding Practice

1. Navigate to `/practice/` or `/coding/`
2. Select a problem from the available challenges
3. Write code in the real-time editor
4. Run test cases and submit for evaluation
5. View detailed results and analytics

### Managing API Keys

1. Go to `/api/keys/` in the admin interface
2. Add your API keys for different providers
3. Configure which AI provider to use for interviews

## API Endpoints

### REST API
- `GET/POST /api/interviews/` - Interview management
- `GET/POST /api/coding/problems/` - Coding problems
- `POST /api/coding/submissions/` - Code submissions
- `GET/POST /api/chat/sessions/` - Chat sessions

### WebSocket Endpoints
- `ws://localhost:8000/ws/interview/{session_id}/` - Real-time interviews
- `ws://localhost:8000/ws/coding/{problem_id}/` - Real-time coding

## Development

### Running Tests
```bash
python manage.py test
```

### Code Formatting
```bash
black .
isort .
```

### Database Management
```bash
python manage.py makemigrations
python manage.py migrate
```

### Sample Data
```bash
python manage.py populate_sample_data
```

## Deployment

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**
   ```bash
   vercel
   ```

3. **Set Environment Variables in Vercel Dashboard**
   - Go to your project in Vercel dashboard
   - Navigate to Settings > Environment Variables
   - Add all the environment variables from your `.env` file

4. **Database Configuration**
   - Use a cloud database like PostgreSQL on Railway, PlanetScale, or Supabase
   - Update `DATABASE_URL` environment variable

5. **Static Files**
   - Static files are automatically collected during build
   - Served directly by Vercel CDN

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database (PostgreSQL)
- [ ] Set up proper static file serving
- [ ] Configure HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

### Docker Deployment
```bash
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Contact the development team

## Roadmap

### Upcoming Features
- [ ] Voice-based interviews
- [ ] Video interview recording
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Integration with popular coding platforms
- [ ] Team collaboration features
- [ ] Custom interview templates