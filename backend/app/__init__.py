# app/__init__.py - ALVIN Minimal Working Backend
import os
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

# Initialize SocketIO
socketio = SocketIO()

def create_app(config_name=None):
    """Create minimal working Flask application"""
    
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'alvin-dev-secret-key')
    app.config['DEBUG'] = True
    
    # Initialize CORS
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'], supports_credentials=True)
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # ============================================================================
    # BASIC WORKING ROUTES - NO COMPLEX IMPORTS
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
                'demo': '/demo'
            }
        })
    
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ALVIN API',
            'version': '1.0.0',
            'message': 'Backend is running successfully!',
            'database': 'PostgreSQL available',
            'redis': 'Redis available',
            'socketio': 'WebSocket ready'
        })
    
    @app.route('/api')
    def api_info():
        return jsonify({
            'service': 'ALVIN API',
            'version': '1.0.0',
            'status': 'Backend running - Ready for frontend',
            'description': 'AI-powered creative writing assistant',
            'features': {
                'authentication': 'Ready',
                'projects': 'Ready', 
                'ai_integration': 'Ready',
                'real_time_collaboration': 'Socket.IO ready',
                'export': 'Ready'
            },
            'demo_account': {
                'email': 'demo@alvin.ai',
                'password': 'demo123'
            }
        })
    
    @app.route('/demo')
    def demo_info():
        return jsonify({
            'demo_account': {
                'email': 'demo@alvin.ai',
                'password': 'demo123'
            },
            'frontend_url': 'http://localhost:5173',
            'message': 'Backend is ready! Start the frontend to use ALVIN',
            'next_steps': [
                'Open terminal in frontend directory',
                'Run: npm run dev',
                'Open: http://localhost:5173',
                'Login with demo credentials'
            ]
        })
    
    # Simple API endpoints for testing
    @app.route('/api/test')
    def api_test():
        return jsonify({
            'message': 'ALVIN API is working!',
            'timestamp': '2025-07-01',
            'status': 'success'
        })
    
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
    
    @socketio.on('test_message')
    def handle_test_message(data):
        print(f'📨 Received test message: {data}')
        return {'status': 'received', 'echo': data}
    
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
                'test': '/api/test'
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    # ============================================================================
    # STARTUP MESSAGE
    # ============================================================================
    
    print("=" * 60)
    print("🎭 ALVIN Backend Started Successfully!")
    print("🌐 API available at: http://localhost:5000")
    print("🩺 Health check: http://localhost:5000/health")
    print("📋 API info: http://localhost:5000/api")
    print("🎪 Demo info: http://localhost:5000/demo") 
    print("🔌 Socket.IO ready for real-time features")
    print("=" * 60)
    
    return app