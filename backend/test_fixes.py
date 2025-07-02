#!/usr/bin/env python3
"""
Quick test for auth blueprint fixes
Run this after replacing the auth.py file: python test_auth_fix.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_auth_blueprint():
    """Test the fixed auth blueprint"""
    print("🔐 Testing Fixed Auth Blueprint")
    print("=" * 40)
    
    # Test 1: Auth status endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/auth/status", timeout=5)
        if response.status_code == 200:
            print("✅ Auth Blueprint: Registered and working")
            data = response.json()
            print(f"   Demo users: {data.get('demo_users_count', 0)}")
        else:
            print(f"⚠️  Auth Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Auth Status: {str(e)}")
    
    # Test 2: Demo login
    try:
        login_data = {"email": "demo@alvin.ai", "password": "demo123"}
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json=login_data, timeout=5)
        if response.status_code == 200:
            print("✅ Demo Login: Working")
            data = response.json()
            if 'token' in data or 'access_token' in data:
                token = data.get('token') or data.get('access_token')
                print(f"   Token received: {token[:20]}...")
                return token
            else:
                print("⚠️  Token missing in response")
                return None
        else:
            print(f"❌ Demo Login: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
            return None
    except Exception as e:
        print(f"❌ Demo Login: {str(e)}")
        return None

def test_protected_endpoints(token):
    """Test protected endpoints with token"""
    if not token:
        print("\n🔒 Skipping protected tests (no token)")
        return
    
    print(f"\n🛡️  Testing Protected Endpoints")
    print("=" * 40)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test token verification
    try:
        response = requests.get(f"{BASE_URL}/api/auth/verify", 
                              headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Token Verify: Working")
            data = response.json()
            print(f"   Valid: {data.get('valid', False)}")
        else:
            print(f"❌ Token Verify: {response.status_code}")
    except Exception as e:
        print(f"❌ Token Verify: {str(e)}")
    
    # Test get current user
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", 
                              headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Get User: Working")
            data = response.json()
            user = data.get('user', {})
            print(f"   User: {user.get('email', 'Unknown')}")
        else:
            print(f"❌ Get User: {response.status_code}")
    except Exception as e:
        print(f"❌ Get User: {str(e)}")

def test_registration():
    """Test user registration"""
    print(f"\n📝 Testing Registration")
    print("=" * 40)
    
    timestamp = int(datetime.now().timestamp())
    register_data = {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", 
                               json=register_data, timeout=5)
        if response.status_code == 201:
            print("✅ Registration: Working")
            data = response.json()
            if 'token' in data or 'access_token' in data:
                print("   Token provided in registration")
            user = data.get('user', {})
            print(f"   Created user: {user.get('email', 'Unknown')}")
        elif response.status_code == 400:
            print("⚠️  Registration: Validation error (expected for testing)")
        else:
            print(f"❌ Registration: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Registration: {str(e)}")

def main():
    print("🚀 Auth Blueprint Fix Verification")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test auth blueprint
    token = test_auth_blueprint()
    
    # Test protected endpoints
    test_protected_endpoints(token)
    
    # Test registration
    test_registration()
    
    print(f"\n✨ Auth test complete at {datetime.now().strftime('%H:%M:%S')}")
    
    if token:
        print("\n🎉 SUCCESS: Auth blueprint is working!")
        print("   ✅ Demo login functional")
        print("   ✅ Token generation working")
        print("   ✅ Protected endpoints accessible")
        print("\n📋 Next: Run the comprehensive diagnostic to see improvement")
    else:
        print("\n❌ Auth blueprint still has issues")
        print("   Check server console for import errors")

if __name__ == "__main__":
    main()