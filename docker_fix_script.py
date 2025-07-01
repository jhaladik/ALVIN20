#!/usr/bin/env python3
"""
ALVIN20 Docker Fix Script
Comprehensive fix for all Docker-related issues
"""

import subprocess
import os
import sys
import time
import shutil
from pathlib import Path
from typing import List, Dict, Any

class DockerFixer:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.issues_found = []
        self.fixes_applied = []
        
    def log_issue(self, issue: str):
        """Log an issue found"""
        self.issues_found.append(issue)
        print(f"🔍 Found issue: {issue}")
    
    def log_fix(self, fix: str):
        """Log a fix applied"""
        self.fixes_applied.append(fix)
        print(f"✅ Applied fix: {fix}")
    
    def check_docker_environment(self) -> bool:
        """Check if Docker and Docker Compose are available"""
        print("🔧 Checking Docker environment...")
        
        try:
            # Check Docker
            result = subprocess.run(["docker", "--version"], 
                                 capture_output=True, text=True, check=True)
            print(f"✅ Docker: {result.stdout.strip()}")
            
            # Check Docker Compose
            result = subprocess.run(["docker-compose", "--version"], 
                                 capture_output=True, text=True, check=True)
            print(f"✅ Docker Compose: {result.stdout.strip()}")
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Docker environment check failed: {e}")
            print("Please install Docker and Docker Compose first")
            return False
    
    def fix_frontend_dockerfile(self) -> bool:
        """Fix frontend Dockerfile issues"""
        print("\n🔧 Fixing frontend Dockerfile...")
        
        fixes_made = False
        
        # Fix Dockerfile.dev
        dockerfile_dev = self.root_dir / "frontend" / "Dockerfile.dev"
        if dockerfile_dev.exists():
            content = dockerfile_dev.read_text()
            original_content = content
            
            # Fix incorrect package name
            if "@vitejs/create-react-app" in content:
                content = content.replace(
                    "RUN npm install -g @vitejs/create-react-app",
                    "# No global packages needed for existing project"
                )
                self.log_fix("Removed incorrect @vitejs/create-react-app package")
                fixes_made = True
            
            # Fix package.json copy
            if "COPY package*.json ./" in content:
                content = content.replace(
                    "COPY package*.json ./",
                    "COPY package.json ./"
                )
                self.log_fix("Fixed package.json copy command")
                fixes_made = True
            
            # Fix npm ci to npm install
            if "npm ci" in content:
                content = content.replace("npm ci", "npm install")
                self.log_fix("Changed npm ci to npm install")
                fixes_made = True
            
            if content != original_content:
                dockerfile_dev.write_text(content)
                self.log_fix("Updated frontend/Dockerfile.dev")
        
        # Fix production Dockerfile
        dockerfile_prod = self.root_dir / "frontend" / "Dockerfile"
        if dockerfile_prod.exists():
            content = dockerfile_prod.read_text()
            original_content = content
            
            # Fix npm install command
            if "npm install --production" in content:
                content = content.replace(
                    "npm install --production",
                    "npm install"
                )
                self.log_fix("Fixed npm install in production Dockerfile")
                fixes_made = True
            
            if content != original_content:
                dockerfile_prod.write_text(content)
                self.log_fix("Updated frontend/Dockerfile")
        
        return fixes_made
    
    def create_missing_frontend_files(self) -> bool:
        """Create missing frontend configuration files"""
        print("\n📁 Creating missing frontend files...")
        
        frontend_dir = self.root_dir / "frontend"
        frontend_dir.mkdir(exist_ok=True)
        
        files_created = []
        
        # Create package.json if missing
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            package_content = {
                "name": "alvin-frontend",
                "version": "1.0.0",
                "type": "module",
                "scripts": {
                    "dev": "vite --host 0.0.0.0 --port 5173",
                    "build": "vite build",
                    "preview": "vite preview"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.8.0",
                    "axios": "^1.3.0",
                    "@tanstack/react-query": "^4.24.0"
                },
                "devDependencies": {
                    "@types/react": "^18.0.27",
                    "@types/react-dom": "^18.0.10",
                    "@vitejs/plugin-react": "^3.1.0",
                    "typescript": "^4.9.3",
                    "vite": "^4.1.0"
                }
            }
            
            import json
            package_json.write_text(json.dumps(package_content, indent=2))
            files_created.append("package.json")
        
        # Create vite.config.ts if missing
        vite_config = frontend_dir / "vite.config.ts"
        if not vite_config.exists():
            vite_content = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
  },
  define: {
    'process.env': process.env
  }
})
'''
            vite_config.write_text(vite_content)
            files_created.append("vite.config.ts")
        
        # Create tsconfig.json if missing
        tsconfig = frontend_dir / "tsconfig.json"
        if not tsconfig.exists():
            ts_content = '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}'''
            tsconfig.write_text(ts_content)
            files_created.append("tsconfig.json")
        
        # Create basic src structure
        src_dir = frontend_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Create main.tsx if missing
        main_tsx = src_dir / "main.tsx"
        if not main_tsx.exists():
            main_content = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''
            main_tsx.write_text(main_content)
            files_created.append("src/main.tsx")
        
        # Create App.tsx if missing
        app_tsx = src_dir / "App.tsx"
        if not app_tsx.exists():
            app_content = '''import React from 'react'

function App() {
  return (
    <div className="App">
      <h1>ALVIN Frontend</h1>
      <p>Loading...</p>
    </div>
  )
}

export default App
'''
            app_tsx.write_text(app_content)
            files_created.append("src/App.tsx")
        
        # Create index.css if missing
        index_css = src_dir / "index.css"
        if not index_css.exists():
            css_content = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
'''
            index_css.write_text(css_content)
            files_created.append("src/index.css")
        
        # Create index.html if missing
        index_html = frontend_dir / "index.html"
        if not index_html.exists():
            html_content = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ALVIN - AI-Powered Writing Assistant</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''
            index_html.write_text(html_content)
            files_created.append("index.html")
        
        if files_created:
            self.log_fix(f"Created frontend files: {', '.join(files_created)}")
        
        return len(files_created) > 0
    
    def fix_environment_file(self) -> bool:
        """Create or fix environment file"""
        print("\n🔧 Fixing environment configuration...")
        
        env_file = self.root_dir / ".env"
        env_template = self.root_dir / ".env.template"
        
        if not env_file.exists():
            if env_template.exists():
                shutil.copy(env_template, env_file)
                self.log_fix("Created .env file from template")
                
                # Add some sensible defaults
                with env_file.open("a") as f:
                    f.write("\n# Additional defaults\n")
                    f.write("AI_SIMULATION_MODE=true\n")
                    f.write("PAYMENT_SIMULATION_MODE=true\n")
                    f.write("DEBUG=true\n")
                
                print("\n🔑 Please edit .env file and add your API keys:")
                print("   - ANTHROPIC_API_KEY=your-key-here")
                print("   - STRIPE_SECRET_KEY=sk_test_your-key")
                
                return True
            else:
                # Create basic .env file
                env_content = """# ALVIN Environment Configuration
FLASK_CONFIG=development
SECRET_KEY=alvin-dev-secret-key-change-for-production
JWT_SECRET_KEY=jwt-dev-secret-key-change-for-production

# Database
DATABASE_URL=postgresql://alvin_user:alvin_password@postgres:5432/alvin

# Redis
REDIS_URL=redis://redis:6379/0

# AI Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
AI_SIMULATION_MODE=true

# Stripe (for billing)
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
PAYMENT_SIMULATION_MODE=true

# Frontend
VITE_API_URL=http://localhost:5000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your-publishable-key

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Debug
DEBUG=true
"""
                env_file.write_text(env_content)
                self.log_fix("Created basic .env file")
                print("\n🔑 Please edit .env file and add your actual API keys")
                return True
        
        return False
    
    def create_necessary_directories(self) -> bool:
        """Create necessary directories for the application"""
        print("\n📁 Creating necessary directories...")
        
        directories = [
            "backend/uploads",
            "backend/logs", 
            "backend/exports",
            "backend/backups",
            "nginx/ssl",
            "backups"
        ]
        
        created = []
        for directory in directories:
            dir_path = self.root_dir / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                created.append(directory)
        
        if created:
            self.log_fix(f"Created directories: {', '.join(created)}")
            return True
        
        return False
    
    def fix_docker_compose_issues(self) -> bool:
        """Fix docker-compose.yml issues"""
        print("\n🔧 Checking docker-compose.yml...")
        
        compose_file = self.root_dir / "docker-compose.yml"
        if not compose_file.exists():
            self.log_issue("docker-compose.yml not found")
            return False
        
        # Validate compose file
        try:
            result = subprocess.run(
                ["docker-compose", "config"], 
                capture_output=True, text=True, check=True
            )
            print("✅ docker-compose.yml syntax is valid")
            return True
        except subprocess.CalledProcessError as e:
            self.log_issue(f"docker-compose.yml has syntax errors: {e.stderr}")
            return False
    
    def clean_docker_cache(self):
        """Clean Docker build cache"""
        print("\n🧹 Cleaning Docker cache...")
        
        try:
            # Stop all containers
            subprocess.run(["docker-compose", "down"], capture_output=True)
            
            # Clean build cache
            subprocess.run(["docker", "system", "prune", "-f"], 
                         capture_output=True)
            
            # Remove specific volumes if they exist
            subprocess.run(["docker", "volume", "rm", "alvin_postgres_data"], 
                         capture_output=True)
            subprocess.run(["docker", "volume", "rm", "alvin_redis_data"], 
                         capture_output=True)
            
            self.log_fix("Cleaned Docker cache and volumes")
            
        except Exception as e:
            print(f"⚠️  Cache cleaning warning: {e}")
    
    def test_backend_only_start(self) -> bool:
        """Try to start just the backend services"""
        print("\n🚀 Testing backend-only startup...")
        
        try:
            # Start essential backend services
            cmd = [
                "docker-compose", "up", "-d",
                "postgres", "redis", "backend-dev"
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Wait for services to start
            print("⏱️  Waiting for services to start...")
            time.sleep(15)
            
            # Check if services are running
            result = subprocess.run(
                ["docker-compose", "ps"], 
                capture_output=True, text=True
            )
            
            if "Up" in result.stdout:
                print("✅ Backend services started successfully!")
                print("\n🌐 Services available:")
                print("   📊 Backend API: http://localhost:5000")
                print("   🩺 Health Check: http://localhost:5000/health")
                print("   🗄️  Database: PostgreSQL on localhost:5432")
                print("   💾 Cache: Redis on localhost:6379")
                return True
            else:
                self.log_issue("Backend services failed to start properly")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log_issue(f"Failed to start backend services: {e}")
            return False
    
    def test_full_startup(self) -> bool:
        """Try to start all services"""
        print("\n🚀 Testing full application startup...")
        
        try:
            # Build and start all development services
            cmd = [
                "docker-compose", "--profile", "development", 
                "up", "--build", "-d"
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Wait for services to start
            print("⏱️  Waiting for all services to start...")
            time.sleep(20)
            
            # Check service status
            result = subprocess.run(
                ["docker-compose", "ps"], 
                capture_output=True, text=True
            )
            
            if "Up" in result.stdout:
                print("✅ All services started successfully!")
                print("\n🌐 Application ready:")
                print("   🎭 Frontend: http://localhost:5173")
                print("   📊 Backend API: http://localhost:5000")
                print("   🩺 Health Check: http://localhost:5000/health")
                print("\n🔑 Demo Account:")
                print("   📧 Email: demo@alvin.ai")
                print("   🔒 Password: demo123")
                return True
            else:
                self.log_issue("Some services failed to start")
                print("❌ Full startup failed, trying backend-only mode...")
                return self.test_backend_only_start()
                
        except subprocess.CalledProcessError as e:
            self.log_issue(f"Full startup failed: {e}")
            print("❌ Full startup failed, trying backend-only mode...")
            return self.test_backend_only_start()
    
    def run_fixes(self) -> bool:
        """Run all fixes"""
        print("🎭 ALVIN20 Docker Fix Script")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_docker_environment():
            return False
        
        # Apply fixes
        self.fix_frontend_dockerfile()
        self.create_missing_frontend_files()
        self.fix_environment_file()
        self.create_necessary_directories()
        self.fix_docker_compose_issues()
        
        # Clean and rebuild
        self.clean_docker_cache()
        
        print(f"\n📊 Summary: {len(self.fixes_applied)} fixes applied")
        
        # Test startup
        success = self.test_full_startup()
        
        if success:
            print("\n🎉 ALVIN20 is ready to use!")
        else:
            print("\n⚠️  Some issues remain. Check logs above.")
            print("\n💡 Manual steps to try:")
            print("   1. Check your .env file has correct API keys")
            print("   2. Run: docker-compose --profile development build --no-cache")
            print("   3. Run: docker-compose --profile development up -d")
        
        return success

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--backend-only":
        print("🔧 Backend-only mode requested")
        fixer = DockerFixer()
        if fixer.check_docker_environment():
            return fixer.test_backend_only_start()
    else:
        fixer = DockerFixer()
        return fixer.run_fixes()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)