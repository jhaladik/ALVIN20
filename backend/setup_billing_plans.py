from app import create_app, db
from app.models import BillingPlan
from decimal import Decimal

def setup_perfect_plans():
    """Create billing plans using the EXACT field names from your model"""
    app = create_app()
    with app.app_context():
        # Check if plans already exist
        if BillingPlan.query.count() > 0:
            print("✅ Billing plans already exist")
            for plan in BillingPlan.query.all():
                print(f"   - {plan.name}: {plan.display_name}")
            return
        
        print("🔧 Creating billing plans with correct field names...")
        
        # Create plans using the EXACT fields from your model
        plans = [
            {
                'name': 'free',
                'display_name': 'Free',
                'description': 'Perfect for getting started with ALVIN. Try AI-powered writing assistance.',
                'price_monthly': Decimal('0.00'),      # ✅ CORRECT: price_monthly, not price
                'price_yearly': Decimal('0.00'),       # ✅ CORRECT: price_yearly
                'token_limit': 1000,                   # ✅ CORRECT: token_limit exists
                'project_limit': 3,                    # ✅ CORRECT: project_limit exists
                'features': [                          # ✅ CORRECT: JSON list
                    'Up to 3 projects',
                    'Basic AI assistance',
                    'Text export',
                    '1,000 AI tokens per month'
                ],
                'is_active': True                      # ✅ CORRECT: is_active exists
            },
            {
                'name': 'pro',
                'display_name': 'Pro',
                'description': 'Advanced features for serious writers. Everything you need to write better.',
                'price_monthly': Decimal('19.99'),     # ✅ CORRECT: price_monthly
                'price_yearly': Decimal('199.99'),     # ✅ CORRECT: price_yearly
                'token_limit': 10000,                  # ✅ CORRECT: token_limit
                'project_limit': 25,                   # ✅ CORRECT: project_limit
                'features': [                          # ✅ CORRECT: JSON list
                    'Up to 25 projects',
                    'Advanced AI assistance',
                    'All export formats',
                    'Real-time collaboration',
                    '10,000 AI tokens per month',
                    'Priority support'
                ],
                'is_active': True                      # ✅ CORRECT: is_active
            },
            {
                'name': 'enterprise',
                'display_name': 'Enterprise',
                'description': 'For teams and professional writers. Scale your writing with powerful features.',
                'price_monthly': Decimal('49.99'),     # ✅ CORRECT: price_monthly
                'price_yearly': Decimal('499.99'),     # ✅ CORRECT: price_yearly
                'token_limit': 50000,                  # ✅ CORRECT: token_limit
                'project_limit': 100,                  # ✅ CORRECT: project_limit
                'features': [                          # ✅ CORRECT: JSON list
                    'Up to 100 projects',
                    'Premium AI assistance',
                    'All export formats',
                    'Team collaboration',
                    'Advanced analytics',
                    '50,000 AI tokens per month',
                    'Priority support',
                    'Team management',
                    'Custom integrations'
                ],
                'is_active': True                      # ✅ CORRECT: is_active
            }
        ]
        
        # Create each plan
        created_count = 0
        for plan_data in plans:
            try:
                plan = BillingPlan(**plan_data)
                db.session.add(plan)
                print(f"✅ Added plan: {plan_data['display_name']} (${plan_data['price_monthly']}/month)")
                created_count += 1
            except Exception as e:
                print(f"❌ Failed to add plan {plan_data['name']}: {e}")
        
        # Commit all plans
        try:
            db.session.commit()
            print(f"\n🎉 SUCCESS! Created {created_count} billing plans in database!")
            
            # Verify creation
            total_plans = BillingPlan.query.count()
            print(f"📊 Total plans in database: {total_plans}")
            
            # Show created plans
            print("\n📋 Created plans:")
            for plan in BillingPlan.query.all():
                print(f"   🏷️  {plan.name}: {plan.display_name} - ${plan.price_monthly}/month")
                
        except Exception as e:
            print(f"❌ Commit failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    setup_perfect_plans()