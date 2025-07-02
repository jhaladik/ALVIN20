#!/usr/bin/env python3
"""
ALVIN20 Backend Test Script
Tests the backend API endpoints and verifies functionality
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class BackendTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token = None
        
    def test_connection(self) -> bool:
        """Test basic connection to the backend"""
        print("🔌 Testing backend connection...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend is running: {data.get('status', 'OK')}")
                return True
            else:
                print(f"❌ Backend returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend - is it running?")
            return False
        except requests.exceptions.Timeout:
            print("❌ Backend connection timed out")
            return False
        except Exception as e:
            print(f"❌ Error connecting to backend: {e}")
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connectivity through the backend"""
        print("🗄️  Testing database connection...")
        try:
            response = self.session.get(f"{self.base_url}/api/status/db")
            if response.status_code == 200:
                data = response.json()
                if data.get('database_connected'):
                    print("✅ Database connection successful")
                    return True
                else:
                    print("❌ Database not connected")
                    return False
            else:
                print(f"❌ Database status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False
    
    def test_redis_connection(self) -> bool:
        """Test Redis connectivity through the backend"""
        print("💾 Testing Redis connection...")
        try:
            response = self.session.get(f"{self.base_url}/api/status/redis")
            if response.status_code == 200:
                data = response.json()
                if data.get('redis_connected'):
                    print("✅ Redis connection successful")
                    return True
                else:
                    print("❌ Redis not connected")
                    return False
            else:
                print(f"❌ Redis status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Redis connection test failed: {e}")
            return False
    
    def test_auth_endpoints(self) -> bool:
        """Test authentication endpoints"""
        print("🔐 Testing authentication endpoints...")
        
        # Test login with demo account
        login_data = {
            "email": "demo@alvin.ai",
            "password": "demo123"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                print("✅ Authentication successful")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            return False
    
    def test_ai_endpoints(self) -> bool:
        """Test AI-related endpoints"""
        print("🤖 Testing AI endpoints...")
        
        if not self.auth_token:
            print("❌ No auth token available, skipping AI tests")
            return False
        
        try:
            # Test AI status
            response = self.session.get(f"{self.base_url}/api/ai/status")
            if response.status_code == 200:
                data = response.json()
                ai_available = data.get('ai_available', False)
                simulation_mode = data.get('simulation_mode', True)
                
                if ai_available or simulation_mode:
                    print("✅ AI service available")
                    if simulation_mode:
                        print("   ℹ️  Running in simulation mode")
                    return True
                else:
                    print("❌ AI service not available")
                    return False
            else:
                print(f"❌ AI status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ AI endpoint test failed: {e}")
            return False
    
    def test_story_endpoints(self) -> bool:
        """Test story-related endpoints"""
        print("📚 Testing story endpoints...")
        
        if not self.auth_token:
            print("❌ No auth token available, skipping story tests")
            return False
        
        try:
            # Test getting user stories
            response = self.session.get(f"{self.base_url}/api/stories")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Story endpoints working - found {len(data.get('stories', []))} stories")
                return True
            else:
                print(f"❌ Story endpoints failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Story endpoint test failed: {e}")
            return False
    
    def test_file_upload(self) -> bool:
        """Test file upload functionality"""
        print("📁 Testing file upload...")
        
        if not self.auth_token:
            print("❌ No auth token available, skipping upload tests")
            return False
        
        try:
            # Create a simple test file
            test_content = "This is a test file for ALVIN backend"
            files = {
                'file': ('test.txt', test_content, 'text/plain')
            }
            
            response = self.session.post(
                f"{self.base_url}/api/upload",
                files=files
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ File upload working")
                return True
            else:
                print(f"❌ File upload failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ File upload test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all backend tests"""
        print("🎭 ALVIN20 Backend Test Suite")
        print("=" * 50)
        
        results = {}
        
        # Basic connectivity
        results['connection'] = self.test_connection()
        if not results['connection']:
            print("\n❌ Cannot connect to backend - stopping tests")
            return results
        
        # Wait a moment for backend to stabilize
        time.sleep(2)
        
        # Database and Redis
        results['database'] = self.test_database_connection()
        results['redis'] = self.test_redis_connection()
        
        # Authentication
        results['auth'] = self.test_auth_endpoints()
        
        # API endpoints (require auth)
        results['ai'] = self.test_ai_endpoints()
        results['stories'] = self.test_story_endpoints()
        results['upload'] = self.test_file_upload()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.capitalize():15} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the issues above.")
            
        return passed == total

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test ALVIN20 Backend')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Backend URL (default: http://localhost:5000)')
    parser.add_argument('--wait', type=int, default=0,
                       help='Wait N seconds before starting tests')
    
    args = parser.parse_args()
    
    if args.wait > 0:
        print(f"⏱️  Waiting {args.wait} seconds for backend to start...")
        time.sleep(args.wait)
    
    tester = BackendTester(args.url)
    results = tester.run_all_tests()
    success = tester.print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
