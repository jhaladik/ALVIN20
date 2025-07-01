#!/usr/bin/env python3
"""
ALVIN Backend Entry Point
Fixed version that properly initializes the Flask app with all blueprints
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variables before importing Flask
os.environ.setdefault('FLASK_CONFIG', 'development')
os.environ.setdefault('FLASK_ENV', 'development')

try:
    from app import create_app, socketio, db
    from app.models import User, Project, Scene, StoryObject
    
    # Create the Flask application
    app = create_app()
    
    # Create database tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Create a demo user if it doesn't exist
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
            else:
                print("✅ Demo user already exists: demo@alvin.ai / demo123")
                
        except Exception as e:
            print(f"⚠️ Database setup warning: {e}")
    
    @app.route('/demo')
    def demo_info():
        """Demo information endpoint"""
        return {
            'message': 'ALVIN Demo Information',
            'demo_account': {
                'email': 'demo@alvin.ai',
                'password': 'demo123'
            },
            'api_endpoints': {
                'health': '/health',
                'api_info': '/api',
                'auth': '/api/auth',
                'projects': '/api/projects',
                'scenes': '/api/scenes',
                'ai': '/api/ai'
            },
            'status': 'ready'
        }
    
    if __name__ == '__main__':
        print("🎭 Starting ALVIN Backend...")
        print("=" * 60)
        
        # Print configuration info
        config_name = os.environ.get('FLASK_CONFIG', 'development')
        print(f"📋 Configuration: {config_name}")
        print(f"🗄️ Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
        print(f"🔧 Debug Mode: {app.config.get('DEBUG', False)}")
        print(f"🤖 AI Simulation: {os.environ.get('AI_SIMULATION_MODE', 'false')}")
        
        # Check if running in Docker
        in_docker = os.path.exists('/.dockerenv')
        host = '0.0.0.0' if in_docker else '127.0.0.1'
        
        try:
            print("=" * 60)
            print(" * Serving Flask app 'app'")
            print(" * Debug mode: on")
            print("=" * 60)
            print("🎭 ALVIN Backend Started Successfully!")
            print(f"🌐 API available at: http://localhost:5000")
            print(f"🩺 Health check: http://localhost:5000/health")
            print(f"📋 API info: http://localhost:5000/api")
            print(f"🎪 Demo info: http://localhost:5000/demo")
            print(f"🔌 Socket.IO ready for real-time features")
            print("=" * 60)
            
            # Start the server
            socketio.run(
                app,
                host=host,
                port=5000,
                debug=True,
                allow_unsafe_werkzeug=True,
                use_reloader=True,
                log_output=True
            )
            
        except KeyboardInterrupt:
            print("\n🛑 ALVIN Backend stopped by user")
        except Exception as e:
            print(f"\n💥 Failed to start ALVIN Backend: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

except ImportError as e:
    print(f"💥 Import Error: {e}")
    print("\n🔧 Possible solutions:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Check if you're in the backend/ directory")
    print("3. Run setup: python setup.py")
    sys.exit(1)
except Exception as e:
    print(f"💥 Startup Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)