#!/usr/bin/env python3
# setup.py - ALVIN Setup and Installation Script
import os
import sys
import subprocess
import sqlite3
from datetime import datetime, timedelta

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🎭 ALVIN - AI-Powered Creative Writing Assistant")
    print("   Setup and Installation Script")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def create_environment_file():
    """Create .env file with default configuration"""
    print("\n🔧 Creating environment configuration...")
    
    env_file = '.env'
    if os.path.exists(env_file):
        response = input(f"   {env_file} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping environment file creation")
            return
    
    env_content = f"""# ALVIN Environment Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Flask Configuration
FLASK_CONFIG=development
SECRET_KEY=alvin-dev-secret-{datetime.now().strftime('%Y%m%d')}-change-in-production
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///alvin_dev.db

# JWT Configuration
JWT_SECRET_KEY=jwt-secret-{datetime.now().strftime('%Y%m%d')}-change-in-production

# Claude AI Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
AI_SIMULATION_MODE=true
DEFAULT_CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Rate Limiting
CLAUDE_MAX_REQUESTS_PER_MINUTE=100
CLAUDE_MAX_TOKENS_PER_REQUEST=4000

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Redis Configuration (optional for development)
REDIS_URL=redis://localhost:6379/0

# Email Configuration (optional)
MAIL_SERVER=
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=

# Stripe Configuration (for billing)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Development Settings
PAYMENT_SIMULATION_MODE=true
LOG_LEVEL=INFO

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Environment file created: {env_file}")
    print("   📝 Please edit the .env file and add your API keys")

def setup_database():
    """Initialize the database"""
    print("\n🗄️ Setting up database...")
    
    try:
        # Set environment for database setup first
        os.environ['FLASK_CONFIG'] = 'development'
        
        # Import app factory
        from app import create_app, db
        
        # Create app instance
        app = create_app('development')
        
        # Import models only within app context
        with app.app_context():
            # Import models after app context is created
            from app.models import User, Project, Scene, StoryObject, BillingPlan, UserSubscription
            
            print("   Creating database tables...")
            db.create_all()
            
            # Create default billing plans
            print("   Creating default billing plans...")
            create_default_billing_plans(db)
            
            # Create demo user if requested
            create_demo = input("   Create demo user? (Y/n): ")
            if create_demo.lower() != 'n':
                create_demo_user(db)
            
            print("✅ Database setup completed")
            
    except ImportError as e:
        print(f"❌ Failed to import application modules: {e}")
        print("   Make sure dependencies are installed first")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_default_billing_plans(db):
    """Create default billing plans"""
    from app.models import BillingPlan
    
    plans = [
        {
            'name': 'free',
            'display_name': 'Free',
            'description': 'Perfect for getting started with AI writing assistance',
            'price': 0.00,
            'currency': 'USD',
            'billing_interval': 'month',
            'token_limit': 1000,
            'features': {
                'projects': 3,
                'ai_operations': True,
                'export_formats': ['txt', 'html'],
                'collaboration': False,
                'priority_support': False
            },
            'is_public': True,
            'is_active': True
        },
        {
            'name': 'pro',
            'display_name': 'Pro',
            'description': 'Advanced features for serious writers',
            'price': 19.99,
            'currency': 'USD',
            'billing_interval': 'month',
            'token_limit': 10000,
            'features': {
                'projects': 25,
                'ai_operations': True,
                'export_formats': ['txt', 'html', 'pdf', 'docx'],
                'collaboration': True,
                'priority_support': True,
                'advanced_analytics': True
            },
            'is_public': True,
            'is_active': True
        },
        {
            'name': 'enterprise',
            'display_name': 'Enterprise',
            'description': 'For teams and professional writers',
            'price': 49.99,
            'currency': 'USD',
            'billing_interval': 'month',
            'token_limit': 50000,
            'features': {
                'projects': 100,
                'ai_operations': True,
                'export_formats': ['txt', 'html', 'pdf', 'docx'],
                'collaboration': True,
                'priority_support': True,
                'advanced_analytics': True,
                'team_management': True,
                'custom_integrations': True
            },
            'is_public': True,
            'is_active': True
        }
    ]
    
    for plan_data in plans:
        existing_plan = BillingPlan.query.filter_by(name=plan_data['name']).first()
        if not existing_plan:
            plan = BillingPlan(**plan_data)
            db.session.add(plan)
    
    db.session.commit()

def create_demo_user(db):
    """Create a demo user for testing"""
    from app.models import User, Project, Scene
    
    # Check if demo user already exists
    demo_user = User.query.filter_by(email='demo@alvin.ai').first()
    if demo_user:
        print("   Demo user already exists")
        return
    
    # Create demo user
    demo_user = User(
        username='demo',
        email='demo@alvin.ai',
        full_name='Demo User',
        plan='pro',
        tokens_limit=10000,
        tokens_used=150,
        bio='A demo user for testing ALVIN features'
    )
    demo_user.set_password('demo123')
    db.session.add(demo_user)
    db.session.commit()
    
    # Create demo project
    demo_project = Project(
        id=f"demo-project-{datetime.now().strftime('%Y%m%d')}",
        title="Mystery at Moonlight Manor",
        description="A thrilling mystery novel set in a Victorian mansion",
        genre="Mystery",
        current_phase="expand",
        target_word_count=80000,
        current_word_count=2500,
        status="active",
        tone="suspenseful",
        target_audience="Adult",
        original_idea="A detective investigates mysterious disappearances at an old manor house",
        user_id=demo_user.id
    )
    db.session.add(demo_project)
    db.session.commit()
    
    # Create demo scenes
    demo_scenes = [
        {
            'title': 'The Arrival',
            'description': 'Detective Sarah Mills arrives at Moonlight Manor on a foggy evening',
            'content': '<p>The gravel crunched under Detective Sarah Mills\' feet as she approached the imposing silhouette of Moonlight Manor. Through the swirling fog, she could make out the Gothic windows staring down at her like hollow eyes.</p><p>"Another missing person case," she muttered, pulling her coat tighter against the autumn chill.</p>',
            'scene_type': 'opening',
            'emotional_intensity': 0.6,
            'order_index': 1
        },
        {
            'title': 'The Mysterious Host',
            'description': 'Sarah meets Lord Blackwood, the enigmatic owner of the manor',
            'content': '<p>Lord Blackwood emerged from the shadows of the grand entrance hall, his silver hair gleaming in the candlelight. His smile was warm, but his eyes remained cold and calculating.</p><p>"Detective Mills, I presume? I do hope you can solve this... unfortunate situation quickly."</p>',
            'scene_type': 'development',
            'emotional_intensity': 0.7,
            'order_index': 2
        },
        {
            'title': 'The Hidden Room',
            'description': 'Sarah discovers a secret room with evidence of the missing persons',
            'content': '<p>Behind the false wall, Sarah\'s flashlight revealed a room that time had forgotten. Personal belongings lay scattered across dusty tables - a watch, a locket, a pair of reading glasses. Each item told the story of someone who had vanished without a trace.</p>',
            'scene_type': 'climax',
            'emotional_intensity': 0.9,
            'order_index': 3
        }
    ]
    
    for i, scene_data in enumerate(demo_scenes):
        scene = Scene(
            **scene_data,
            project_id=demo_project.id,
            word_count=len(scene_data['content'].split()) if scene_data['content'] else 0
        )
        db.session.add(scene)
    
    db.session.commit()
    
    print("✅ Demo user created:")
    print("   📧 Email: demo@alvin.ai")
    print("   🔑 Password: demo123")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        'uploads',
        'logs',
        'exports',
        'backups'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Created: {directory}/")
        else:
            print(f"   📁 Exists: {directory}/")

def setup_logging():
    """Set up logging configuration"""
    print("\n📝 Setting up logging...")
    
    log_config = """# logging.conf - ALVIN Logging Configuration
[loggers]
keys=root,alvin

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_alvin]
level=INFO
handlers=consoleHandler,fileHandler
qualname=alvin
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=detailedFormatter
args=('logs/alvin.log',)

[formatter_simpleFormatter]
format=%(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""
    
    with open('logging.conf', 'w') as f:
        f.write(log_config)
    
    print("✅ Logging configuration created")

def run_tests():
    """Run basic tests to verify setup"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        from app import create_app, db
        from app.models import User, Project
        from app.services.claude_service import ClaudeService
        from app.services.token_service import TokenService
        
        print("   ✅ All imports successful")
        
        # Test app creation
        app = create_app('testing')
        print("   ✅ App creation successful")
        
        # Test Claude service initialization
        with app.app_context():
            claude_service = ClaudeService()
            token_service = TokenService()
            print("   ✅ Services initialization successful")
        
        print("✅ All tests passed")
        
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return False
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 ALVIN Setup Complete!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Edit .env file and add your Anthropic API key")
    print("2. Start the development server:")
    print("   python run.py")
    print("\n3. Start the frontend (in another terminal):")
    print("   cd frontend")
    print("   npm install")
    print("   npm run dev")
    print("\n4. Open your browser and go to:")
    print("   http://localhost:5173")
    print("\n5. Login with demo account:")
    print("   📧 Email: demo@alvin.ai")
    print("   🔑 Password: demo123")
    print("\n🔗 Useful Commands:")
    print("   python force_db_init.py  # Reset database")
    print("   python -m pytest         # Run tests")
    print("   python setup.py --help   # This help")
    print("\n📚 Documentation:")
    print("   API: http://localhost:5000/api")
    print("   Health: http://localhost:5000/health")
    print("=" * 60)

def main():
    """Main setup function"""
    print_banner()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("ALVIN Setup Script")
            print("\nUsage: python setup.py [options]")
            print("\nOptions:")
            print("  --help, -h    Show this help message")
            print("  --skip-deps   Skip dependency installation")
            print("  --skip-db     Skip database setup")
            print("  --skip-test   Skip running tests")
            sys.exit(0)
    
    skip_deps = '--skip-deps' in sys.argv
    skip_db = '--skip-db' in sys.argv
    skip_test = '--skip-test' in sys.argv
    
    try:
        # Setup steps
        check_python_version()
        
        if not skip_deps:
            install_dependencies()
        
        create_environment_file()
        create_directories()
        setup_logging()
        
        if not skip_db:
            setup_database()
        
        if not skip_test:
            if not run_tests():
                print("\n⚠️  Setup completed with test failures")
                print("   The application should still work, but please check the errors above")
        
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()