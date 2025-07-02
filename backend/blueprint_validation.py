# blueprint_validation.py
# Run this script to validate blueprint registration
# Usage: python blueprint_validation.py

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import requests
import json
from datetime import datetime

def validate_blueprint_registration():
    """Validate that all blueprints are properly registered"""
    
    print("🧪 BLUEPRINT REGISTRATION VALIDATION")
    print("=" * 50)
    
    # Create app instance
    try:
        app = create_app('development')
        print("✅ App created successfully")
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False
    
    # Test with app context
    with app.app_context():
        
        # 1. Check registered blueprints
        print(f"\n📦 REGISTERED BLUEPRINTS:")
        blueprint_count = 0
        expected_blueprints = ['auth_bp', 'projects_bp', 'scenes_bp', 'objects_bp', 
                              'analytics_bp', 'ai_bp', 'collaboration_bp', 'billing_bp']
        
        for blueprint_name in app.blueprints:
            blueprint = app.blueprints[blueprint_name]
            print(f"   ✅ {blueprint_name}: {blueprint.url_prefix or 'No prefix'}")
            blueprint_count += 1
        
        print(f"\n📊 Blueprint Count: {blueprint_count} registered")
        
        # 2. Check route registration
        print(f"\n🛣️  REGISTERED ROUTES BY BLUEPRINT:")
        blueprint_routes = {}
        
        for rule in app.url_map.iter_rules():
            endpoint = rule.endpoint
            blueprint_name = endpoint.split('.')[0] if '.' in endpoint else 'main'
            
            if blueprint_name not in blueprint_routes:
                blueprint_routes[blueprint_name] = []
            
            methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            blueprint_routes[blueprint_name].append({
                'path': rule.rule,
                'methods': methods,
                'endpoint': endpoint
            })
        
        # Display routes by blueprint
        for bp_name, routes in blueprint_routes.items():
            if bp_name in expected_blueprints or bp_name == 'main':
                print(f"\n   📋 {bp_name} ({len(routes)} routes):")
                for route in sorted(routes, key=lambda x: x['path']):
                    print(f"      {route['methods']:12} {route['path']}")
        
        # 3. Expected endpoint validation
        print(f"\n🎯 CRITICAL ENDPOINT VALIDATION:")
        critical_endpoints = [
            '/api/auth/register',
            '/api/auth/login', 
            '/api/projects',
            '/api/scenes',
            '/api/objects',
            '/api/ai/analyze-idea',
            '/api/analytics/dashboard',
            '/api/billing/plans'
        ]
        
        missing_endpoints = []
        for endpoint in critical_endpoints:
            found = False
            for rule in app.url_map.iter_rules():
                if rule.rule == endpoint:
                    found = True
                    break
            
            if found:
                print(f"   ✅ {endpoint}")
            else:
                print(f"   ❌ {endpoint} - MISSING")
                missing_endpoints.append(endpoint)
        
        # 4. Conflict detection
        print(f"\n⚠️  CONFLICT DETECTION:")
        conflicts_found = False
        
        # Check for duplicate routes
        route_paths = {}
        for rule in app.url_map.iter_rules():
            path_method = f"{rule.rule}:{','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))}"
            if path_method in route_paths:
                print(f"   ❌ CONFLICT: {path_method} registered multiple times")
                conflicts_found = True
            else:
                route_paths[path_method] = rule.endpoint
        
        if not conflicts_found:
            print("   ✅ No route conflicts detected")
        
        # 5. Summary
        print(f"\n📈 VALIDATION SUMMARY:")
        print(f"   Blueprints registered: {blueprint_count}/8 expected")
        print(f"   Critical endpoints missing: {len(missing_endpoints)}")
        print(f"   Route conflicts: {'Yes' if conflicts_found else 'No'}")
        
        # Overall status
        if blueprint_count >= 6 and len(missing_endpoints) == 0 and not conflicts_found:
            print(f"\n🎉 VALIDATION PASSED: Blueprint registration successful!")
            return True
        else:
            print(f"\n❌ VALIDATION FAILED: Issues detected")
            return False


def test_live_endpoints():
    """Test blueprint endpoints with live requests (requires running server)"""
    
    print(f"\n🌐 LIVE ENDPOINT TESTING")
    print("=" * 50)
    print("Note: This requires the Flask server to be running on localhost:5000")
    
    base_url = "http://localhost:5000"
    
    # Test basic endpoints
    test_endpoints = [
        {'url': '/', 'method': 'GET', 'description': 'Home page'},
        {'url': '/health', 'method': 'GET', 'description': 'Health check'},
        {'url': '/api', 'method': 'GET', 'description': 'API info'},
        {'url': '/api/auth/register', 'method': 'POST', 'description': 'Auth registration (expects 400)'},
        {'url': '/api/projects', 'method': 'GET', 'description': 'Projects list (expects 401)'},
        {'url': '/api/billing/plans', 'method': 'GET', 'description': 'Billing plans'},
    ]
    
    for test in test_endpoints:
        try:
            if test['method'] == 'GET':
                response = requests.get(f"{base_url}{test['url']}", timeout=5)
            else:
                response = requests.post(f"{base_url}{test['url']}", json={}, timeout=5)
            
            status_code = response.status_code
            if status_code in [200, 400, 401, 405]:  # Expected responses
                print(f"   ✅ {test['method']} {test['url']} → {status_code} ({test['description']})")
            else:
                print(f"   ⚠️  {test['method']} {test['url']} → {status_code} (unexpected)")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {test['method']} {test['url']} → Connection failed (server not running?)")
        except Exception as e:
            print(f"   💥 {test['method']} {test['url']} → Error: {str(e)}")


if __name__ == "__main__":
    print(f"🚀 Starting Blueprint Validation at {datetime.now().strftime('%H:%M:%S')}")
    
    # Validate registration
    validation_passed = validate_blueprint_registration()
    
    # Ask for live testing
    if validation_passed:
        print(f"\n" + "=" * 50)
        live_test = input("Run live endpoint tests? (requires running server) [y/N]: ")
        if live_test.lower() == 'y':
            test_live_endpoints()
    
    print(f"\n✨ Validation complete at {datetime.now().strftime('%H:%M:%S')}")
