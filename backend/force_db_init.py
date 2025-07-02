# force_db_init.py - FORCE DATABASE INITIALIZATION
"""
Create all database tables and initialize with demo data
Run this when the database tables don't exist
"""

import os
import sys
from datetime import datetime

def force_database_initialization():
    """Force create all database tables and add demo data"""
    
    print("🗄️ ALVIN DATABASE FORCE INITIALIZATION")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Set environment variables for development
        os.environ['FLASK_CONFIG'] = 'development'
        
        # Import app and db
        from app import create_app, db
        
        print("📦 Creating Flask app...")
        app = create_app('development')
        
        print("🔗 Establishing database connection...")
        with app.app_context():
            
            # Import all models to ensure they're registered
            print("📋 Importing all models...")
            from app.models import (
                User, Project, Scene, StoryObject, SceneObject, 
                TokenUsageLog, BillingPlan, UserSubscription,
                Comment, ProjectCollaborator
            )
            
            print("✅ All models imported successfully")
            
            # Check if tables already exist
            print("🔍 Checking existing tables...")
            try:
                existing_users = User.query.count()
                print(f"✅ Database connected - found {existing_users} existing users")
                
                # If we can query users, tables exist
                print("🎉 Database tables already exist!")
                return True
                
            except Exception as e:
                print(f"❌ Database tables missing: {str(e)}")
                print("🔧 Creating all database tables...")
            
            # Drop all tables if they exist (fresh start)
            print("🗑️ Dropping existing tables (if any)...")
            db.drop_all()
            
            # Create all tables
            print("🏗️ Creating all database tables...")
            db.create_all()
            
            # Verify table creation
            print("✅ Verifying table creation...")
            inspector = db.inspect(db.engine)
            table_names = inspector.get_table_names()
            
            expected_tables = [
                'user', 'project', 'scene', 'story_object', 'scene_object',
                'token_usage_log', 'billing_plan', 'user_subscription',
                'comment', 'project_collaborator'
            ]
            
            created_tables = []
            missing_tables = []
            
            for table in expected_tables:
                if table in table_names:
                    created_tables.append(table)
                    print(f"   ✅ {table}")
                else:
                    missing_tables.append(table)
                    print(f"   ❌ {table} - MISSING")
            
            if missing_tables:
                print(f"\n⚠️ Missing tables: {missing_tables}")
                return False
            
            print(f"\n✅ Successfully created {len(created_tables)} tables")
            
            # Create default billing plans
            print("\n💳 Creating default billing plans...")
            create_billing_plans(db)
            
            # Create demo user
            print("\n👤 Creating demo user...")
            create_demo_user(db)
            
            # Commit all changes
            print("💾 Committing changes...")
            db.session.commit()
            
            print("\n🎉 DATABASE INITIALIZATION COMPLETE!")
            print("✅ All tables created")
            print("✅ Demo user created: demo@alvin.ai / demo123") 
            print("✅ Billing plans configured")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Database initialization failed: {str(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        return False

def create_billing_plans(db):
    """Create default billing plans"""
    from app.models import BillingPlan
    
    plans = [
        {
            'id': 'free',
            'name': 'Free Plan',
            'description': 'Perfect for getting started with story writing',
            'price_monthly': 0,
            'price_yearly': 0,
            'token_limit': 1000,
            'max_projects': 3,
            'max_scenes_per_project': 20,
            'features': [
                'Up to 3 projects',
                '20 scenes per project', 
                '1,000 AI tokens/month',
                'Basic export (TXT, HTML)',
                'Community support'
            ]
        },
        {
            'id': 'pro',
            'name': 'Pro Plan',
            'description': 'For serious writers who need more power',
            'price_monthly': 1999,  # $19.99
            'price_yearly': 19999,  # $199.99
            'token_limit': 10000,
            'max_projects': 25,
            'max_scenes_per_project': 100,
            'features': [
                'Up to 25 projects',
                '100 scenes per project',
                '10,000 AI tokens/month',
                'All export formats (PDF, DOCX)',
                'Advanced analytics',
                'Priority support'
            ]
        },
        {
            'id': 'enterprise',
            'name': 'Enterprise Plan',
            'description': 'For teams and professional writers',
            'price_monthly': 4999,  # $49.99
            'price_yearly': 49999,  # $499.99
            'token_limit': 50000,
            'max_projects': 100,
            'max_scenes_per_project': 500,
            'features': [
                'Unlimited projects',
                '500 scenes per project',
                '50,000 AI tokens/month',
                'Team collaboration',
                'Custom integrations',
                'Dedicated support'
            ]
        }
    ]
    
    for plan_data in plans:
        existing_plan = BillingPlan.query.get(plan_data['id'])
        if not existing_plan:
            plan = BillingPlan(**plan_data)
            db.session.add(plan)
            print(f"   ✅ Created plan: {plan_data['name']}")
        else:
            print(f"   ⚠️ Plan already exists: {plan_data['name']}")

def create_demo_user(db):
    """Create demo user for testing"""
    from app.models import User, UserSubscription
    
    # Check if demo user already exists
    demo_user = User.query.filter_by(email='demo@alvin.ai').first()
    if demo_user:
        print("   ⚠️ Demo user already exists")
        return demo_user
    
    # Create demo user
    demo_user = User(
        username='demo_user',
        email='demo@alvin.ai',
        full_name='Demo User',
        bio='This is a demo account for testing ALVIN',
        is_active=True,
        is_verified=True,
        plan='free',
        tokens_used=0,
        tokens_limit=1000
    )
    demo_user.set_password('demo123')
    
    db.session.add(demo_user)
    db.session.flush()  # Get the ID
    
    # Create subscription for demo user
    subscription = UserSubscription(
        user_id=demo_user.id,
        plan_id='free',
        status='active'
    )
    
    db.session.add(subscription)
    
    print(f"   ✅ Created demo user: {demo_user.email}")
    return demo_user

if __name__ == "__main__":
    success = force_database_initialization()
    
    if success:
        print("\n🎯 SUCCESS: Database initialized!")
        print("🚀 You can now start the backend server")
        print("📧 Login with: demo@alvin.ai / demo123")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Database initialization failed")
        sys.exit(1)