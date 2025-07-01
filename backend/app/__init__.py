# app/__init__.py - ALVIN Application Factory
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()

# Blacklisted tokens storage (in production, use Redis)
blacklisted_tokens = set()

def create_app(config_name=None):
    """Application factory pattern"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Initialize SocketIO
    socketio.init_app(
        app,
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'],
        async_mode=app.config['SOCKETIO_ASYNC_MODE']
    )
    
    # Import models after db is initialized
    # This ensures models are registered with the correct db instance
    from app import models
    
    # JWT Configuration
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if JWT token is blacklisted"""
        return jwt_payload['jti'] in blacklisted_tokens
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired tokens"""
        return jsonify({
            'error': 'Token has expired',
            'message': 'Please log in again'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid tokens"""
        return jsonify({
            'error': 'Invalid token',
            'message': 'Token is invalid or malformed'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing tokens"""
        return jsonify({
            'error': 'Authorization token required',
            'message': 'Please log in to access this resource'
        }), 401
    
    # Register blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'ALVIN Backend',
            'version': '1.0.0'
        })
    
    @app.route('/api')
    def api_info():
        """API information endpoint"""
        return jsonify({
            'message': 'ALVIN API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'projects': '/api/projects',
                'ai': '/api/ai',
                'health': '/health'
            }
        })
    
    return app

def register_blueprints(app):
    """Register application blueprints"""
    try:
        from app.routes.auth import auth_bp
        from app.routes.projects import projects_bp
        from app.routes.ai import ai_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(projects_bp, url_prefix='/api/projects')
        app.register_blueprint(ai_bp, url_prefix='/api/ai')
        
    except ImportError as e:
        # If blueprints don't exist yet, continue without them
        print(f"Warning: Could not import blueprints: {e}")
        pass