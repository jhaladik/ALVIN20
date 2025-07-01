# 🎭 ALVIN - AI-Powered Creative Writing Assistant

ALVIN is a comprehensive creative writing platform that leverages Claude AI to help writers develop stories, analyze content, and enhance their creative process. From initial idea to finished manuscript, ALVIN provides intelligent assistance every step of the way.

## ✨ Features

### 🤖 AI-Powered Writing Assistance
- **Story Idea Analysis**: Get intelligent feedback on your story concepts
- **Automated Project Creation**: Transform ideas into structured projects
- **Scene Suggestions**: AI-generated scene recommendations and outlines
- **Character Development**: Deep character analysis and development suggestions
- **Plot Enhancement**: Story structure analysis and improvement recommendations
- **Dialogue Enhancement**: Improve character voices and conversation flow

### 📚 Project Management
- **Multi-Project Support**: Manage multiple writing projects simultaneously
- **Phase-Based Workflow**: Organize projects through idea, expansion, and story phases
- **Scene Organization**: Create, organize, and reorder scenes with drag-and-drop
- **Story Objects**: Manage characters, locations, objects, and themes
- **Progress Tracking**: Monitor word counts, completion status, and writing goals

### 👥 Collaboration Features
- **Real-Time Collaboration**: Work with others using Socket.IO-powered live editing
- **Comment System**: Add and manage feedback with threaded comments
- **User Permissions**: Granular access control for collaborators
- **Live Presence**: See who's online and actively editing
- **Typing Indicators**: Real-time typing status for collaborative sessions

### 📊 Analytics & Insights
- **Writing Analytics**: Track productivity, word counts, and writing streaks
- **Token Usage Monitoring**: Monitor AI operation costs and usage patterns
- **Project Progress Visualization**: Visual charts and progress tracking
- **Goal Setting**: Set and track daily, weekly, and monthly writing goals
- **Activity Timeline**: Comprehensive history of all writing activities

### 🎨 Export & Sharing
- **Multiple Formats**: Export to TXT, HTML, PDF, DOCX, and JSON
- **Professional Formatting**: Publication-ready document generation
- **Data Portability**: Complete project backup and restore capabilities
- **Print Optimization**: Print-friendly layouts and styling

### 🔐 Security & Privacy
- **JWT Authentication**: Secure token-based authentication
- **Data Encryption**: Encrypted storage for sensitive content
- **Privacy Controls**: Granular privacy settings for projects and collaboration
- **API Key Management**: Secure API access for integrations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Anthropic API Key (for Claude AI integration)

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/alvin.git
cd alvin
```

2. **Backend Setup**
```bash
cd backend
python setup.py
```

3. **Frontend Setup**
```bash
cd ../frontend
npm install
```

4. **Environment Configuration**
Edit `backend/.env` file and add your API keys:
```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here
STRIPE_SECRET_KEY=your-stripe-secret-key-here
```

5. **Start the Application**

Backend (Terminal 1):
```bash
cd backend
python run.py
```

Frontend (Terminal 2):
```bash
cd frontend
npm run dev
```

6. **Access the Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/health

### Demo Account
- **Email**: demo@alvin.ai
- **Password**: demo123

## 🏗️ Architecture

### Backend (Flask)
```
backend/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models/                  # Database models
│   ├── routes/                  # API endpoints
│   │   ├── auth.py             # Authentication
│   │   ├── projects.py         # Project management
│   │   ├── scenes.py           # Scene management
│   │   ├── objects.py          # Story objects
│   │   ├── ai.py               # AI operations
│   │   ├── collaboration.py    # Real-time collaboration
│   │   ├── billing.py          # Subscription management
│   │   └── analytics.py        # Analytics and insights
│   ├── services/               # Business logic
│   │   ├── claude_service.py   # Claude AI integration
│   │   ├── export_service.py   # Document export
│   │   └── token_service.py    # Token management
│   └── sockets.py              # Socket.IO events
├── migrations/                 # Database migrations
├── tests/                      # Test suites
├── config.py                   # Configuration
├── run.py                      # Application runner
└── setup.py                    # Setup script
```

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/             # Reusable components
│   ├── pages/                  # Page components
│   ├── hooks/                  # Custom React hooks
│   ├── context/                # React context providers
│   ├── services/               # API services
│   └── utils/                  # Utility functions
├── public/                     # Static assets
└── package.json                # Dependencies
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Flask Configuration
FLASK_CONFIG=development
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DATABASE_URL=sqlite:///alvin_dev.db

# Claude AI
ANTHROPIC_API_KEY=your-anthropic-key
AI_SIMULATION_MODE=false
DEFAULT_CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Billing (Stripe)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional Services
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_APP_VERSION=1.0.0
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Integration Tests
```bash
cd backend
python -m pytest tests/test_integration.py -v
```

## 🚢 Deployment

### Docker Deployment

1. **Build and Run with Docker Compose**
```bash
docker-compose up --build
```

2. **Environment Configuration**
Copy `.env.example` to `.env.production` and configure for production.

### Manual Deployment

#### Backend (Production)
```bash
cd backend
pip install -r requirements.txt
export FLASK_CONFIG=production
export DATABASE_URL=postgresql://user:pass@host:port/db
export ANTHROPIC_API_KEY=your-key
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

#### Frontend (Production)
```bash
cd frontend
npm run build
# Serve the dist/ directory with nginx or similar
```

### Database Migrations
```bash
cd backend
flask db init     # First time only
flask db migrate  # Create migration
flask db upgrade  # Apply migration
```

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/profile` - Update user profile

### Project Management
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### AI Operations
- `POST /api/ai/analyze-idea` - Analyze story idea
- `POST /api/ai/create-project-from-idea` - Create project from idea
- `POST /api/ai/projects/{id}/analyze-structure` - Analyze story structure
- `POST /api/ai/projects/{id}/suggest-scenes` - Generate scene suggestions
- `POST /api/ai/projects/{id}/generate-story` - Generate complete story

### Real-Time Features (Socket.IO)
- `join_project` - Join project room for collaboration
- `scene_updated` - Broadcast scene changes
- `typing_status` - Share typing indicators
- `comment_added` - Share new comments

## 🎯 Usage Examples

### Creating Your First Project

1. **Start with an Idea**
```javascript
// Analyze your story idea
const response = await api.post('/api/ai/analyze-idea', {
  idea_text: "A detective investigates mysterious disappearances in a small town",
  target_audience: "Adult",
  preferred_genre: "Mystery"
});
```

2. **Create a Project**
```javascript
// Create structured project from idea
const project = await api.post('/api/ai/create-project-from-idea', {
  idea_text: "A detective investigates mysterious disappearances...",
  title: "Mystery in Millbrook"
});
```

3. **Develop Scenes**
```javascript
// Get AI scene suggestions
const scenes = await api.post(`/api/ai/projects/${projectId}/suggest-scenes`, {
  target_length: "medium"
});
```

### Real-Time Collaboration

```javascript
// Join project for real-time collaboration
socket.emit('join_project', { project_id: projectId });

// Listen for updates
socket.on('scene_updated', (data) => {
  console.log('Scene updated by:', data.updated_by.username);
  // Update UI with new scene data
});

// Send typing status
socket.emit('typing_status', {
  project_id: projectId,
  scene_id: sceneId,
  is_typing: true
});
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `npm test` and `python -m pytest`
6. Submit a pull request

### Code Style
- **Backend**: Follow PEP 8 for Python code
- **Frontend**: Use Prettier and ESLint configurations
- **Commits**: Use conventional commit format

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude AI API
- **OpenAI** for backup AI capabilities
- **React Team** for the amazing frontend framework
- **Flask Team** for the lightweight backend framework

## 🆘 Support

### Getting Help
- 📖 [Documentation](https://docs.alvin.ai)
- 💬 [Discord Community](https://discord.gg/alvin)
- 📧 Email: support@alvin.ai
- 🐛 [Issue Tracker](https://github.com/yourusername/alvin/issues)

### Troubleshooting

#### Common Issues

**"Claude API key not working"**
```bash
# Test your API key
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.anthropic.com/v1/messages
```

**"Database connection failed"**
```bash
# Reset database
python force_db_init.py
```

**"Frontend not connecting to backend"**
- Check CORS settings in `backend/config.py`
- Verify VITE_API_URL in frontend `.env`
- Ensure backend is running on port 5000

#### Performance Optimization

**Large Projects**
- Enable pagination for scenes: `?page=1&limit=50`
- Use incremental loading for large story objects
- Consider database indexing for frequently queried fields

**Token Usage**
- Monitor usage with analytics dashboard
- Set up alerts for high token consumption
- Use simulation mode for development

## 🗺️ Roadmap

### Version 1.1 (Q2 2024)
- [ ] Mobile app (React Native)
- [ ] Advanced AI models integration
- [ ] Enhanced collaboration features
- [ ] Marketplace for writing templates

### Version 1.2 (Q3 2024)
- [ ] Multi-language support
- [ ] Advanced analytics and insights
- [ ] Integration with publishing platforms
- [ ] Writing contest and community features

### Version 2.0 (Q4 2024)
- [ ] Voice-to-text integration
- [ ] AI-powered illustration generation
- [ ] Advanced plot analysis tools
- [ ] Enterprise team management

---

**Happy Writing! 🎭✨**

For more information, visit [https://alvin.ai](https://alvin.ai)