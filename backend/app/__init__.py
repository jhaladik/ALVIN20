# app/__init__.py - ALVIN Complete Backend with Authentication
import os
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()
jwt = JWTManager()

def create_app(config_name=None):
    """Create complete Flask application with authentication"""
    
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'alvin-dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_ALGORITHM'] = 'HS256'
    
    # Debug JWT configuration
    print(f"🔍 JWT Secret Key: {app.config['JWT_SECRET_KEY'][:10]}...")
    print(f"🔍 JWT Algorithm: {app.config['JWT_ALGORITHM']}")
    print(f"🔍 JWT Expires: {app.config['JWT_ACCESS_TOKEN_EXPIRES']}")
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("Warning: DATABASE_URL not set, using SQLite")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alvin.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'], supports_credentials=True)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # Import models
    with app.app_context():
        from app.models import User, Project, Scene, StoryObject
        
        # Create tables
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Create demo user if it doesn't exist
        demo_user = User.query.filter_by(email='demo@alvin.ai').first()
        if not demo_user:
            demo_user = User(
                username='demo_user',
                email='demo@alvin.ai',
                full_name='Demo User',
                plan='free',
                is_active=True,
                tokens_limit=10000
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
            print("✅ Demo user created: demo@alvin.ai / demo123")
    
    # ============================================================================
    # BASIC ROUTES
    # ============================================================================
    
    @app.route('/')
    def home():
        return jsonify({
            'message': '🎭 ALVIN Backend is WORKING!',
            'status': 'running',
            'version': '1.0.0',
            'description': 'AI-powered creative writing assistant backend',
            'endpoints': {
                'health': '/health',
                'api': '/api',
                'demo': '/demo',
                'auth': '/api/auth'
            }
        })
    
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ALVIN API',
            'version': '1.0.0',
            'message': 'Backend is running successfully!',
            'database': 'Available',
            'authentication': 'Ready',
            'socketio': 'WebSocket ready'
        })
    
    @app.route('/api')
    def api_info():
        return jsonify({
            'service': 'ALVIN API',
            'version': '1.0.0',
            'status': 'Ready',
            'authentication': 'JWT enabled',
            'endpoints': {
                'register': '/api/auth/register',
                'login': '/api/auth/login',
                'profile': '/api/auth/profile',
                'projects': '/api/projects'
            },
            'demo_account': {
                'email': 'demo@alvin.ai',
                'password': 'demo123'
            }
        })
    
    # ============================================================================
    # AUTHENTICATION ROUTES
    # ============================================================================
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """User registration endpoint"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'message': 'Please check your input'}), 400
            
            # Validate required fields
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            name = data.get('name', '').strip()
            
            if not email or not password:
                return jsonify({'message': 'Please check your input'}), 400
            
            # Check if user exists
            from app.models import User
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'message': 'Email already registered'}), 400
            
            # Create username from email
            username = email.split('@')[0]
            counter = 1
            original_username = username
            while User.query.filter_by(username=username).first():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=name or f"User {username}",
                plan='free',
                is_active=True,
                tokens_limit=1000
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(identity=str(user.id))  # Convert to string
            
            return jsonify({
                'message': 'User created successfully',
                'access_token': access_token,
                'user': user.to_dict()
            }), 201
            
        except Exception as e:
            print(f"Registration error: {e}")
            return jsonify({'message': 'Please check your input'}), 400
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """User login endpoint"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'message': 'Email or password is incorrect'}), 401
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'message': 'Email or password is incorrect'}), 401
            
            # Find user
            from app.models import User
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                return jsonify({'message': 'Email or password is incorrect'}), 401
            
            if not user.is_active:
                return jsonify({'message': 'Account is disabled'}), 401
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create access token with additional claims
            additional_claims = {"user_email": user.email, "user_plan": user.plan}
            access_token = create_access_token(
                identity=str(user.id),  # Convert to string - JWT requires string subject
                additional_claims=additional_claims
            )
            
            print(f"✅ User {email} logged in successfully, token created")
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': user.to_dict(),
                'token_type': 'Bearer'
            }), 200
            
        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({'message': 'Email or password is incorrect'}), 401
    
    @app.route('/api/auth/verify', methods=['GET'])
    @jwt_required()
    def verify_token():
        """Verify if the current token is valid"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)  # Convert back to int
            auth_header = request.headers.get('Authorization', 'Not provided')
            print(f"🔍 Debug - Token verification for user_id: {user_id} (from string: {user_id_str})")
            print(f"🔍 Debug - Authorization header: {auth_header[:100]}...")
            
            from app.models import User
            user = User.query.get(user_id)
            
            if not user:
                print(f"❌ User {user_id} not found in database")
                return jsonify({'valid': False, 'message': 'User not found'}), 404
            
            print(f"✅ Token verification successful for {user.email}")
            return jsonify({
                'valid': True,
                'user_id': user_id,
                'email': user.email,
                'message': 'Token is valid'
            }), 200
            
        except Exception as e:
            print(f"❌ Token verification error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'valid': False, 'message': 'Token verification failed'}), 500
    
    @app.route('/api/debug/headers', methods=['GET', 'POST'])
    def debug_headers():
        """Debug endpoint to see all headers"""
        headers_dict = dict(request.headers)
        print(f"🔍 Debug - All headers received: {headers_dict}")
        
        return jsonify({
            'method': request.method,
            'headers': headers_dict,
            'has_auth': 'Authorization' in headers_dict,
            'auth_header': headers_dict.get('Authorization', 'Not provided')
        }), 200
    
    @app.route('/api/debug/decode-token', methods=['POST'])
    def debug_decode_token():
        """Debug endpoint to decode JWT token without validation"""
        try:
            data = request.get_json()
            token = data.get('token', '')
            
            if not token:
                return jsonify({'error': 'No token provided'}), 400
            
            # Decode without verification to see contents
            import jwt as pyjwt
            try:
                # First try to decode without verification
                decoded_unverified = pyjwt.decode(token, options={"verify_signature": False})
                print(f"🔍 Token payload (unverified): {decoded_unverified}")
                
                # Now try to decode with our secret
                secret = app.config['JWT_SECRET_KEY']
                algorithm = app.config['JWT_ALGORITHM']
                
                try:
                    decoded_verified = pyjwt.decode(token, secret, algorithms=[algorithm])
                    print(f"🔍 Token payload (verified): {decoded_verified}")
                    
                    return jsonify({
                        'status': 'valid',
                        'payload_unverified': decoded_unverified,
                        'payload_verified': decoded_verified,
                        'secret_used': secret[:10] + '...',
                        'algorithm_used': algorithm
                    }), 200
                    
                except pyjwt.InvalidTokenError as e:
                    print(f"🔍 JWT verification failed: {e}")
                    return jsonify({
                        'status': 'invalid',
                        'payload_unverified': decoded_unverified,
                        'verification_error': str(e),
                        'secret_used': secret[:10] + '...',
                        'algorithm_used': algorithm
                    }), 200
                    
            except Exception as e:
                print(f"🔍 Token decode error: {e}")
                return jsonify({'error': f'Token decode failed: {e}'}), 400
                
        except Exception as e:
            print(f"🔍 Debug decode error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        """Get current user profile"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)  # Convert back to int
            print(f"📋 Profile request for user_id: {user_id}")
            
            from app.models import User
            user = User.query.get(user_id)
            
            if not user:
                print(f"❌ User {user_id} not found in database")
                return jsonify({'message': 'User not found'}), 404
            
            print(f"✅ Profile retrieved for user: {user.email}")
            return jsonify({
                'user': user.to_dict()
            }), 200
            
        except Exception as e:
            print(f"Profile error: {e}")
            return jsonify({'message': 'Unable to get profile'}), 500
    
    # ============================================================================
    # PROJECT ROUTES
    # ============================================================================
    
    @app.route('/api/projects', methods=['GET'])
    @jwt_required()
    def get_projects():
        """Get user's projects"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)  # Convert back to int
            print(f"📝 Projects request for user_id: {user_id}")
            
            # Log authorization header for debugging
            auth_header = request.headers.get('Authorization', 'Not provided')
            print(f"🔐 Authorization header: {auth_header[:50]}...")
            
            from app.models import User, Project
            user = User.query.get(user_id)
            
            if not user:
                print(f"❌ User {user_id} not found in database")
                return jsonify({'message': 'User not found'}), 404
            
            projects = user.projects.all()
            print(f"✅ Found {len(projects)} projects for user: {user.email}")
            
            return jsonify({
                'projects': [project.to_dict() for project in projects]
            }), 200
            
        except Exception as e:
            print(f"Projects error: {e}")
            return jsonify({'message': 'Unable to get projects'}), 500
    
    @app.route('/api/projects', methods=['POST'])
    @jwt_required()
    def create_project():
        """Create a new project"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)  # Convert back to int
            data = request.get_json()
            
            if not data or not data.get('title'):
                return jsonify({'message': 'Project title is required'}), 400
            
            from app.models import User, Project
            user = User.query.get(user_id)
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            project = Project(
                title=data['title'],
                description=data.get('description', ''),
                genre=data.get('genre'),
                target_audience=data.get('target_audience'),
                expected_length=data.get('expected_length', 'medium'),
                user_id=user_id
            )
            
            db.session.add(project)
            db.session.commit()
            
            return jsonify({
                'message': 'Project created successfully',
                'project': project.to_dict()
            }), 201
            
        except Exception as e:
            print(f"Create project error: {e}")
            return jsonify({'message': 'Unable to create project'}), 500

    @app.route('/api/projects/<int:project_id>', methods=['PUT'])
    @jwt_required()
    def update_project(project_id):
        """Update a specific project"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)
            data = request.get_json()
            
            from app.models import Project
            project = Project.query.filter_by(id=project_id, user_id=user_id).first()
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            
            # Update project fields
            if 'title' in data:
                project.title = data['title']
            if 'description' in data:
                project.description = data['description']
            if 'genre' in data:
                project.genre = data['genre']
            if 'target_audience' in data:
                project.target_audience = data['target_audience']
            if 'expected_length' in data:
                project.expected_length = data['expected_length']
            if 'status' in data:
                project.status = data['status']
            if 'target_word_count' in data:
                project.target_word_count = data['target_word_count']
            
            project.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Project updated successfully',
                'project': project.to_dict()
            }), 200
            
        except Exception as e:
            print(f"Update project error: {e}")
            return jsonify({'message': 'Unable to update project'}), 500

    @app.route('/api/projects/<project_id>', methods=['GET'])
    @jwt_required()
    def get_project(project_id):
        """Get a specific project"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)  # Convert back to int
            from app.models import Project
            
            project = Project.query.filter_by(id=project_id, user_id=user_id).first()
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            
            return jsonify({
                'project': project.to_dict()
            }), 200
            
        except Exception as e:
            print(f"Get project error: {e}")
            return jsonify({'message': 'Unable to get project'}), 500
    
    # ============================================================================
    # SCENE MANAGEMENT ROUTES
    # ============================================================================
    
    @app.route('/api/scenes', methods=['GET'])
    @jwt_required()
    def get_scenes():
        """Get scenes, optionally filtered by project_id"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)
            project_id = request.args.get('project_id')
            
            from app.models import Scene, Project
            
            # If project_id is specified, verify user owns the project
            if project_id:
                project = Project.query.filter_by(id=project_id, user_id=user_id).first()
                if not project:
                    return jsonify({'message': 'Project not found'}), 404
                
                scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.order_index).all()
            else:
                # Get all scenes for user's projects
                user_projects = Project.query.filter_by(user_id=user_id).all()
                project_ids = [p.id for p in user_projects]
                scenes = Scene.query.filter(Scene.project_id.in_(project_ids)).order_by(Scene.project_id, Scene.order_index).all()
            
            return jsonify({
                'scenes': [scene.to_dict() for scene in scenes],
                'count': len(scenes)
            }), 200
            
        except Exception as e:
            print(f"Get scenes error: {e}")
            return jsonify({'message': 'Unable to get scenes'}), 500
    
    @app.route('/api/scenes', methods=['POST'])
    @jwt_required()
    def create_scene():
        """Create a new scene"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)
            data = request.get_json()
            
            if not data or not data.get('title') or not data.get('project_id'):
                return jsonify({'message': 'Scene title and project_id are required'}), 400
            
            from app.models import Scene, Project
            
            # Verify user owns the project
            project = Project.query.filter_by(id=data['project_id'], user_id=user_id).first()
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            
            scene = Scene(
                title=data['title'],
                description=data.get('description', ''),
                content=data.get('content', ''),
                scene_type=data.get('scene_type', 'development'),
                emotional_intensity=data.get('emotional_intensity', 0.5),
                order_index=data.get('order_index', 0),
                word_count=len(data.get('content', '').split()) if data.get('content') else 0,
                project_id=data['project_id']
            )
            
            db.session.add(scene)
            db.session.commit()
            
            return jsonify({
                'message': 'Scene created successfully',
                'scene': scene.to_dict()
            }), 201
            
        except Exception as e:
            print(f"Create scene error: {e}")
            return jsonify({'message': 'Unable to create scene'}), 500
    
    @app.route('/api/scenes/<int:scene_id>', methods=['GET'])
    @jwt_required()
    def get_scene(scene_id):
        """Get a specific scene"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)
            
            from app.models import Scene, Project
            
            scene = Scene.query.get(scene_id)
            if not scene:
                return jsonify({'message': 'Scene not found'}), 404
            
            # Verify user owns the project this scene belongs to
            project = Project.query.filter_by(id=scene.project_id, user_id=user_id).first()
            if not project:
                return jsonify({'message': 'Scene not found'}), 404
            
            return jsonify({
                'scene': scene.to_dict()
            }), 200
            
        except Exception as e:
            print(f"Get scene error: {e}")
            return jsonify({'message': 'Unable to get scene'}), 500
    
    @app.route('/api/scenes/<int:scene_id>', methods=['PUT'])
    @jwt_required()
    def update_scene(scene_id):
        """Update a specific scene"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)
            data = request.get_json()
            
            from app.models import Scene, Project
            
            scene = Scene.query.get(scene_id)
            if not scene:
                return jsonify({'message': 'Scene not found'}), 404
            
            # Verify user owns the project this scene belongs to
            project = Project.query.filter_by(id=scene.project_id, user_id=user_id).first()
            if not project:
                return jsonify({'message': 'Scene not found'}), 404
            
            # Update scene fields
            if 'title' in data:
                scene.title = data['title']
            if 'description' in data:
                scene.description = data['description']
            if 'content' in data:
                scene.content = data['content']
                # Recalculate word count
                scene.word_count = len(data['content'].split()) if data['content'] else 0
            if 'scene_type' in data:
                scene.scene_type = data['scene_type']
            if 'emotional_intensity' in data:
                scene.emotional_intensity = data['emotional_intensity']
            if 'order_index' in data:
                scene.order_index = data['order_index']
            if 'status' in data:
                scene.status = data['status']
            
            scene.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Scene updated successfully',
                'scene': scene.to_dict()
            }), 200
            
        except Exception as e:
            print(f"Update scene error: {e}")
            return jsonify({'message': 'Unable to update scene'}), 500
    
    @app.route('/api/scenes/<int:scene_id>', methods=['DELETE'])
    @jwt_required()
    def delete_scene(scene_id):
        """Delete a specific scene"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)
            
            from app.models import Scene, Project
            
            scene = Scene.query.get(scene_id)
            if not scene:
                return jsonify({'message': 'Scene not found'}), 404
            
            # Verify user owns the project this scene belongs to
            project = Project.query.filter_by(id=scene.project_id, user_id=user_id).first()
            if not project:
                return jsonify({'message': 'Scene not found'}), 404
            
            db.session.delete(scene)
            db.session.commit()
            
            return jsonify({
                'message': 'Scene deleted successfully'
            }), 200
            
        except Exception as e:
            print(f"Delete scene error: {e}")
            return jsonify({'message': 'Unable to delete scene'}), 500

    # ============================================================================
    # AI ROUTES (Simulation Mode)
    # ============================================================================
    
    @app.route('/api/ai/status', methods=['GET'])
    def ai_status():
        """Get AI service status"""
        return jsonify({
            'ai_available': True,
            'simulation_mode': True,
            'models': ['claude-3-sonnet', 'gpt-4'],
            'status': 'ready'
        }), 200
    
    @app.route('/api/ai/analyze-idea', methods=['POST'])
    @jwt_required()
    def analyze_idea():
        """Analyze a story idea (simulation mode)"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)  # Convert back to int
            data = request.get_json()
            
            if not data or not data.get('idea_text'):
                return jsonify({'message': 'Idea text is required'}), 400
            
            # Simulate AI analysis
            idea_text = data['idea_text']
            
            # Simulated analysis response
            analysis = {
                'idea_text': idea_text,
                'analysis': {
                    'genre_suggestions': ['Fantasy', 'Adventure'],
                    'target_audience': 'Young Adult',
                    'estimated_length': 'Medium (50,000-80,000 words)',
                    'themes': ['Coming of age', 'Good vs. evil', 'Friendship'],
                    'plot_potential': 8.5,
                    'character_development': 7.8,
                    'originality_score': 8.2
                },
                'suggestions': [
                    'Consider developing the antagonist\'s motivation more deeply',
                    'Add supporting characters to enhance the world-building',
                    'Explore the magical system in more detail'
                ],
                'estimated_tokens_used': 1250,
                'simulation_mode': True
            }
            
            return jsonify(analysis), 200
            
        except Exception as e:
            print(f"Analyze idea error: {e}")
            return jsonify({'message': 'Unable to analyze idea'}), 500
    
    @app.route('/api/ai/create-project-from-idea', methods=['POST'])
    @jwt_required()
    def create_project_from_idea():
        """Create a project from an analyzed idea"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)  # Convert back to int
            data = request.get_json()
            
            if not data or not data.get('idea_text'):
                return jsonify({'message': 'Idea text is required'}), 400
            
            from app.models import User, Project
            user = User.query.get(user_id)
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            # Create project from idea
            project = Project(
                title=data.get('title', 'Untitled Story'),
                description=data['idea_text'],
                genre=data.get('preferred_genre', 'Fantasy'),
                target_audience=data.get('target_audience', 'Young Adult'),
                expected_length='medium',
                user_id=user_id
            )
            
            db.session.add(project)
            db.session.commit()
            
            return jsonify({
                'message': 'Project created from idea successfully',
                'project': project.to_dict(),
                'simulation_mode': True
            }), 201
            
        except Exception as e:
            print(f"Create project from idea error: {e}")
            return jsonify({'message': 'Unable to create project from idea'}), 500
    
    @app.route('/api/ai/projects/<int:project_id>/analyze-structure', methods=['POST'])
    @jwt_required()
    def analyze_project_structure(project_id):
        """Analyze project structure (simulation mode)"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)
            
            from app.models import User, Project
            
            # Verify user owns the project
            project = Project.query.filter_by(id=project_id, user_id=user_id).first()
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            
            # Simulated structure analysis
            structure_analysis = {
                'project_id': project_id,
                'project_title': project.title,
                'structure_analysis': {
                    'acts': {
                        'act_1': {
                            'title': 'Setup & Inciting Incident',
                            'target_word_count': int((project.target_word_count or 50000) * 0.25),
                            'current_word_count': 0,
                            'completion_percentage': 0,
                            'key_elements': ['Character introduction', 'World building', 'Inciting incident']
                        },
                        'act_2a': {
                            'title': 'Rising Action',
                            'target_word_count': int((project.target_word_count or 50000) * 0.25),
                            'current_word_count': 0,
                            'completion_percentage': 0,
                            'key_elements': ['Plot development', 'Character growth', 'Obstacles']
                        },
                        'act_2b': {
                            'title': 'Midpoint & Complications',
                            'target_word_count': int((project.target_word_count or 50000) * 0.25),
                            'current_word_count': 0,
                            'completion_percentage': 0,
                            'key_elements': ['Midpoint twist', 'Escalating stakes', 'Dark moment']
                        },
                        'act_3': {
                            'title': 'Climax & Resolution',
                            'target_word_count': int((project.target_word_count or 50000) * 0.25),
                            'current_word_count': 0,
                            'completion_percentage': 0,
                            'key_elements': ['Climax', 'Resolution', 'Character arc completion']
                        }
                    },
                    'pacing_analysis': {
                        'overall_pace': 'Well-balanced',
                        'action_scenes': 3,
                        'character_development_scenes': 5,
                        'plot_advancement_scenes': 4,
                        'recommended_improvements': [
                            'Add more character development in Act 2',
                            'Consider increasing tension before the midpoint',
                            'Strengthen the climax with higher stakes'
                        ]
                    },
                    'genre_compliance': {
                        'genre': project.genre,
                        'compliance_score': 8.5,
                        'missing_elements': ['Genre-specific tropes', 'Expected character archetypes'],
                        'strengths': ['Strong world-building', 'Compelling premise', 'Clear protagonist goals']
                    }
                },
                'recommendations': [
                    'Develop subplot to strengthen Act 2',
                    'Add foreshadowing for the climax in earlier acts',
                    'Consider expanding the resolution for better closure'
                ],
                'estimated_tokens_used': 2100,
                'simulation_mode': True
            }
            
            return jsonify(structure_analysis), 200
            
        except Exception as e:
            print(f"Analyze structure error: {e}")
            return jsonify({'message': 'Unable to analyze structure'}), 500
    
    @app.route('/api/ai/projects/<int:project_id>/suggest-scenes', methods=['POST'])
    @jwt_required()
    def suggest_scenes(project_id):
        """Suggest scenes for a project (simulation mode)"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)
            data = request.get_json() or {}
            
            from app.models import User, Project
            
            # Verify user owns the project
            project = Project.query.filter_by(id=project_id, user_id=user_id).first()
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            
            # Get number of scenes to suggest (default 5)
            scene_count = data.get('count', 5)
            scene_count = max(1, min(scene_count, 10))  # Limit between 1-10
            
            # Simulated scene suggestions
            scene_suggestions = []
            scene_types = ['opening', 'inciting', 'development', 'climax', 'resolution']
            scene_templates = [
                {
                    'title': 'Character Introduction',
                    'description': 'Introduce the protagonist in their ordinary world',
                    'scene_type': 'opening',
                    'emotional_intensity': 0.3,
                    'key_elements': ['Character establishment', 'World introduction', 'Normal routine']
                },
                {
                    'title': 'The Call to Adventure',
                    'description': 'The inciting incident that disrupts the protagonist\'s world',
                    'scene_type': 'inciting',
                    'emotional_intensity': 0.7,
                    'key_elements': ['Disruption', 'New opportunity/threat', 'Decision point']
                },
                {
                    'title': 'First Obstacle',
                    'description': 'The protagonist faces their first major challenge',
                    'scene_type': 'development',
                    'emotional_intensity': 0.6,
                    'key_elements': ['Challenge', 'Growth opportunity', 'Stakes introduction']
                },
                {
                    'title': 'Midpoint Revelation',
                    'description': 'A crucial discovery that changes everything',
                    'scene_type': 'development',
                    'emotional_intensity': 0.8,
                    'key_elements': ['Major revelation', 'Stakes escalation', 'Character growth']
                },
                {
                    'title': 'The Dark Moment',
                    'description': 'All seems lost - the lowest point for the protagonist',
                    'scene_type': 'development',
                    'emotional_intensity': 0.9,
                    'key_elements': ['Despair', 'Apparent failure', 'Internal struggle']
                },
                {
                    'title': 'Final Confrontation',
                    'description': 'The climactic battle or confrontation',
                    'scene_type': 'climax',
                    'emotional_intensity': 1.0,
                    'key_elements': ['Ultimate challenge', 'Character transformation', 'Resolution of conflict']
                },
                {
                    'title': 'New Beginning',
                    'description': 'The aftermath and new status quo',
                    'scene_type': 'resolution',
                    'emotional_intensity': 0.4,
                    'key_elements': ['Closure', 'Character growth shown', 'Future implications']
                }
            ]
            
            # Select suggested scenes
            for i in range(min(scene_count, len(scene_templates))):
                suggestion = scene_templates[i].copy()
                suggestion['suggested_order'] = i + 1
                suggestion['estimated_word_count'] = 1000 + (i * 200)  # Varying lengths
                scene_suggestions.append(suggestion)
            
            response = {
                'project_id': project_id,
                'project_title': project.title,
                'project_genre': project.genre,
                'suggested_scenes': scene_suggestions,
                'scene_count': len(scene_suggestions),
                'suggestions': [
                    'Consider the pacing between scenes',
                    'Ensure each scene advances plot or character development',
                    'Balance action and dialogue scenes',
                    f'These scenes fit well with the {project.genre} genre'
                ],
                'estimated_tokens_used': 1800,
                'simulation_mode': True
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            print(f"Suggest scenes error: {e}")
            return jsonify({'message': 'Unable to suggest scenes'}), 500
    
    # ============================================================================
    # ANALYTICS ROUTES
    # ============================================================================
    
    @app.route('/api/analytics/dashboard', methods=['GET'])
    @jwt_required()
    def analytics_dashboard():
        """Get user analytics dashboard data"""
        try:
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)  # Convert back to int
            from app.models import User, Project
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            # Calculate analytics
            total_projects = user.projects.count()
            active_projects = user.projects.filter_by(status='active').count()
            total_words = sum(p.current_word_count or 0 for p in user.projects.all())
            
            analytics = {
                'user_stats': {
                    'total_projects': total_projects,
                    'active_projects': active_projects,
                    'completed_projects': user.projects.filter_by(status='completed').count(),
                    'total_words_written': total_words,
                    'tokens_used': user.tokens_used,
                    'tokens_remaining': user.get_remaining_tokens(),
                    'account_age_days': (datetime.utcnow() - user.created_at).days
                },
                'writing_progress': {
                    'words_this_week': total_words,  # Simplified for demo
                    'words_this_month': total_words,
                    'average_words_per_project': total_words // max(total_projects, 1),
                    'most_productive_genre': 'Fantasy'  # Simplified
                },
                'recent_activity': [
                    {
                        'type': 'project_created',
                        'title': 'Recent Project Activity',
                        'timestamp': datetime.utcnow().isoformat(),
                        'description': f'You have {total_projects} active projects'
                    }
                ]
            }
            
            return jsonify(analytics), 200
            
        except Exception as e:
            print(f"Analytics error: {e}")
            return jsonify({'message': 'Unable to get analytics'}), 500
    
    # ============================================================================
    # DEMO ROUTE
    # ============================================================================
    
    @app.route('/demo')
    def demo_info():
        """Demo information endpoint"""
        return jsonify({
            'message': 'ALVIN Demo Information',
            'demo_account': {
                'email': 'demo@alvin.ai',
                'password': 'demo123'
            },
            'api_endpoints': {
                'health': '/health',
                'api_info': '/api',
                'register': '/api/auth/register',
                'login': '/api/auth/login',
                'profile': '/api/auth/profile',
                'verify_token': '/api/auth/verify',
                'projects': '/api/projects',
                'update_project': '/api/projects/{id}',
                'scenes': '/api/scenes',
                'create_scene': '/api/scenes',
                'update_scene': '/api/scenes/{id}',
                'ai_status': '/api/ai/status',
                'analyze_idea': '/api/ai/analyze-idea',
                'create_from_idea': '/api/ai/create-project-from-idea',
                'analyze_structure': '/api/ai/projects/{id}/analyze-structure',
                'suggest_scenes': '/api/ai/projects/{id}/suggest-scenes',
                'analytics': '/api/analytics/dashboard',
                'debug_headers': '/api/debug/headers',
                'debug_decode_token': '/api/debug/decode-token'
            },
            'features': {
                'authentication': 'JWT tokens',
                'ai_simulation': 'Enabled',
                'project_management': 'Full CRUD',
                'scene_management': 'Full CRUD',
                'advanced_ai': 'Structure analysis & scene suggestions',
                'analytics': 'User dashboard'
            },
            'status': 'ready'
        })
    
    # ============================================================================
    # ERROR HANDLERS
    # ============================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found',
            'available_endpoints': {
                'home': '/',
                'health': '/health',
                'api_info': '/api',
                'demo': '/demo',
                'register': '/api/auth/register',
                'login': '/api/auth/login'
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    # ============================================================================
    # JWT ERROR HANDLERS
    # ============================================================================
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"🔍 JWT Token expired - Header: {jwt_header}, Payload: {jwt_payload}")
        return jsonify({'message': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"🔍 JWT Invalid token error: {error}")
        print(f"🔍 JWT Error type: {type(error)}")
        return jsonify({'message': 'Invalid token', 'error_details': str(error)}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"🔍 JWT Missing token error: {error}")
        return jsonify({'message': 'Authorization token is required'}), 401
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        print(f"🔍 JWT Blocklist check - Header: {jwt_header}, Payload: {jwt_payload}")
        return False  # For now, don't check blocklist
    
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        print(f"🔍 JWT Adding claims for identity: {identity} (type: {type(identity)})")
        # identity is now a string, convert to int to get user_id
        user_id = int(identity)
        return {'user_id': user_id}
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        print(f"🔍 JWT Identity lookup for user: {user} (type: {type(user)})")
        # If user is an integer (user ID), convert to string
        if isinstance(user, int):
            return str(user)
        # If user is already a string, return as-is
        return user
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]  # This will be a string now
        user_id = int(identity)  # Convert to int for database lookup
        print(f"🔍 JWT User lookup for identity: {identity} (converted to int: {user_id})")
        from app.models import User
        return User.query.filter_by(id=user_id).one_or_none()
    
    # ============================================================================
    # ADDITIONAL API ROUTES
    # ============================================================================
    
    @app.route('/api/status/db', methods=['GET'])
    def database_status():
        """Check database connection status"""
        try:
            from app.models import User
            User.query.first()
            return jsonify({'database_connected': True}), 200
        except Exception as e:
            print(f"Database check error: {e}")
            return jsonify({'database_connected': False, 'error': str(e)}), 500
    
    @app.route('/api/status/redis', methods=['GET'])
    def redis_status():
        """Check Redis connection status (simulated)"""
        return jsonify({'redis_connected': True}), 200
    
    # ============================================================================
    # SOCKET.IO EVENTS
    # ============================================================================
    
    @socketio.on('connect')
    def handle_connect():
        print('🔌 Client connected to ALVIN backend')
        return {'status': 'connected', 'message': 'Welcome to ALVIN!'}
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('🔌 Client disconnected from ALVIN backend')
    
    print("=" * 60)
    print("🎭 ALVIN Backend Ready with Complete API!")
    print("🌐 API available at: http://localhost:5000")
    print("🔐 Auth endpoints: /api/auth/register, /api/auth/login")
    print("🤖 AI endpoints: /api/ai/analyze-idea, /api/ai/create-project-from-idea")
    print("🧠 Advanced AI: /api/ai/projects/{id}/analyze-structure, suggest-scenes")
    print("📊 Analytics: /api/analytics/dashboard")
    print("📝 Projects: /api/projects (GET, POST, PUT)")
    print("🎬 Scenes: /api/scenes (GET, POST, PUT, DELETE)")
    print("🎪 Demo: demo@alvin.ai / demo123")
    print("=" * 60)
    
    return app