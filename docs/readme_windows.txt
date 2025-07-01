# 🎭 ALVIN - Windows Setup Guide

Welcome to ALVIN! This guide will help you set up ALVIN on Windows. Choose the method that works best for you.

## 🚀 Quick Start Options

### Option 1: PowerShell Script (Recommended)
```powershell
# Open PowerShell as Administrator and run:
.\deploy.ps1 setup
.\deploy.ps1 dev
```

### Option 2: Batch File (Simple)
```cmd
# Open Command Prompt and run:
deploy.bat setup
deploy.bat dev
```

### Option 3: Python Script (Most Compatible)
```cmd
# Open Command Prompt and run:
python setup_windows.py
python setup_windows.py start-dev
```

### Option 4: Manual Docker Setup
```cmd
# If you prefer Docker commands directly:
docker-compose --profile development up -d
```

---

## 📋 Prerequisites

### Required:
- **Windows 10/11** (64-bit)
- **Docker Desktop** - [Download Here](https://docs.docker.com/desktop/install/windows-install/)

### Optional (for manual development):
- **Python 3.8+** - [Download Here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Here](https://nodejs.org/)

---

## 🔧 Step-by-Step Setup

### Step 1: Install Docker Desktop
1. Download and install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. Start Docker Desktop
3. Wait for Docker to be ready (green icon in system tray)

### Step 2: Get ALVIN
```cmd
git clone https://github.com/yourusername/alvin.git
cd alvin
```

### Step 3: Choose Your Setup Method

#### Method A: PowerShell (Recommended)
```powershell
# Allow execution of scripts (run PowerShell as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup
.\deploy.ps1 setup
.\deploy.ps1 dev
```

#### Method B: Simple Batch File
```cmd
deploy.bat setup
deploy.bat dev
```

#### Method C: Python Script
```cmd
python setup_windows.py
```

### Step 4: Configure Environment
1. The setup will create a `.env` file
2. Edit `.env` and add your API keys:
   ```env
   ANTHROPIC_API_KEY=your-api-key-here
   STRIPE_SECRET_KEY=sk_test_your-stripe-key
   ```
3. Save the file

### Step 5: Start ALVIN
The setup script will start ALVIN automatically, or you can start it manually:

```cmd
# Using PowerShell
.\deploy.ps1 dev

# Using Batch
deploy.bat dev

# Using Python
python setup_windows.py start-dev
```

---

## 🌐 Access ALVIN

Once started, open your web browser and go to:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

### Demo Account
- **Email**: demo@alvin.ai
- **Password**: demo123

---

## 🛠️ Common Commands

### PowerShell Commands
```powershell
.\deploy.ps1 setup      # Initial setup
.\deploy.ps1 dev        # Start development
.\deploy.ps1 stop       # Stop services
.\deploy.ps1 restart    # Restart services
.\deploy.ps1 status     # Check status
.\deploy.ps1 logs       # View logs
.\deploy.ps1 backup     # Create backup
```

### Batch Commands
```cmd
deploy.bat setup        # Initial setup
deploy.bat dev          # Start development
deploy.bat stop         # Stop services
deploy.bat restart      # Restart services
deploy.bat status       # Check status
deploy.bat logs         # View logs
```

### Python Commands
```cmd
python setup_windows.py            # Full setup
python setup_windows.py start-dev  # Start development
```

### Direct Docker Commands
```cmd
docker-compose --profile development up -d    # Start development
docker-compose down                           # Stop all services
docker-compose ps                             # Check status
docker-compose logs -f                        # View logs
```

---

## 🔍 Troubleshooting

### Docker Desktop Issues

**Problem**: "docker command not found"
```cmd
# Solution: Make sure Docker Desktop is installed and running
# Check if Docker is in your PATH by opening a new Command Prompt
docker --version
```

**Problem**: "Docker is not running"
```cmd
# Solution: Start Docker Desktop from the Start Menu
# Wait for the Docker whale icon to appear in system tray
```

### PowerShell Execution Policy

**Problem**: "Execution of scripts is disabled on this system"
```powershell
# Solution: Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use

**Problem**: "Port 5000 or 5173 is already in use"
```cmd
# Solution: Stop the conflicting service or change ports in docker-compose.yml
# To find what's using the port:
netstat -ano | findstr :5000
```

### Environment File Issues

**Problem**: "ANTHROPIC_API_KEY not found"
1. Make sure you have a `.env` file in the root directory
2. Open `.env` and verify your API key is correctly set:
   ```env
   ANTHROPIC_API_KEY=your-actual-api-key-here
   ```
3. No spaces around the `=` sign
4. Save the file and restart the services

### Database Connection Issues

**Problem**: "Database connection failed"
```cmd
# Solution: Reset the database
docker-compose down
docker volume rm alvin_postgres_data
.\deploy.ps1 dev
```

---

## 📁 Project Structure

```
ALVIN/
├── backend/           # Flask API backend
├── frontend/          # React frontend
├── docker-compose.yml # Docker services configuration
├── .env               # Environment variables (you create this)
├── .env.template      # Environment template
├── deploy.ps1         # PowerShell deployment script
├── deploy.bat         # Batch deployment script
├── setup_windows.py   # Python setup script
└