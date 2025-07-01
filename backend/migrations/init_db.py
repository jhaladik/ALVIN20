# backend/migrations/init_db.py
"""
ALVIN Backend - Database Migration and Initialization Script
Handles database schema creation, upgrades, and data seeding
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app, db, User, Project, Scene, StoryObject, TokenUsageLog
from app import create_demo_user, create_demo_data

def create_database_schema():
    """Create all database tables"""
    try:
        print("🔄 Creating database schema...")
        db.create_all()
        print("✅ Database schema created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create database schema: {str(e)}")
        return False

def drop_database_schema():
    """Drop all database tables"""
    try:
        print("🔄 Dropping database schema...")
        db.drop_all()
        print("✅ Database schema dropped successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to drop database schema: {str(e)}")
        return False

def seed_initial_data():
    """Seed database with initial data"""
    try:
        print("🔄 Seeding initial data...")
        
        # Create demo user
        demo_user = create_demo_user()
        
        # Create demo projects and scenes
        create_demo_data()
        
        print("✅ Initial data seeded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to seed initial data: {str(e)}")
        return False

def create_admin_user():
    """Create admin user"""
    try:
        print("🔄 Creating admin user...")
        
        admin_email = "admin@alvin.ai"
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            admin_user = User(
                username='admin',
                email=admin_email,
                full_name='Admin User',
                plan='admin',
                is_active=True,
                is_admin=True,
                tokens_limit=10000,
                preferences={
                    'theme': 'dark',
                    'notifications': {'email': True, 'push': True},
                    'privacy': {'profile_public': False}
                }
            )
            admin_user.set_password('admin123')  # Change in production!
            db.session.add(admin_user)
            db.session.commit()
            print(f"✅ Admin user created: {admin_email} / admin123")
        else:
            print("✅ Admin user already exists")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create admin user: {str(e)}")
        return False

def backup_database():
    """Create database backup"""
    try:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(backend_dir) / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        # For SQLite databases
        if 'sqlite' in str(db.engine.url):
            import shutil
            db_path = str(db.engine.url).replace('sqlite:///', '')
            backup_path = backup_dir / f'alvin_backup_{timestamp}.db'
            shutil.copy2(db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
        else:
            print("⚠️ Backup not implemented for this database type")
        
        return True
    except Exception as e:
        print(f"❌ Failed to backup database: {str(e)}")
        return False

def verify_database():
    """Verify database integrity"""
    try:
        print("🔄 Verifying database integrity...")
        
        # Check if tables exist (FIXED METHOD)
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['users', 'projects', 'scenes', 'story_objects', 'token_usage_logs']
        
        missing_tables = [table for table in expected_tables if table not in tables]
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        # Check if demo user exists
        demo_user = User.query.filter_by(email='demo@alvin.ai').first()
        if not demo_user:
            print("⚠️ Demo user not found")
        
        # Check record counts
        user_count = User.query.count()
        project_count = Project.query.count()
        scene_count = Scene.query.count()
        
        print(f"📊 Database statistics:")
        print(f"   Users: {user_count}")
        print(f"   Projects: {project_count}")
        print(f"   Scenes: {scene_count}")
        
        print("✅ Database verification completed")
        return True
    except Exception as e:
        print(f"❌ Database verification failed: {str(e)}")
        return False

def reset_database():
    """Reset database (drop and recreate)"""
    try:
        print("🔄 Resetting database...")
        
        # Drop all tables
        if not drop_database_schema():
            return False
        
        # Create all tables
        if not create_database_schema():
            return False
        
        # Seed initial data
        if not seed_initial_data():
            return False
        
        # Create admin user
        if not create_admin_user():
            return False
        
        print("✅ Database reset completed successfully")
        return True
    except Exception as e:
        print(f"❌ Database reset failed: {str(e)}")
        return False

def upgrade_database():
    """Upgrade database schema (for future migrations)"""
    try:
        print("🔄 Upgrading database...")
        
        # Add future migration logic here
        # For now, just verify the current schema
        if not verify_database():
            return False
        
        print("✅ Database upgrade completed")
        return True
    except Exception as e:
        print(f"❌ Database upgrade failed: {str(e)}")
        return False

def main():
    """Main migration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ALVIN Database Migration Tool')
    parser.add_argument('command', choices=[
        'init', 'reset', 'seed', 'verify', 'backup', 'upgrade', 'create-admin'
    ], help='Migration command to execute')
    
    args = parser.parse_args()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🎭 ALVIN Database Migration Tool")
        print("=" * 60)
        
        success = False
        
        if args.command == 'init':
            print("Initializing database...")
            success = (create_database_schema() and 
                      seed_initial_data() and 
                      create_admin_user())
        
        elif args.command == 'reset':
            print("Resetting database...")
            success = reset_database()
        
        elif args.command == 'seed':
            print("Seeding database...")
            success = seed_initial_data()
        
        elif args.command == 'verify':
            print("Verifying database...")
            success = verify_database()
        
        elif args.command == 'backup':
            print("Backing up database...")
            success = backup_database()
        
        elif args.command == 'upgrade':
            print("Upgrading database...")
            success = upgrade_database()
        
        elif args.command == 'create-admin':
            print("Creating admin user...")
            success = create_admin_user()
        
        print("=" * 60)
        if success:
            print("✅ Migration completed successfully!")
        else:
            print("❌ Migration failed!")
            sys.exit(1)

if __name__ == '__main__':
    main()