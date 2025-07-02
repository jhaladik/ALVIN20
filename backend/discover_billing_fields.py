from app import create_app, db
from app.models import BillingPlan

def discover_billing_plan_fields():
    """Discover the actual fields in your BillingPlan model"""
    app = create_app()
    with app.app_context():
        # Get the model's columns
        print("🔍 Discovering BillingPlan model fields...")
        print("=" * 50)
        
        # Method 1: Check SQLAlchemy columns
        columns = BillingPlan.__table__.columns
        print("📋 Available fields in BillingPlan:")
        for column in columns:
            print(f"   ✅ {column.name} ({column.type})")
        
        print("\n" + "=" * 50)
        
        # Method 2: Try to create a minimal plan to see what's required
        print("🧪 Testing minimal BillingPlan creation...")
        try:
            # Try creating with just required fields
            test_plan = BillingPlan(
                name='test',
                display_name='Test Plan',
                description='Test description'
            )
            print("✅ Minimal plan creation works!")
            print("🎯 Required fields: name, display_name, description")
            
            # Don't actually save it
            
        except Exception as e:
            print(f"❌ Minimal plan creation failed: {e}")
        
        print("\n" + "=" * 50)
        print("📝 Use this information to create the correct setup script")

if __name__ == "__main__":
    discover_billing_plan_fields()