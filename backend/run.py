#!/usr/bin/env python3
"""
ALVIN Backend Entry Point
Complete version with authentication and database integration
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
    from app import create_app, socketio
    
    # Create the Flask application
    app = create_app()
    
    if __name__ == '__main__':
        print("🎭 Starting ALVIN Backend...")
        print("=" * 60)
        
        # Print configuration info
        config_name = os.environ.get('FLASK_CONFIG', 'development')
        print(f"📋 Configuration: {config_name}")
        print(f"🗄️ Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
        print(f"🔧 Debug Mode: {app.config.get('DEBUG', False)}")
        print(f"🔐 JWT Enabled: {'JWT_SECRET_KEY' in app.config}")
        
        # Check if running in Docker
        in_docker = os.path.exists('/.dockerenv')
        host = '0.0.0.0' if in_docker else '127.0.0.1'
        
        try:
            print("=" * 60)
            print("🎭 ALVIN Backend Started Successfully!")
            print(f"🌐 API available at: http://localhost:5000")
            print(f"🩺 Health check: http://localhost:5000/health")
            print(f"📋 API info: http://localhost:5000/api")
            print(f"🎪 Demo info: http://localhost:5000/demo")
            print(f"🔐 Auth: /api/auth/register, /api/auth/login")
            print(f"🔌 Socket.IO ready for real-time features")
            print("=" * 60)
            
            # Start the server
            socketio.run(
                app,
                host=host,
                port=5000,
                debug=True,
                allow_unsafe_werkzeug=True,
                use_reloader=False,
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
    print("3. Make sure models/__init__.py has all models defined")
    sys.exit(1)
except Exception as e:
    print(f"💥 Startup Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)