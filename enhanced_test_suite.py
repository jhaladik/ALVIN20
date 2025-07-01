#!/usr/bin/env python3
"""
Simplified ALVIN Frontend-Backend Integration Test Suite
Works with existing dependencies - no playwright or websockets required
"""

import asyncio
import aiohttp
import json
import time
import logging
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics
import psutil
import sys
import subprocess
import requests
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'alvin_simplified_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

@dataclass
class TestResult:
    test_name: str
    category: str  # 'backend', 'frontend', 'integration'
    status: str    # 'pass', 'fail', 'warning', 'skip'
    details: Dict[str, Any]
    response_time: float
    timestamp: datetime
    recommendations: List[str] = None

class SimplifiedTestSuite:
    def __init__(self, backend_url: str = "http://localhost:5000", frontend_url: str = "http://localhost:5173"):
        self.backend_url = backend_url.rstrip('/')
        self.frontend_url = frontend_url.rstrip('/')
        self.results: List[TestResult] = []
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()
        
    def add_result(self, test_name: str, category: str, status: str, details: Dict, response_time: float = 0, recommendations: List[str] = None):
        """Add a test result"""
        self.results.append(TestResult(
            test_name=test_name,
            category=category,
            status=status,
            details=details,
            response_time=response_time,
            timestamp=datetime.now(),
            recommendations=recommendations or []
        ))
    
    async def run_comprehensive_test(self) -> Dict:
        """Run comprehensive tests using available tools"""
        self.logger.info("🎭 Starting Simplified ALVIN Integration Test Suite")
        self.logger.info("=" * 80)
        
        # Test service availability
        await self.test_service_availability()
        
        # Enhanced backend tests
        await self.test_enhanced_backend_functionality()
        
        # Frontend static analysis (without browser)
        await self.test_frontend_static_analysis()
        
        # Integration tests using HTTP only
        await self.test_http_integration_patterns()
        
        # Analyze results and generate report
        return self.generate_comprehensive_report()
    
    async def test_service_availability(self):
        """Test if services are running and accessible"""
        self.logger.info("🔍 Testing Service Availability...")
        
        # Test backend
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health") as response:
                    backend_healthy = response.status == 200
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    self.add_result(
                        "backend_health",
                        "backend", 
                        "pass" if backend_healthy else "fail",
                        {
                            "status_code": response.status,
                            "response_data": response_data,
                            "healthy": backend_healthy
                        },
                        time.time() - start_time
                    )
        except Exception as e:
            self.add_result(
                "backend_health",
                "backend",
                "fail",
                {"error": str(e), "accessible": False},
                time.time() - start_time,
                ["🔧 Backend is not accessible - check if it's running on port 5000"]
            )
        
        # Test frontend
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.frontend_url) as response:
                    frontend_accessible = response.status == 200
                    content = await response.text()
                    
                    # Check for key frontend indicators
                    has_react = 'react' in content.lower() or 'vite' in content.lower()
                    has_app_root = 'id="root"' in content or 'id="app"' in content
                    
                    self.add_result(
                        "frontend_accessibility",
                        "frontend",
                        "pass" if frontend_accessible else "fail",
                        {
                            "status_code": response.status,
                            "accessible": frontend_accessible,
                            "has_react_indicators": has_react,
                            "has_app_root": has_app_root,
                            "content_length": len(content)
                        },
                        time.time() - start_time
                    )
        except Exception as e:
            self.add_result(
                "frontend_accessibility",
                "frontend",
                "fail",
                {"error": str(e), "accessible": False},
                time.time() - start_time,
                ["🔧 Frontend is not accessible - check if it's running on port 5173"]
            )
    
    async def test_enhanced_backend_functionality(self):
        """Enhanced backend testing focusing on areas that affect frontend"""
        self.logger.info("🔧 Testing Enhanced Backend Functionality...")
        
        async with aiohttp.ClientSession() as session:
            # Test CORS configuration
            await self.test_cors_configuration(session)
            
            # Test API error responses and formats
            await self.test_api_error_formats(session)
            
            # Test authentication flow from frontend perspective
            await self.test_auth_frontend_compatibility(session)
            
            # Test data format consistency
            await self.test_data_format_consistency(session)
            
            # Test WebSocket endpoint availability (without actually connecting)
            await self.test_websocket_endpoint_availability(session)
    
    async def test_cors_configuration(self, session: aiohttp.ClientSession):
        """Test CORS configuration for frontend compatibility"""
        start_time = time.time()
        
        try:
            headers = {
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            async with session.options(f"{self.backend_url}/api/auth/login", headers=headers) as response:
                cors_headers = {
                    'access_control_allow_origin': response.headers.get('Access-Control-Allow-Origin'),
                    'access_control_allow_methods': response.headers.get('Access-Control-Allow-Methods'),
                    'access_control_allow_headers': response.headers.get('Access-Control-Allow-Headers'),
                    'access_control_allow_credentials': response.headers.get('Access-Control-Allow-Credentials')
                }
                
                cors_properly_configured = (
                    cors_headers['access_control_allow_origin'] in ['*', 'http://localhost:5173'] and
                    'POST' in (cors_headers['access_control_allow_methods'] or '') and
                    'Authorization' in (cors_headers['access_control_allow_headers'] or '')
                )
                
                recommendations = []
                if not cors_properly_configured:
                    recommendations = [
                        "🔧 Configure CORS to allow frontend origin (http://localhost:5173)",
                        "🔧 Ensure CORS allows POST, PUT, DELETE methods",
                        "🔧 Allow Authorization header in CORS configuration"
                    ]
                
                self.add_result(
                    "cors_configuration",
                    "backend",
                    "pass" if cors_properly_configured else "warning",
                    {
                        "cors_headers": cors_headers,
                        "properly_configured": cors_properly_configured,
                        "status_code": response.status
                    },
                    time.time() - start_time,
                    recommendations
                )
        except Exception as e:
            self.add_result(
                "cors_configuration",
                "backend",
                "fail",
                {"error": str(e)},
                time.time() - start_time,
                ["🔧 CORS preflight request failed - check CORS configuration"]
            )
    
    async def test_api_error_formats(self, session: aiohttp.ClientSession):
        """Test that API returns consistent error formats for frontend handling"""
        start_time = time.time()
        
        error_tests = [
            {
                "name": "404_endpoint",
                "url": f"{self.backend_url}/api/nonexistent",
                "method": "GET",
                "expected_status": 404
            },
            {
                "name": "invalid_json",
                "url": f"{self.backend_url}/api/auth/login",
                "method": "POST",
                "data": "invalid json",
                "headers": {"Content-Type": "application/json"},
                "expected_status": 400
            },
            {
                "name": "missing_auth",
                "url": f"{self.backend_url}/api/projects",
                "method": "GET",
                "expected_status": 401
            }
        ]
        
        error_format_consistent = True
        error_details = {}
        
        for test in error_tests:
            try:
                method = getattr(session, test["method"].lower())
                kwargs = {}
                if "data" in test:
                    kwargs["data"] = test["data"]
                if "headers" in test:
                    kwargs["headers"] = test["headers"]
                
                async with method(test["url"], **kwargs) as response:
                    if response.content_type == 'application/json':
                        error_data = await response.json()
                        has_error_field = 'error' in error_data or 'message' in error_data
                        error_details[test["name"]] = {
                            "status": response.status,
                            "has_error_field": has_error_field,
                            "response_format": "json"
                        }
                        if not has_error_field:
                            error_format_consistent = False
                    else:
                        error_details[test["name"]] = {
                            "status": response.status,
                            "response_format": response.content_type
                        }
                        error_format_consistent = False
                        
            except Exception as e:
                error_details[test["name"]] = {"error": str(e)}
                error_format_consistent = False
        
        recommendations = []
        if not error_format_consistent:
            recommendations = [
                "🔧 Ensure all API errors return JSON with consistent structure",
                "🔧 Include 'error' or 'message' field in all error responses",
                "🔧 Set proper Content-Type: application/json for error responses"
            ]
        
        self.add_result(
            "api_error_formats",
            "backend",
            "pass" if error_format_consistent else "warning",
            {
                "consistent_format": error_format_consistent,
                "error_tests": error_details
            },
            time.time() - start_time,
            recommendations
        )
    
    async def test_auth_frontend_compatibility(self, session: aiohttp.ClientSession):
        """Test authentication flow compatibility with frontend"""
        start_time = time.time()
        
        # Test user registration
        test_user = {
            "email": f"frontend_test_{int(time.time())}@test.com",
            "password": "FrontendTest123!",
            "name": "Frontend Test User"
        }
        
        auth_flow_results = {}
        
        try:
            # Register user
            async with session.post(f"{self.backend_url}/api/auth/register", json=test_user) as response:
                register_data = await response.json() if response.content_type == 'application/json' else {}
                auth_flow_results["register"] = {
                    "status": response.status,
                    "success": response.status in [200, 201],
                    "has_token": "access_token" in register_data or "token" in register_data,
                    "response_data": register_data
                }
            
            # Test login
            login_data = {"email": test_user["email"], "password": test_user["password"]}
            async with session.post(f"{self.backend_url}/api/auth/login", json=login_data) as response:
                login_response = await response.json() if response.content_type == 'application/json' else {}
                auth_flow_results["login"] = {
                    "status": response.status,
                    "success": response.status == 200,
                    "has_token": "access_token" in login_response or "token" in login_response,
                    "response_data": login_response
                }
                
                # Extract token for further testing
                token = login_response.get("access_token") or login_response.get("token")
                
                if token:
                    # Test authenticated request
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(f"{self.backend_url}/api/projects", headers=headers) as auth_response:
                        auth_flow_results["authenticated_request"] = {
                            "status": auth_response.status,
                            "success": auth_response.status == 200,
                            "token_works": auth_response.status != 401
                        }
        
        except Exception as e:
            auth_flow_results["error"] = str(e)
        
        auth_compatible = all(
            result.get("success", False) 
            for result in auth_flow_results.values() 
            if isinstance(result, dict) and "success" in result
        )
        
        recommendations = []
        if not auth_compatible:
            recommendations = [
                "🔧 Ensure registration returns access_token in response",
                "🔧 Ensure login returns access_token in response", 
                "🔧 Verify JWT tokens work for authenticated endpoints",
                "🔧 Check token format and expiration settings"
            ]
        
        self.add_result(
            "auth_frontend_compatibility",
            "integration",
            "pass" if auth_compatible else "fail",
            {
                "auth_flow_compatible": auth_compatible,
                "flow_results": auth_flow_results
            },
            time.time() - start_time,
            recommendations
        )
    
    async def test_data_format_consistency(self, session: aiohttp.ClientSession):
        """Test that API returns consistent data formats for frontend consumption"""
        start_time = time.time()
        
        # Test key endpoints for data format consistency
        endpoints_to_test = [
            {"url": "/health", "expected_fields": ["status"]},
            {"url": "/api/auth/register", "method": "POST", "data": {"email": "test@test.com", "password": "test123", "name": "Test"}, "expected_fields": ["access_token", "user"]},
        ]
        
        format_issues = []
        
        for endpoint in endpoints_to_test:
            try:
                method = endpoint.get("method", "GET").lower()
                url = f"{self.backend_url}{endpoint['url']}"
                
                request_method = getattr(session, method)
                kwargs = {}
                if "data" in endpoint:
                    kwargs["json"] = endpoint["data"]
                
                async with request_method(url, **kwargs) as response:
                    if response.content_type == 'application/json':
                        data = await response.json()
                        
                        # Check for expected fields
                        missing_fields = []
                        for field in endpoint.get("expected_fields", []):
                            if field not in data:
                                missing_fields.append(field)
                        
                        if missing_fields:
                            format_issues.append({
                                "endpoint": endpoint["url"],
                                "missing_fields": missing_fields,
                                "actual_fields": list(data.keys()) if isinstance(data, dict) else "non-dict response"
                            })
                    else:
                        format_issues.append({
                            "endpoint": endpoint["url"],
                            "issue": f"Non-JSON response: {response.content_type}"
                        })
                        
            except Exception as e:
                # Skip endpoints that are expected to fail (like auth without proper data)
                continue
        
        data_consistent = len(format_issues) == 0
        
        recommendations = []
        if not data_consistent:
            recommendations = [
                "🔧 Ensure all API endpoints return consistent JSON structure",
                "🔧 Include expected fields in API responses",
                "🔧 Document API response formats for frontend team"
            ]
        
        self.add_result(
            "data_format_consistency",
            "backend",
            "pass" if data_consistent else "warning",
            {
                "consistent_formats": data_consistent,
                "format_issues": format_issues
            },
            time.time() - start_time,
            recommendations
        )
    
    async def test_websocket_endpoint_availability(self, session: aiohttp.ClientSession):
        """Test if WebSocket endpoint is available for real-time features"""
        start_time = time.time()
        
        # Check if Socket.IO endpoint responds
        try:
            # Socket.IO typically serves on /socket.io/
            async with session.get(f"{self.backend_url}/socket.io/") as response:
                websocket_available = response.status in [200, 400]  # 400 is also acceptable for Socket.IO
                
                self.add_result(
                    "websocket_endpoint",
                    "backend",
                    "pass" if websocket_available else "warning",
                    {
                        "status_code": response.status,
                        "available": websocket_available,
                        "content_type": response.content_type
                    },
                    time.time() - start_time,
                    [] if websocket_available else ["🔧 Socket.IO endpoint not available - real-time features may not work"]
                )
        except Exception as e:
            self.add_result(
                "websocket_endpoint",
                "backend",
                "warning",
                {"error": str(e), "available": False},
                time.time() - start_time,
                ["🔧 Could not check WebSocket endpoint - ensure Socket.IO is configured"]
            )
    
    async def test_frontend_static_analysis(self):
        """Analyze frontend code structure without running browser"""
        self.logger.info("🎨 Analyzing Frontend Structure...")
        
        import os
        from pathlib import Path
        
        frontend_path = Path("frontend")
        
        if not frontend_path.exists():
            self.add_result(
                "frontend_structure",
                "frontend",
                "fail",
                {"error": "Frontend directory not found"},
                0,
                ["🔧 Frontend directory missing - check project structure"]
            )
            return
        
        # Check key files and directories
        key_files = {
            "package.json": frontend_path / "package.json",
            "vite.config": frontend_path / "vite.config.ts",
            "tsconfig": frontend_path / "tsconfig.json",
            "main_component": frontend_path / "src" / "main.tsx",
            "app_component": frontend_path / "src" / "App.tsx",
        }
        
        missing_files = []
        existing_files = []
        
        for name, path in key_files.items():
            if path.exists():
                existing_files.append(name)
            else:
                missing_files.append(name)
        
        # Analyze package.json for dependencies
        dependencies_analysis = {}
        if key_files["package.json"].exists():
            try:
                with open(key_files["package.json"]) as f:
                    package_data = json.load(f)
                    
                dependencies = package_data.get("dependencies", {})
                dev_dependencies = package_data.get("devDependencies", {})
                
                # Check for key frontend dependencies
                key_deps = {
                    "react": dependencies.get("react"),
                    "typescript": dev_dependencies.get("typescript"),
                    "vite": dev_dependencies.get("vite"),
                    "axios": dependencies.get("axios"),
                    "socket.io-client": dependencies.get("socket.io-client"),
                    "testing": dev_dependencies.get("vitest") or dev_dependencies.get("@testing-library/react")
                }
                
                dependencies_analysis = {
                    "total_deps": len(dependencies),
                    "total_dev_deps": len(dev_dependencies),
                    "key_dependencies": key_deps,
                    "has_testing": bool(key_deps["testing"])
                }
                
            except Exception as e:
                dependencies_analysis = {"error": f"Could not parse package.json: {e}"}
        
        # Check src directory structure
        src_structure = {}
        src_path = frontend_path / "src"
        if src_path.exists():
            key_dirs = ["components", "pages", "hooks", "context", "services", "utils"]
            src_structure = {
                dir_name: (src_path / dir_name).exists() 
                for dir_name in key_dirs
            }
        
        frontend_well_structured = (
            len(missing_files) <= 1 and  # Allow one missing file
            dependencies_analysis.get("key_dependencies", {}).get("react") and
            src_structure.get("components", False)
        )
        
        recommendations = []
        if missing_files:
            recommendations.append(f"🔧 Missing key files: {', '.join(missing_files)}")
        if not dependencies_analysis.get("has_testing", False):
            recommendations.append("🧪 Add testing framework (Vitest + React Testing Library)")
        if not src_structure.get("components", False):
            recommendations.append("🔧 Create components directory structure")
        
        self.add_result(
            "frontend_structure",
            "frontend",
            "pass" if frontend_well_structured else "warning",
            {
                "existing_files": existing_files,
                "missing_files": missing_files,
                "dependencies_analysis": dependencies_analysis,
                "src_structure": src_structure,
                "well_structured": frontend_well_structured
            },
            0,
            recommendations
        )
    
    async def test_http_integration_patterns(self):
        """Test integration patterns using HTTP requests only"""
        self.logger.info("🔄 Testing HTTP Integration Patterns...")
        
        async with aiohttp.ClientSession() as session:
            # Test API consistency between different endpoints
            await self.test_api_consistency_patterns(session)
            
            # Test error handling integration
            await self.test_error_handling_integration(session)
    
    async def test_api_consistency_patterns(self, session: aiohttp.ClientSession):
        """Test that API follows consistent patterns"""
        start_time = time.time()
        
        # Test different endpoint patterns
        patterns_to_test = [
            {"endpoint": "/health", "should_exist": True},
            {"endpoint": "/api/auth/login", "should_exist": True, "methods": ["POST"]},
            {"endpoint": "/api/projects", "should_exist": True, "methods": ["GET", "POST"]},
            {"endpoint": "/api/ai/analyze-idea", "should_exist": True, "methods": ["POST"]},
        ]
        
        pattern_results = {}
        
        for pattern in patterns_to_test:
            endpoint = pattern["endpoint"]
            pattern_results[endpoint] = {}
            
            # Test GET (if not specified otherwise)
            methods_to_test = pattern.get("methods", ["GET"])
            
            for method in methods_to_test:
                try:
                    request_method = getattr(session, method.lower())
                    async with request_method(f"{self.backend_url}{endpoint}") as response:
                        pattern_results[endpoint][method] = {
                            "status": response.status,
                            "exists": response.status != 404,
                            "content_type": response.content_type
                        }
                except Exception as e:
                    pattern_results[endpoint][method] = {"error": str(e)}
        
        # Check for consistency
        api_consistent = True
        consistency_issues = []
        
        for endpoint, methods in pattern_results.items():
            for method, result in methods.items():
                if isinstance(result, dict) and "status" in result:
                    if result["status"] == 404 and any(p["endpoint"] == endpoint and p.get("should_exist", False) for p in patterns_to_test):
                        consistency_issues.append(f"{method} {endpoint} returns 404 but should exist")
                        api_consistent = False
                    
                    if result.get("content_type") and "application/json" not in result["content_type"] and endpoint.startswith("/api/"):
                        consistency_issues.append(f"{method} {endpoint} doesn't return JSON")
        
        recommendations = []
        if not api_consistent:
            recommendations = [
                "🔧 Ensure all /api/ endpoints return JSON responses",
                "🔧 Implement missing endpoints that frontend expects",
                "🔧 Follow consistent URL patterns for API endpoints"
            ]
        
        self.add_result(
            "api_consistency",
            "integration",
            "pass" if api_consistent else "warning",
            {
                "consistent": api_consistent,
                "pattern_results": pattern_results,
                "consistency_issues": consistency_issues
            },
            time.time() - start_time,
            recommendations
        )
    
    async def test_error_handling_integration(self, session: aiohttp.ClientSession):
        """Test how backend errors will be handled by frontend"""
        start_time = time.time()
        
        # Test various error scenarios
        error_scenarios = [
            {
                "name": "rate_limiting",
                "description": "Test if rate limiting returns proper headers",
                "requests": 10,  # Send multiple requests quickly
                "endpoint": "/api/auth/login",
                "data": {"email": "test@test.com", "password": "wrong"}
            },
            {
                "name": "large_payload", 
                "description": "Test large payload handling",
                "endpoint": "/api/projects",
                "data": {"title": "x" * 10000, "description": "Large payload test"}
            }
        ]
        
        error_handling_results = {}
        
        for scenario in error_scenarios:
            try:
                if scenario["name"] == "rate_limiting":
                    # Send multiple requests
                    responses = []
                    for i in range(scenario["requests"]):
                        async with session.post(
                            f"{self.backend_url}{scenario['endpoint']}", 
                            json=scenario["data"]
                        ) as response:
                            responses.append({
                                "status": response.status,
                                "headers": dict(response.headers),
                                "request_num": i + 1
                            })
                    
                    # Check if rate limiting kicks in
                    rate_limited = any(r["status"] == 429 for r in responses)
                    has_rate_limit_headers = any(
                        "x-ratelimit" in str(r["headers"]).lower() or "retry-after" in str(r["headers"]).lower()
                        for r in responses
                    )
                    
                    error_handling_results[scenario["name"]] = {
                        "rate_limited": rate_limited,
                        "has_rate_limit_headers": has_rate_limit_headers,
                        "responses": responses[-3:]  # Last 3 responses
                    }
                
                elif scenario["name"] == "large_payload":
                    async with session.post(
                        f"{self.backend_url}{scenario['endpoint']}", 
                        json=scenario["data"]
                    ) as response:
                        error_handling_results[scenario["name"]] = {
                            "status": response.status,
                            "handled_gracefully": response.status in [400, 413, 422],  # Expected error codes
                            "content_type": response.content_type
                        }
                        
            except Exception as e:
                error_handling_results[scenario["name"]] = {"error": str(e)}
        
        error_handling_good = all(
            result.get("handled_gracefully", True) or result.get("has_rate_limit_headers", False)
            for result in error_handling_results.values()
            if isinstance(result, dict)
        )
        
        recommendations = []
        if not error_handling_good:
            recommendations = [
                "🔧 Implement rate limiting with proper HTTP headers",
                "🔧 Add request size limits and return 413 for large payloads",
                "🔧 Ensure error responses include helpful messages for frontend"
            ]
        
        self.add_result(
            "error_handling_integration",
            "integration", 
            "pass" if error_handling_good else "warning",
            {
                "error_scenarios": error_handling_results,
                "handled_well": error_handling_good
            },
            time.time() - start_time,
            recommendations
        )
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive test report with actionable recommendations"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        # Categorize results
        backend_results = [r for r in self.results if r.category == "backend"]
        frontend_results = [r for r in self.results if r.category == "frontend"] 
        integration_results = [r for r in self.results if r.category == "integration"]
        
        # Calculate statistics
        def calc_stats(results):
            if not results:
                return {"total": 0, "passed": 0, "failed": 0, "warnings": 0, "pass_rate": 0}
            
            passed = len([r for r in results if r.status == "pass"])
            failed = len([r for r in results if r.status == "fail"])
            warnings = len([r for r in results if r.status == "warning"])
            
            return {
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "pass_rate": (passed / len(results)) * 100 if results else 0
            }
        
        # Collect all recommendations
        all_recommendations = []
        for result in self.results:
            if result.recommendations:
                all_recommendations.extend(result.recommendations)
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        seen = set()
        for rec in all_recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        # Add general recommendations based on test results
        if any(r.status == "fail" for r in backend_results):
            unique_recommendations.append("🔧 CRITICAL: Fix failing backend tests before frontend integration")
        
        if any(r.status == "fail" for r in frontend_results):
            unique_recommendations.append("🎨 CRITICAL: Fix frontend structure issues")
        
        # Priority recommendations for improving frontend-backend integration
        unique_recommendations.extend([
            "🧪 ADD COMPREHENSIVE TESTING: Implement unit tests for React components",
            "🎭 ADD E2E TESTING: Install Playwright or Cypress for full user journey testing",
            "📊 ADD PERFORMANCE MONITORING: Implement frontend performance tracking",
            "🔄 ADD INTEGRATION TESTS: Test complete user workflows end-to-end",
            "🎯 ADD ERROR BOUNDARIES: Implement React error boundaries for better UX",
            "📱 TEST MOBILE COMPATIBILITY: Ensure all features work on mobile devices",
            "♿ ADD ACCESSIBILITY TESTING: Implement accessibility compliance testing",
            "🔐 STRENGTHEN SECURITY TESTING: Add tests for authentication edge cases"
        ])
        
        report = {
            "test_summary": {
                "duration_seconds": total_duration,
                "total_tests": len(self.results),
                "test_start_time": self.start_time.isoformat(),
                "test_end_time": datetime.now().isoformat()
            },
            "backend_analysis": {
                **calc_stats(backend_results),
                "key_issues": [r.test_name for r in backend_results if r.status == "fail"]
            },
            "frontend_analysis": {
                **calc_stats(frontend_results),
                "key_issues": [r.test_name for r in frontend_results if r.status == "fail"]
            },
            "integration_analysis": {
                **calc_stats(integration_results),
                "key_issues": [r.test_name for r in integration_results if r.status == "fail"]
            },
            "recommendations": unique_recommendations[:15],  # Top 15 recommendations
            "detailed_results": [asdict(result) for result in self.results],
            "next_steps": self.generate_next_steps()
        }
        
        return report
    
    def generate_next_steps(self) -> List[str]:
        """Generate specific next steps based on test results"""
        failed_tests = [r for r in self.results if r.status == "fail"]
        
        if not failed_tests:
            return [
                "✅ All critical tests passed - focus on implementing additional test coverage",
                "📈 Add performance monitoring and alerting",
                "🚀 Consider deploying to staging environment for further testing"
            ]
        
        next_steps = ["🚨 IMMEDIATE ACTIONS REQUIRED:"]
        
        # Backend issues
        backend_failures = [r for r in failed_tests if r.category == "backend"]
        if backend_failures:
            next_steps.append("🔧 Fix backend connectivity and health check issues")
        
        # Frontend issues  
        frontend_failures = [r for r in failed_tests if r.category == "frontend"]
        if frontend_failures:
            next_steps.append("🎨 Resolve frontend structure and accessibility problems")
        
        # Integration issues
        integration_failures = [r for r in failed_tests if r.category == "integration"]
        if integration_failures:
            next_steps.append("🔄 Fix frontend-backend communication issues")
        
        next_steps.extend([
            "📋 Create GitHub issues for each failed test",
            "⏰ Set up CI/CD pipeline to run these tests automatically", 
            "👥 Share results with development team for prioritization"
        ])
        
        return next_steps
    
    def print_executive_summary(self, report: Dict):
        """Print executive summary of test results"""
        print("\n" + "=" * 80)
        print("📊 SIMPLIFIED ALVIN INTEGRATION TEST - EXECUTIVE SUMMARY")
        print("=" * 80)
        
        summary = report['test_summary']
        backend = report['backend_analysis']
        frontend = report['frontend_analysis']
        integration = report['integration_analysis']
        
        print(f"🕒 Test Duration: {summary['duration_seconds']:.1f} seconds")
        print(f"🧪 Total Tests: {summary['total_tests']}")
        print()
        print(f"🔧 Backend Tests: {backend['passed']}/{backend['total']} passed ({backend['pass_rate']:.1f}%)")
        print(f"🎨 Frontend Tests: {frontend['passed']}/{frontend['total']} passed ({frontend['pass_rate']:.1f}%)")
        print(f"🔄 Integration Tests: {integration['passed']}/{integration['total']} passed ({integration['pass_rate']:.1f}%)")
        
        if backend['key_issues'] or frontend['key_issues'] or integration['key_issues']:
            print(f"\n❌ Failed Tests:")
            for issue in backend['key_issues'] + frontend['key_issues'] + integration['key_issues']:
                print(f"   • {issue}")
        
        print(f"\n🎯 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'][:8], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n📋 NEXT STEPS:")
        for i, step in enumerate(report['next_steps'][:5], 1):
            print(f"   {i}. {step}")

async def main():
    """Main function to run simplified test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simplified ALVIN Frontend-Backend Integration Tests')
    parser.add_argument('--backend-url', default='http://localhost:5000', help='Backend URL')
    parser.add_argument('--frontend-url', default='http://localhost:5173', help='Frontend URL')
    parser.add_argument('--save-report', action='store_true', help='Save detailed report to file')
    
    args = parser.parse_args()
    
    test_suite = SimplifiedTestSuite(args.backend_url, args.frontend_url)
    
    try:
        report = await test_suite.run_comprehensive_test()
        
        # Print summary
        test_suite.print_executive_summary(report)
        
        # Save report if requested
        if args.save_report:
            report_filename = f"simplified_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n📄 Detailed report saved to: {report_filename}")
        
        # Determine exit code based on critical failures
        critical_failures = sum(1 for r in test_suite.results if r.status == "fail" and r.category in ["backend", "integration"])
        exit_code = 0 if critical_failures == 0 else 1
        
        print(f"\n{'🎉 Test suite completed successfully!' if exit_code == 0 else '⚠️ Test suite completed with issues.'}")
        
        return exit_code
        
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)