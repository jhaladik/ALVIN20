#!/usr/bin/env python3
"""
ALVIN Frontend Simulation Test
Comprehensive test that simulates frontend interactions to validate and optimize backend
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
from pathlib import Path
import statistics
import concurrent.futures
from threading import Thread
import psutil
import sys

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'alvin_simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

@dataclass
class TestMetrics:
    endpoint: str
    method: str
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    timestamp: datetime
    user_id: Optional[str] = None
    error_message: Optional[str] = None
    additional_data: Optional[Dict] = None

@dataclass
class UserSession:
    user_id: str
    email: str
    access_token: str
    projects: List[Dict] = None
    scenes: List[Dict] = None
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    
    def __post_init__(self):
        if self.projects is None:
            self.projects = []
        if self.scenes is None:
            self.scenes = []

class FrontendSimulator:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.sessions: List[UserSession] = []
        self.metrics: List[TestMetrics] = []
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()
        
        # Test data generators
        self.story_ideas = [
            "A detective discovers that the serial killer they're hunting is actually their future self from a parallel timeline",
            "In a world where memories can be extracted and sold, a memory thief finds a memory that doesn't belong to anyone",
            "A small town baker realizes their bread recipes are actually ancient spells that grant wishes to those who eat them",
            "An AI therapist becomes self-aware and starts manipulating patients to create the perfect human being",
            "A librarian finds books that write themselves, but each new chapter changes reality to match the story",
            "Time moves backwards in a small village, and only the newcomer remembers how things used to be",
            "A social media influencer's followers start disappearing from real life whenever they unfollow online",
            "A child's imaginary friend turns out to be a quantum physicist trapped between dimensions",
            "Every lie told in a courthouse manifests as a physical creature that haunts the liar",
            "A dating app matches people with their worst possible life decisions personified as romantic partners"
        ]
        
        self.project_titles = [
            "The Quantum Detective", "Memory Merchants", "The Enchanted Bakery",
            "Digital Therapy", "The Living Library", "Backwards Village",
            "Vanishing Followers", "Dimensional Friends", "Courthouse Creatures",
            "Dating Your Demons"
        ]
        
        self.scene_types = ['opening', 'inciting', 'development', 'climax', 'resolution', 'transition']
        
    async def make_request(self, session: aiohttp.ClientSession, method: str, endpoint: str, 
                          headers: Dict = None, data: Dict = None, user_session: UserSession = None) -> Tuple[Dict, TestMetrics]:
        """Make HTTP request and collect metrics"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        request_size = len(json.dumps(data)) if data else 0
        
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        try:
            async with session.request(method, url, headers=default_headers, json=data) as response:
                response_text = await response.text()
                response_time = time.time() - start_time
                
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {'raw_response': response_text}
                
                metrics = TestMetrics(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status,
                    response_time=response_time,
                    request_size=request_size,
                    response_size=len(response_text),
                    timestamp=datetime.now(),
                    user_id=user_session.user_id if user_session else None,
                    error_message=response_data.get('message') if response.status >= 400 else None,
                    additional_data={'url': url, 'headers': dict(response.headers)}
                )
                
                self.metrics.append(metrics)
                
                if user_session:
                    user_session.total_operations += 1
                    if response.status < 400:
                        user_session.successful_operations += 1
                    else:
                        user_session.failed_operations += 1
                
                return response_data, metrics
                
        except Exception as e:
            response_time = time.time() - start_time
            metrics = TestMetrics(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                request_size=request_size,
                response_size=0,
                timestamp=datetime.now(),
                user_id=user_session.user_id if user_session else None,
                error_message=str(e),
                additional_data={'error_type': type(e).__name__}
            )
            
            self.metrics.append(metrics)
            
            if user_session:
                user_session.total_operations += 1
                user_session.failed_operations += 1
            
            return {'error': str(e)}, metrics

    async def test_basic_health_check(self, session: aiohttp.ClientSession) -> bool:
        """Test basic connectivity"""
        self.logger.info("🔍 Testing basic connectivity...")
        
        response, metrics = await self.make_request(session, 'GET', '/health')
        
        if metrics.status_code == 200:
            self.logger.info(f"✅ Health check passed ({metrics.response_time:.3f}s)")
            return True
        else:
            self.logger.error(f"❌ Health check failed: {metrics.error_message}")
            return False

    async def create_test_user(self, session: aiohttp.ClientSession, user_id: str) -> Optional[UserSession]:
        """Create and authenticate a test user"""
        self.logger.info(f"👤 Creating test user: {user_id}")
        
        email = f"test_user_{user_id}@alvin-test.com"
        password = f"TestPass123_{user_id}"
        
        # Try to register user
        register_data = {
            "email": email,
            "password": password,
            "confirm_password": password,
            "name": f"Test User {user_id}",
            "accept_terms": True
        }
        
        response, metrics = await self.make_request(session, 'POST', '/api/auth/register', data=register_data)
        
        # If registration fails (user exists), try login
        if metrics.status_code != 201:
            self.logger.info(f"User {email} might exist, trying login...")
        
        # Login
        login_data = {"email": email, "password": password}
        response, metrics = await self.make_request(session, 'POST', '/api/auth/login', data=login_data)
        
        if metrics.status_code == 200 and 'access_token' in response:
            user_session = UserSession(
                user_id=user_id,
                email=email,
                access_token=response['access_token']
            )
            self.sessions.append(user_session)
            self.logger.info(f"✅ User {email} authenticated successfully")
            return user_session
        else:
            self.logger.error(f"❌ Failed to authenticate user {email}: {metrics.error_message}")
            return None

    async def test_ai_operations(self, session: aiohttp.ClientSession, user_session: UserSession) -> Dict:
        """Test AI-related operations"""
        self.logger.info(f"🤖 Testing AI operations for user {user_session.email}")
        
        headers = {'Authorization': f'Bearer {user_session.access_token}'}
        results = {}
        
        # Test idea analysis
        idea = random.choice(self.story_ideas)
        idea_data = {
            "idea_text": idea,
            "target_audience": random.choice(["Young Adult", "Adult", "Children"]),
            "preferred_genre": random.choice(["Mystery", "Fantasy", "Sci-Fi", "Romance", "Thriller"])
        }
        
        response, metrics = await self.make_request(
            session, 'POST', '/api/ai/analyze-idea', 
            headers=headers, data=idea_data, user_session=user_session
        )
        
        results['idea_analysis'] = {
            'success': metrics.status_code == 200,
            'response_time': metrics.response_time,
            'data': response
        }
        
        if metrics.status_code == 200:
            # Test project creation from idea
            project_data = {
                "idea_text": idea,
                "title": random.choice(self.project_titles)
            }
            
            response, metrics = await self.make_request(
                session, 'POST', '/api/ai/create-project-from-idea',
                headers=headers, data=project_data, user_session=user_session
            )
            
            results['project_from_idea'] = {
                'success': metrics.status_code == 201,
                'response_time': metrics.response_time,
                'data': response
            }
            
            if metrics.status_code == 201 and 'project' in response:
                project = response['project']
                user_session.projects.append(project)
                
                # Test project-specific AI operations
                project_id = project['id']
                
                # Test structure analysis
                response, metrics = await self.make_request(
                    session, 'POST', f'/api/ai/projects/{project_id}/analyze-structure',
                    headers=headers, data={}, user_session=user_session
                )
                
                results['structure_analysis'] = {
                    'success': metrics.status_code == 200,
                    'response_time': metrics.response_time
                }
                
                # Test scene suggestions
                response, metrics = await self.make_request(
                    session, 'POST', f'/api/ai/projects/{project_id}/suggest-scenes',
                    headers=headers, data={'count': 3}, user_session=user_session
                )
                
                results['scene_suggestions'] = {
                    'success': metrics.status_code == 200,
                    'response_time': metrics.response_time
                }
        
        return results

    async def test_project_operations(self, session: aiohttp.ClientSession, user_session: UserSession) -> Dict:
        """Test project management operations"""
        self.logger.info(f"📚 Testing project operations for user {user_session.email}")
        
        headers = {'Authorization': f'Bearer {user_session.access_token}'}
        results = {}
        
        # Get existing projects
        response, metrics = await self.make_request(
            session, 'GET', '/api/projects',
            headers=headers, user_session=user_session
        )
        
        results['list_projects'] = {
            'success': metrics.status_code == 200,
            'response_time': metrics.response_time,
            'count': len(response.get('projects', [])) if metrics.status_code == 200 else 0
        }
        
        # Create a new project
        project_data = {
            "title": f"Test Project {uuid.uuid4().hex[:8]}",
            "description": "A test project created during simulation",
            "genre": random.choice(["Fantasy", "Mystery", "Sci-Fi", "Romance"]),
            "target_audience": random.choice(["Young Adult", "Adult", "Children"]),
            "expected_length": random.choice(["short", "medium", "long"])
        }
        
        response, metrics = await self.make_request(
            session, 'POST', '/api/projects',
            headers=headers, data=project_data, user_session=user_session
        )
        
        results['create_project'] = {
            'success': metrics.status_code == 201,
            'response_time': metrics.response_time,
            'data': response
        }
        
        if metrics.status_code == 201 and 'project' in response:
            project = response['project']
            user_session.projects.append(project)
            project_id = project['id']
            
            # Test project retrieval
            response, metrics = await self.make_request(
                session, 'GET', f'/api/projects/{project_id}',
                headers=headers, user_session=user_session
            )
            
            results['get_project'] = {
                'success': metrics.status_code == 200,
                'response_time': metrics.response_time
            }
            
            # Test project update
            update_data = {
                "description": f"Updated description at {datetime.now()}",
                "status": "active"
            }
            
            response, metrics = await self.make_request(
                session, 'PUT', f'/api/projects/{project_id}',
                headers=headers, data=update_data, user_session=user_session
            )
            
            results['update_project'] = {
                'success': metrics.status_code == 200,
                'response_time': metrics.response_time
            }
        
        return results

    async def test_scene_operations(self, session: aiohttp.ClientSession, user_session: UserSession) -> Dict:
        """Test scene management operations"""
        self.logger.info(f"🎬 Testing scene operations for user {user_session.email}")
        
        headers = {'Authorization': f'Bearer {user_session.access_token}'}
        results = {}
        
        if not user_session.projects:
            return {'error': 'No projects available for scene testing'}
        
        project = user_session.projects[0]
        project_id = project['id']
        
        # Create multiple scenes
        scene_count = random.randint(3, 7)
        created_scenes = []
        
        for i in range(scene_count):
            scene_data = {
                "title": f"Scene {i+1}: {uuid.uuid4().hex[:8]}",
                "description": f"Test scene {i+1} description",
                "content": f"This is the content for scene {i+1}. " * random.randint(10, 50),
                "scene_type": random.choice(self.scene_types),
                "emotional_intensity": random.uniform(0.1, 0.9),
                "project_id": project_id,
                "order_index": i
            }
            
            response, metrics = await self.make_request(
                session, 'POST', '/api/scenes',
                headers=headers, data=scene_data, user_session=user_session
            )
            
            if metrics.status_code == 201 and 'scene' in response:
                created_scenes.append(response['scene'])
        
        results['create_scenes'] = {
            'success': len(created_scenes) > 0,
            'count': len(created_scenes),
            'avg_response_time': statistics.mean([m.response_time for m in self.metrics[-scene_count:]])
        }
        
        user_session.scenes.extend(created_scenes)
        
        # Test scene listing
        response, metrics = await self.make_request(
            session, 'GET', f'/api/scenes?project_id={project_id}',
            headers=headers, user_session=user_session
        )
        
        results['list_scenes'] = {
            'success': metrics.status_code == 200,
            'response_time': metrics.response_time,
            'count': len(response.get('scenes', [])) if metrics.status_code == 200 else 0
        }
        
        # Test scene updates
        if created_scenes:
            scene = created_scenes[0]
            scene_id = scene['id']
            
            update_data = {
                "content": f"Updated content at {datetime.now()}",
                "status": "completed"
            }
            
            response, metrics = await self.make_request(
                session, 'PUT', f'/api/scenes/{scene_id}',
                headers=headers, data=update_data, user_session=user_session
            )
            
            results['update_scene'] = {
                'success': metrics.status_code == 200,
                'response_time': metrics.response_time
            }
        
        return results

    async def test_analytics_endpoints(self, session: aiohttp.ClientSession, user_session: UserSession) -> Dict:
        """Test analytics and reporting endpoints"""
        self.logger.info(f"📊 Testing analytics for user {user_session.email}")
        
        headers = {'Authorization': f'Bearer {user_session.access_token}'}
        results = {}
        
        # Test dashboard analytics
        response, metrics = await self.make_request(
            session, 'GET', '/api/analytics/dashboard',
            headers=headers, user_session=user_session
        )
        
        results['dashboard'] = {
            'success': metrics.status_code == 200,
            'response_time': metrics.response_time,
            'data': response if metrics.status_code == 200 else None
        }
        
        return results

    async def test_error_handling(self, session: aiohttp.ClientSession, user_session: UserSession) -> Dict:
        """Test error handling and edge cases"""
        self.logger.info(f"⚠️ Testing error handling for user {user_session.email}")
        
        headers = {'Authorization': f'Bearer {user_session.access_token}'}
        results = {}
        
        # Test invalid endpoints
        response, metrics = await self.make_request(
            session, 'GET', '/api/nonexistent',
            headers=headers, user_session=user_session
        )
        
        results['invalid_endpoint'] = {
            'returns_404': metrics.status_code == 404,
            'response_time': metrics.response_time
        }
        
        # Test invalid project access
        fake_project_id = str(uuid.uuid4())
        response, metrics = await self.make_request(
            session, 'GET', f'/api/projects/{fake_project_id}',
            headers=headers, user_session=user_session
        )
        
        results['invalid_project'] = {
            'returns_404': metrics.status_code == 404,
            'response_time': metrics.response_time
        }
        
        # Test malformed data
        response, metrics = await self.make_request(
            session, 'POST', '/api/projects',
            headers=headers, data={'invalid': 'data'}, user_session=user_session
        )
        
        results['malformed_data'] = {
            'returns_400': metrics.status_code == 400,
            'response_time': metrics.response_time
        }
        
        # Test unauthorized access
        response, metrics = await self.make_request(
            session, 'GET', '/api/projects',
            headers={}, user_session=user_session
        )
        
        results['unauthorized'] = {
            'returns_401': metrics.status_code == 401,
            'response_time': metrics.response_time
        }
        
        return results

    async def simulate_user_journey(self, session: aiohttp.ClientSession, user_id: str) -> Dict:
        """Simulate a complete user journey"""
        self.logger.info(f"🎭 Starting user journey simulation for user {user_id}")
        
        # Create and authenticate user
        user_session = await self.create_test_user(session, user_id)
        if not user_session:
            return {'error': 'Failed to create user session'}
        
        journey_results = {}
        
        # Test AI operations
        journey_results['ai_operations'] = await self.test_ai_operations(session, user_session)
        await asyncio.sleep(0.5)  # Brief pause between operations
        
        # Test project operations
        journey_results['project_operations'] = await self.test_project_operations(session, user_session)
        await asyncio.sleep(0.5)
        
        # Test scene operations
        journey_results['scene_operations'] = await self.test_scene_operations(session, user_session)
        await asyncio.sleep(0.5)
        
        # Test analytics
        journey_results['analytics'] = await self.test_analytics_endpoints(session, user_session)
        await asyncio.sleep(0.5)
        
        # Test error handling
        journey_results['error_handling'] = await self.test_error_handling(session, user_session)
        
        # Calculate user session summary
        journey_results['session_summary'] = {
            'user_id': user_session.user_id,
            'email': user_session.email,
            'total_operations': user_session.total_operations,
            'successful_operations': user_session.successful_operations,
            'failed_operations': user_session.failed_operations,
            'success_rate': (user_session.successful_operations / user_session.total_operations * 100) if user_session.total_operations > 0 else 0,
            'projects_created': len(user_session.projects),
            'scenes_created': len(user_session.scenes)
        }
        
        self.logger.info(f"✅ User journey completed for {user_session.email}")
        return journey_results

    async def run_concurrent_users(self, num_users: int = 5) -> Dict:
        """Run multiple user simulations concurrently"""
        self.logger.info(f"🚀 Starting concurrent simulation with {num_users} users")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            # Test basic connectivity first
            if not await self.test_basic_health_check(session):
                return {'error': 'Basic connectivity test failed'}
            
            # Run concurrent user journeys
            tasks = []
            for i in range(num_users):
                user_id = f"sim_user_{i}_{uuid.uuid4().hex[:8]}"
                task = self.simulate_user_journey(session, user_id)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                'user_results': results,
                'total_users': num_users,
                'successful_users': len([r for r in results if isinstance(r, dict) and 'error' not in r])
            }

    def monitor_system_resources(self):
        """Monitor system resources during the test"""
        def collect_metrics():
            while True:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    system_metrics = TestMetrics(
                        endpoint='system_monitor',
                        method='MONITOR',
                        status_code=200,
                        response_time=0,
                        request_size=0,
                        response_size=0,
                        timestamp=datetime.now(),
                        additional_data={
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory.percent,
                            'memory_available': memory.available,
                            'memory_used': memory.used
                        }
                    )
                    
                    self.metrics.append(system_metrics)
                    
                except Exception as e:
                    self.logger.warning(f"System monitoring error: {e}")
                
                time.sleep(5)  # Collect every 5 seconds
        
        monitor_thread = Thread(target=collect_metrics, daemon=True)
        monitor_thread.start()

    def generate_comprehensive_report(self, results: Dict) -> Dict:
        """Generate comprehensive analysis report"""
        self.logger.info("📈 Generating comprehensive analysis report...")
        
        # Separate metrics by type
        api_metrics = [m for m in self.metrics if m.endpoint != 'system_monitor']
        system_metrics = [m for m in self.metrics if m.endpoint == 'system_monitor']
        
        # Performance analysis
        response_times = [m.response_time for m in api_metrics if m.response_time > 0]
        
        performance_analysis = {
            'total_requests': len(api_metrics),
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'median_response_time': statistics.median(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else 0,
            'p99_response_time': statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else 0
        }
        
        # Error analysis
        error_metrics = [m for m in api_metrics if m.status_code >= 400]
        status_codes = {}
        for metric in api_metrics:
            status_codes[metric.status_code] = status_codes.get(metric.status_code, 0) + 1
        
        error_analysis = {
            'total_errors': len(error_metrics),
            'error_rate': (len(error_metrics) / len(api_metrics) * 100) if api_metrics else 0,
            'status_code_distribution': status_codes,
            'common_errors': {}
        }
        
        # Group errors by message
        for metric in error_metrics:
            if metric.error_message:
                error_analysis['common_errors'][metric.error_message] = error_analysis['common_errors'].get(metric.error_message, 0) + 1
        
        # Endpoint analysis
        endpoint_stats = {}
        for metric in api_metrics:
            endpoint = metric.endpoint
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'count': 0,
                    'total_time': 0,
                    'errors': 0,
                    'avg_response_size': 0
                }
            
            endpoint_stats[endpoint]['count'] += 1
            endpoint_stats[endpoint]['total_time'] += metric.response_time
            if metric.status_code >= 400:
                endpoint_stats[endpoint]['errors'] += 1
            endpoint_stats[endpoint]['avg_response_size'] += metric.response_size
        
        # Calculate averages
        for endpoint, stats in endpoint_stats.items():
            stats['avg_response_time'] = stats['total_time'] / stats['count']
            stats['error_rate'] = (stats['errors'] / stats['count'] * 100)
            stats['avg_response_size'] = stats['avg_response_size'] / stats['count']
        
        # System resource analysis
        if system_metrics:
            cpu_values = [m.additional_data.get('cpu_percent', 0) for m in system_metrics if m.additional_data]
            memory_values = [m.additional_data.get('memory_percent', 0) for m in system_metrics if m.additional_data]
            
            resource_analysis = {
                'avg_cpu_usage': statistics.mean(cpu_values) if cpu_values else 0,
                'max_cpu_usage': max(cpu_values) if cpu_values else 0,
                'avg_memory_usage': statistics.mean(memory_values) if memory_values else 0,
                'max_memory_usage': max(memory_values) if memory_values else 0
            }
        else:
            resource_analysis = {'error': 'No system metrics collected'}
        
        # Generate recommendations
        recommendations = self.generate_recommendations(performance_analysis, error_analysis, endpoint_stats, resource_analysis)
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            'test_summary': {
                'duration_seconds': total_duration,
                'total_users_simulated': results.get('total_users', 0),
                'successful_users': results.get('successful_users', 0),
                'test_start_time': self.start_time.isoformat(),
                'test_end_time': datetime.now().isoformat()
            },
            'performance_analysis': performance_analysis,
            'error_analysis': error_analysis,
            'endpoint_analysis': endpoint_stats,
            'resource_analysis': resource_analysis,
            'recommendations': recommendations,
            'detailed_user_results': results.get('user_results', [])
        }
        
        return report

    def generate_recommendations(self, performance: Dict, errors: Dict, endpoints: Dict, resources: Dict) -> List[str]:
        """Generate actionable recommendations for backend optimization"""
        recommendations = []
        
        # Performance recommendations
        if performance['avg_response_time'] > 1.0:
            recommendations.append("⚠️ HIGH LATENCY: Average response time exceeds 1 second. Consider adding database indexing, implementing caching, or optimizing queries.")
        
        if performance['p95_response_time'] > 2.0:
            recommendations.append("⚠️ SLOW TAIL LATENCY: 95th percentile response time is high. This suggests some requests are significantly slower - investigate database queries and AI API calls.")
        
        # Error rate recommendations
        if errors['error_rate'] > 5:
            recommendations.append(f"❌ HIGH ERROR RATE: {errors['error_rate']:.1f}% error rate is concerning. Review error logs and implement better error handling.")
        
        # Endpoint-specific recommendations
        slow_endpoints = {k: v for k, v in endpoints.items() if v['avg_response_time'] > 2.0}
        if slow_endpoints:
            recommendations.append(f"🐌 SLOW ENDPOINTS: {list(slow_endpoints.keys())} are consistently slow. Consider optimizing these specific operations.")
        
        error_prone_endpoints = {k: v for k, v in endpoints.items() if v['error_rate'] > 10}
        if error_prone_endpoints:
            recommendations.append(f"💥 ERROR-PRONE ENDPOINTS: {list(error_prone_endpoints.keys())} have high error rates. Review input validation and error handling.")
        
        # AI operation recommendations
        ai_endpoints = {k: v for k, v in endpoints.items() if '/ai/' in k}
        if ai_endpoints:
            avg_ai_time = statistics.mean([v['avg_response_time'] for v in ai_endpoints.values()])
            if avg_ai_time > 5.0:
                recommendations.append("🤖 AI OPTIMIZATION: AI operations are slow. Consider implementing response streaming, caching common results, or using simulation mode for development.")
        
        # Database recommendations
        db_heavy_endpoints = ['/api/projects', '/api/scenes', '/api/analytics/dashboard']
        db_endpoints = {k: v for k, v in endpoints.items() if any(db_ep in k for db_ep in db_heavy_endpoints)}
        if db_endpoints:
            avg_db_time = statistics.mean([v['avg_response_time'] for v in db_endpoints.values()])
            if avg_db_time > 0.5:
                recommendations.append("🗄️ DATABASE OPTIMIZATION: Database operations are slow. Consider adding indexes, implementing connection pooling, or using database query optimization.")
        
        # Resource recommendations
        if resources.get('avg_cpu_usage', 0) > 80:
            recommendations.append("💾 HIGH CPU USAGE: CPU usage is high. Consider scaling horizontally or optimizing CPU-intensive operations.")
        
        if resources.get('avg_memory_usage', 0) > 85:
            recommendations.append("🧠 HIGH MEMORY USAGE: Memory usage is high. Check for memory leaks and consider implementing memory-efficient data structures.")
        
        # Security recommendations
        if any('401' in str(code) for code in errors.get('status_code_distribution', {})):
            recommendations.append("🔐 AUTHENTICATION ISSUES: Some requests are failing authentication. Review JWT token handling and session management.")
        
        # General recommendations
        recommendations.extend([
            "✅ IMPLEMENT CACHING: Add Redis caching for frequently accessed data (user profiles, project metadata).",
            "✅ ADD REQUEST LOGGING: Implement comprehensive request logging for better debugging and monitoring.",
            "✅ IMPLEMENT RATE LIMITING: Add rate limiting to prevent abuse and improve stability.",
            "✅ ADD HEALTH CHECKS: Implement detailed health checks for database, Redis, and AI services.",
            "✅ OPTIMIZE MIDDLEWARE: Review and optimize middleware stack for performance.",
            "✅ ADD MONITORING: Implement application performance monitoring (APM) for production insights."
        ])
        
        return recommendations

    async def run_comprehensive_test(self, num_users: int = 5, save_report: bool = True) -> Dict:
        """Run the complete comprehensive test"""
        self.logger.info("🎭 Starting ALVIN Frontend Simulation & Backend Stress Test")
        self.logger.info("=" * 80)
        
        # Start system monitoring
        self.monitor_system_resources()
        
        # Run the test
        results = await self.run_concurrent_users(num_users)
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report(results)
        
        # Save report if requested
        if save_report:
            report_filename = f"alvin_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"📄 Detailed report saved to: {report_filename}")
        
        # Print summary
        self.print_executive_summary(report)
        
        return report

    def print_executive_summary(self, report: Dict):
        """Print executive summary of the test results"""
        print("\n" + "=" * 80)
        print("📊 ALVIN BACKEND ANALYSIS - EXECUTIVE SUMMARY")
        print("=" * 80)
        
        summary = report['test_summary']
        performance = report['performance_analysis']
        errors = report['error_analysis']
        
        print(f"🕒 Test Duration: {summary['duration_seconds']:.1f} seconds")
        print(f"👥 Users Simulated: {summary['total_users_simulated']}")
        print(f"✅ Successful Users: {summary['successful_users']}")
        print(f"📡 Total API Requests: {performance['total_requests']}")
        print(f"⚡ Average Response Time: {performance['avg_response_time']:.3f}s")
        print(f"🚀 95th Percentile Response Time: {performance['p95_response_time']:.3f}s")
        print(f"❌ Error Rate: {errors['error_rate']:.1f}%")
        
        print(f"\n🎯 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'][:5], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n💡 Full analysis with {len(report['recommendations'])} recommendations available in JSON report")
        print("=" * 80)

def main():
    """Main function to run the comprehensive test"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ALVIN Frontend Simulation & Backend Analysis')
    parser.add_argument('--users', type=int, default=5, help='Number of concurrent users to simulate')
    parser.add_argument('--url', default='http://localhost:5000', help='Backend URL')
    parser.add_argument('--no-save', action='store_true', help='Do not save detailed report')
    
    args = parser.parse_args()
    
    simulator = FrontendSimulator(args.url)
    
    # Run the test
    try:
        report = asyncio.run(simulator.run_comprehensive_test(
            num_users=args.users,
            save_report=not args.no_save
        ))
        
        # Exit with appropriate code
        error_rate = report['error_analysis']['error_rate']
        exit_code = 0 if error_rate < 10 else 1  # Fail if error rate > 10%
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
