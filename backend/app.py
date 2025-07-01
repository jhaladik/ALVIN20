# backend/app.py
"""
ALVIN Backend - Main Application File
This file creates the Flask application instance and handles initialization
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

# Import the application factory and database
from app import create_app, db, initialize_database

def create_application():
    """Create and configure the Flask application"""
    try:
        # Create Flask app
        app = create_app()
        
        # Initialize database with app context
        with app.app_context():
            success = initialize_database()
            if success:
                print("✅ Application initialized successfully")
            else:
                print("⚠️ Application started but database initialization had issues")
        
        return app
    
    except Exception as e:
        print(f"❌ Failed to create application: {str(e)}")
        raise

# Create the application instance
application = create_application()

# For WSGI servers (like Gunicorn)
app = application

if __name__ == '__main__':
    # Development server
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Starting ALVIN Backend on {host}:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    application.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )