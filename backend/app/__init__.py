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

# JWT Token Blacklist
blacklisted_tokens = set()

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()
jwt = JWTManager()

def register_blueprints(app):
    """Register all application blueprints with proper error handling"""
    print("\n🔧 Registering blueprints...")
    
    # Blueprint configuration
    blueprints = [
        ('app.routes.auth', 'auth_bp', '/api/auth', 'Authentication'),
        ('app.routes.projects', 'projects_bp', '/api/projects', 'Project Management'),  
        ('app.routes.scenes', 'scenes_bp', '/api/scenes', 'Scene Management'),
        ('app.routes.objects', 'objects_bp', '/api/objects', 'Story Objects'),
        ('app.routes.analytics', 'analytics_bp', '/api/analytics', 'Analytics'),
        ('app.routes.ai', 'ai_bp', '/api/ai', 'AI Operations'),
        ('app.routes.collaboration', 'collaboration_bp', '/api/collaboration', 'Collaboration'),
        ('app.routes.billing', 'billing_bp', '/api/billing', 'Billing')
    ]
    
    registered = 0
    failed = 0
    
    for module_name, blueprint_name, url_prefix, description in blueprints:
        try:
            print(f"   📦 Importing {module_name}...")
            
            # Import the module
            import importlib
            module = importlib.import_module(module_name)
            
            # Get the blueprint
            if hasattr(module, blueprint_name):
                blueprint = getattr(module, blueprint_name)
                
                # Register the blueprint with URL prefix
                app.register_blueprint(blueprint, url_prefix=url_prefix)
                
                registered += 1
                print(f"   ✅ {blueprint_name}: {description}")
                print(f"      └─ Registered at {url_prefix}")
                
            else:
                raise ImportError(f"Blueprint '{blueprint_name}' not found in {module_name}")
                
        except Exception as e:
            failed += 1
            print(f"   ❌ {blueprint_name}: {str(e)}")
            app.logger.error(f"Blueprint registration failed: {module_name} - {e}")
    
    print(f"\n📊 Blueprint Registration Summary:")
    print(f"   ✅ Successfully registered: {registered}/8 blueprints")
    print(f"   ❌ Failed registrations: {failed}/8 blueprints")
    
    if failed == 0:
        print(f"   🎉 ALL BLUEPRINTS REGISTERED SUCCESSFULLY!")
    
    print(f"✅ Blueprint registration complete!\n")
    
    return {'registered': registered, 'failed': failed}

# Additional helper function for selective registration during development
def register_blueprints_selective(app, enabled_blueprints=None):
    """
    Register only specific blueprints for development/testing.
    
    Args:
        app: Flask application instance
        enabled_blueprints: List of blueprint names to register
                          If None, registers all blueprints
    
    Example:
        # Register only core blueprints for testing
        register_blueprints_selective(app, ['auth', 'projects'])
    """
    if enabled_blueprints is None:
        return register_blueprints(app)
    
    print(f"\n🔧 Selective blueprint registration: {enabled_blueprints}")
    
    # Use the same registry but filter by enabled list
    # ... (implementation similar to register_blueprints but with filtering)
    
    return register_blueprints(app)  # For now, fallback to full registration

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

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        '''Check if a token has been blacklisted'''
        jti = jwt_payload['jti']
        return jti in blacklisted_tokens

    # CORS configuration - ONLY THIS LINE MATTERS:
    CORS(app, 
         origins=['http://localhost:3000', 'http://localhost:5173'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    socketio.init_app(app, 
        cors_allowed_origins="*",
        async_mode='threading',
        logger=False,
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    
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

    register_blueprints(app)

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
   
    # ============================================================================
    # PROJECT ROUTES
    # ============================================================================
  
    # ============================================================================
    # SCENE MANAGEMENT ROUTES
    # ============================================================================
    
    # ============================================================================
    # AI ROUTES (Simulation Mode)
    # ============================================================================
  
    # ============================================================================
    # ANALYTICS ROUTES
    # ============================================================================
  
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
                'debug_decode_token': '/api/debug/decode-token',
                'billing': '/api/billing',
                'billing' : '/api/billing/subscription',
                'analytics': '/api/analytics',
                'recent-activity' : '/api/analytics'
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