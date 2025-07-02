# test_cors.py - QUICK CORS TEST SCRIPT
"""
Run this script to test if CORS is working
"""

import requests
import json

def test_cors():
    """Test CORS configuration"""
    
    print("🧪 TESTING CORS CONFIGURATION")
    print("=" * 40)
    
    backend_url = "http://localhost:5000"
    frontend_origin = "http://localhost:5173"
    
    # Test 1: Basic health check
    print("1. Testing basic connection...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        print(f"   ✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: CORS preflight request
    print("2. Testing CORS preflight...")
    try:
        headers = {
            'Origin': frontend_origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options(f"{backend_url}/api/auth/login", headers=headers, timeout=5)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers:")
        for key, value in cors_headers.items():
            status = "✅" if value else "❌"
            print(f"     {status} {key}: {value}")
        
        # Check if CORS is properly configured
        origin_allowed = cors_headers['Access-Control-Allow-Origin'] in [frontend_origin, '*']
        methods_allowed = 'POST' in (cors_headers['Access-Control-Allow-Methods'] or '')
        headers_allowed = 'Authorization' in (cors_headers['Access-Control-Allow-Headers'] or '')
        
        if origin_allowed and methods_allowed and headers_allowed:
            print("   🎉 CORS is properly configured!")
            return True
        else:
            print("   ⚠️ CORS configuration issues detected")
            
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
        return False
    
    # Test 3: Actual API request with CORS headers
    print("3. Testing API request with CORS...")
    try:
        headers = {
            'Origin': frontend_origin,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{backend_url}/api", headers=headers, timeout=5)
        
        print(f"   Status: {response.status_code}")
        origin_header = response.headers.get('Access-Control-Allow-Origin')
        print(f"   Response Origin: {origin_header}")
        
        if origin_header in [frontend_origin, '*']:
            print("   ✅ API requests should work from frontend")
            return True
        else:
            print("   ❌ API requests will be blocked by CORS")
            return False
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False

def suggest_fixes():
    """Suggest CORS fixes"""
    print("\n🔧 CORS FIX SUGGESTIONS:")
    print("-" * 30)
    print("1. Quick fix - Add to your .env file:")
    print('   CORS_ORIGINS="http://localhost:5173,http://localhost:3000"')
    print()
    print("2. Development fix - In app/__init__.py, change CORS line to:")
    print('   CORS(app, origins=["*"], supports_credentials=True, ...)')
    print()
    print("3. Restart your backend server:")
    print("   python run.py")
    print()
    print("4. Check frontend is running on:")
    print("   http://localhost:5173")

if __name__ == "__main__":
    success = test_cors()
    
    if not success:
        suggest_fixes()
    else:
        print("\n🎉 CORS is working correctly!")
        print("If you're still getting errors, check:")
        print("- Frontend is running on http://localhost:5173")
        print("- Backend is running on http://localhost:5000") 
        print("- No proxy/firewall blocking requests")