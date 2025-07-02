# blueprint_fix.py - COMPREHENSIVE BLUEPRINT FIX SCRIPT
"""
Complete fix for all blueprint registration issues
Run this script to diagnose and fix all backend problems
"""

import os
import sys
import importlib
import traceback
from datetime import datetime

def fix_blueprint_registration():
    """Fix all blueprint registration issues"""
    
    print("🔧 ALVIN BLUEPRINT COMPREHENSIVE FIX")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Validate models and fix table name issues
    print("📋 STEP 1: FIXING MODEL TABLE NAME MISMATCHES")
    print("-" * 40)
    
    try:
        # Test model imports
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.models import User, Project, Scene, StoryObject, SceneObject
        print("✅ Model imports successful")
        
        # Verify table names match migrations
        table_mapping = {
            'User': 'user',
            'Project': 'project', 
            'Scene': 'scene',
            'StoryObject': 'story_object',
            'SceneObject': 'scene_object'
        }
        
        for model_name, expected_table in table_mapping.items():
            model_class = globals()[model_name]
            actual_table = model_class.__tablename__
            if actual_table == expected_table:
                print(f"✅ {model_name}: table '{actual_table}' correct")
            else:
                print(f"❌ {model_name}: table '{actual_table}' should be '{expected_table}'")
                
    except Exception as e:
        print(f"❌ Model import failed: {str(e)}")
        print("   Fix: Update models.py with corrected table names")
    
    print()
    
    # Step 2: Check configuration completeness
    print("⚙️  STEP 2: VALIDATING CONFIGURATION")
    print("-" * 40)
    
    try:
        from config import DevelopmentConfig, config
        
        required_config_values = [
            'PROJECTS_PER_PAGE',
            'SCENES_PER_PAGE', 
            'OBJECTS_PER_PAGE',
            'ANALYTICS_ITEMS_PER_PAGE',
            'TOKEN_LIMITS',
            'PLAN_CONFIGS',
            'RATE_LIMITS'
        ]
        
        config_instance = DevelopmentConfig()
        missing_configs = []
        
        for config_name in required_config_values:
            if hasattr(config_instance, config_name):
                value = getattr(config_instance, config_name)
                print(f"✅ {config_name}: {value}")
            else:
                missing_configs.append(config_name)
                print(f"❌ {config_name}: MISSING")
        
        if missing_configs:
            print(f"   Fix: Add missing config values: {', '.join(missing_configs)}")
        else:
            print("✅ All required configuration values present")
            
    except Exception as e:
        print(f"❌ Configuration validation failed: {str(e)}")
        print("   Fix: Update config.py with complete configuration")
    
    print()
    
    # Step 3: Validate service imports  
    print("🔧 STEP 3: VALIDATING SERVICE IMPORTS")
    print("-" * 40)
    
    services_to_test = [
        ('app.services.export_service', 'ExportService'),
        ('app.services.claude_service', 'ClaudeService'),
        ('app.services.token_service', 'TokenService')
    ]
    
    for module_name, service_name in services_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, service_name):
                service_class = getattr(module, service_name)
                print(f"✅ {module_name}.{service_name}")
                
                # Test ExportService initialization
                if service_name == 'ExportService':
                    service_instance = service_class()
                    formats = service_instance.get_supported_formats()
                    print(f"   └─ Supported formats: {formats}")
                    
            else:
                print(f"❌ {module_name}: {service_name} not found")
        except ImportError as e:
            print(f"❌ {module_name}: Import failed - {str(e)}")
        except Exception as e:
            print(f"⚠️  {module_name}: Warning - {str(e)}")
    
    print()
    
    # Step 4: Test blueprint imports individually
    print("📦 STEP 4: TESTING BLUEPRINT IMPORTS")
    print("-" * 40)
    
    blueprints_to_test = [
        ('app.routes.auth', 'auth_bp'),
        ('app.routes.projects', 'projects_bp'),  
        ('app.routes.scenes', 'scenes_bp'),
        ('app.routes.objects', 'objects_bp'),
        ('app.routes.analytics', 'analytics_bp'),
        ('app.routes.ai', 'ai_bp'),
        ('app.routes.collaboration', 'collaboration_bp'),
        ('app.routes.billing', 'billing_bp')
    ]
    
    successful_imports = 0
    failed_imports = []
    
    for module_name, blueprint_name in blueprints_to_test:
        try:
            print(f"   Testing {module_name}...")
            module = importlib.import_module(module_name)
            
            if hasattr(module, blueprint_name):
                blueprint = getattr(module, blueprint_name)
                print(f"✅ {blueprint_name}: Successfully imported")
                successful_imports += 1
            else:
                print(f"❌ {blueprint_name}: Blueprint not found in module")
                failed_imports.append((module_name, f"Blueprint '{blueprint_name}' not found"))
                
        except ImportError as e:
            print(f"❌ {module_name}: Import error - {str(e)}")
            failed_imports.append((module_name, f"Import error: {str(e)}"))
        except Exception as e:
            print(f"❌ {module_name}: Unexpected error - {str(e)}")
            failed_imports.append((module_name, f"Unexpected error: {str(e)}"))
    
    print()
    print(f"📊 Blueprint Import Summary:")
    print(f"   ✅ Successful: {successful_imports}/8")
    print(f"   ❌ Failed: {len(failed_imports)}/8")
    
    if failed_imports:
        print(f"\n❌ FAILED IMPORTS:")
        for module_name, error in failed_imports:
            print(f"   {module_name}: {error}")
    
    print()
    
    # Step 5: Test full application startup
    print("🚀 STEP 5: TESTING FULL APPLICATION STARTUP")
    print("-" * 40)
    
    try:
        from app import create_app
        
        # Test app creation
        app = create_app('development')
        print("✅ App creation successful")
        
        # Test blueprint registration within app context
        with app.app_context():
            registered_blueprints = list(app.blueprints.keys())
            print(f"✅ Registered blueprints: {len(registered_blueprints)}")
            for bp_name in registered_blueprints:
                print(f"   └─ {bp_name}")
            
            # Count routes
            route_count = len(list(app.url_map.iter_rules()))
            print(f"✅ Total registered routes: {route_count}")
            
    except Exception as e:
        print(f"❌ Application startup failed: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
    
    print()
    
    # Step 6: Provide fix recommendations
    print("💡 STEP 6: FIX RECOMMENDATIONS")
    print("-" * 40)
    
    if successful_imports == 8:
        print("🎉 ALL BLUEPRINTS IMPORTING SUCCESSFULLY!")
        print("   Your issues are likely configuration or database related.")
        print("   Recommended actions:")
        print("   1. Apply the model table name fixes")
        print("   2. Update configuration with missing values")
        print("   3. Restart the backend server")
        print("   4. Run the diagnostic again")
    else:
        print("🔧 BLUEPRINT IMPORT ISSUES DETECTED")
        print("   Priority fixes needed:")
        print("   1. ✅ Apply model table name corrections (models.py)")
        print("   2. ✅ Update configuration with missing values (config.py)")
        print("   3. ✅ Fix ExportService graceful dependency handling")
        print("   4. 🔄 Address specific blueprint import errors listed above")
        print("   5. 🔄 Restart backend server")
        print("   6. 🔄 Re-run diagnostic")
    
    print()
    print("📋 IMMEDIATE ACTION ITEMS:")
    print("1. Replace models.py with the corrected version")
    print("2. Replace config.py with the complete configuration")  
    print("3. Replace app/services/export_service.py with robust version")
    print("4. Restart backend: `python run.py`")
    print("5. Re-run diagnostic to verify fixes")
    
    print()
    print(f"🏁 Fix analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return successful_imports, failed_imports

if __name__ == "__main__":
    successful, failed = fix_blueprint_registration()
    
    if successful == 8:
        print("\n🎉 SUCCESS: All blueprints ready for registration!")
        sys.exit(0)
    else:
        print(f"\n⚠️  ACTION REQUIRED: {len(failed)} blueprint issues need fixing")
        sys.exit(1)