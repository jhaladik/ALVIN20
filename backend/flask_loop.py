# loop_diagnostic.py - IDENTIFY WHAT'S CAUSING THE RESTART LOOP
"""
Run this to identify what's causing your backend to restart continuously
"""

import os
import time
import psutil
from datetime import datetime

def diagnose_restart_loop():
    """Diagnose what's causing the backend restart loop"""
    
    print("🔍 BACKEND RESTART LOOP DIAGNOSTIC")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check 1: Look for running Flask processes
    print("1. 🔍 CHECKING RUNNING PROCESSES:")
    flask_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if 'python' in proc.info['name'].lower() and ('run.py' in cmdline or 'flask' in cmdline):
                flask_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if flask_processes:
        print(f"   ⚠️  Found {len(flask_processes)} Flask/Python processes:")
        for proc in flask_processes:
            print(f"      PID {proc['pid']}: {proc['cmdline'][:80]}...")
        print("   💡 Multiple processes might be conflicting")
    else:
        print("   ✅ No conflicting Flask processes found")
    
    print()
    
    # Check 2: Look for file watcher triggers
    print("2. 🔍 CHECKING POTENTIAL FILE TRIGGERS:")
    
    trigger_files = [
        '*.pyc', '__pycache__', '*.log', '.env', '*.db', 
        'instance/', 'migrations/', '.git/', 'node_modules/'
    ]
    
    found_triggers = []
    
    # Check recent files (modified in last 5 minutes)
    now = time.time()
    five_min_ago = now - 300
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and common noise
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for file in files:
            filepath = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(filepath)
                if mtime > five_min_ago:
                    found_triggers.append({
                        'file': filepath,
                        'modified': datetime.fromtimestamp(mtime).strftime('%H:%M:%S'),
                        'age_seconds': int(now - mtime)
                    })
            except OSError:
                pass
    
    if found_triggers:
        print(f"   ⚠️  Found {len(found_triggers)} recently modified files:")
        for trigger in sorted(found_triggers, key=lambda x: x['age_seconds'])[:10]:
            print(f"      {trigger['modified']} ({trigger['age_seconds']}s ago): {trigger['file']}")
        print("   💡 These files might be triggering auto-reload")
    else:
        print("   ✅ No recently modified files found")
    
    print()
    
    # Check 3: Environment variables
    print("3. 🔍 CHECKING ENVIRONMENT VARIABLES:")
    
    env_vars = [
        'FLASK_DEBUG', 'FLASK_ENV', 'PYTHONDONTWRITEBYTECODE',
        'WERKZEUG_RUN_MAIN', 'FLASK_RUN_RELOAD'
    ]
    
    problematic_env = []
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}={value}")
            if var == 'FLASK_DEBUG' and value.lower() in ['1', 'true']:
                problematic_env.append(f"{var}={value} (enables auto-reload)")
            elif var == 'FLASK_RUN_RELOAD' and value.lower() in ['1', 'true']:
                problematic_env.append(f"{var}={value} (enables auto-reload)")
        else:
            print(f"   {var}=<not set>")
    
    if problematic_env:
        print(f"   ⚠️  Problematic environment variables:")
        for env in problematic_env:
            print(f"      {env}")
    else:
        print("   ✅ Environment variables look good")
    
    print()
    
    # Check 4: Current working directory and permissions
    print("4. 🔍 CHECKING DIRECTORY STATUS:")
    
    cwd = os.getcwd()
    print(f"   Working directory: {cwd}")
    
    # Check if in a special directory that might cause issues
    special_dirs = ['.git', 'node_modules', '__pycache__']
    if any(special in cwd for special in special_dirs):
        print(f"   ⚠️  Running from potentially problematic directory")
    
    # Check write permissions
    try:
        test_file = '.temp_test_write'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"   ✅ Directory is writable")
    except Exception as e:
        print(f"   ⚠️  Directory write test failed: {e}")
    
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("-" * 30)
    
    if len(flask_processes) > 1:
        print("1. ⚠️  Kill extra Flask processes:")
        for proc in flask_processes[1:]:  # Keep first, kill others
            print(f"   kill {proc['pid']}")
    
    if found_triggers:
        print("2. 🧹 Clean triggering files:")
        print("   find . -name '*.pyc' -delete")
        print("   find . -name '__pycache__' -type d -exec rm -rf {} +")
        print("   rm -f *.log app.log")
    
    print("3. 🔧 Start with loop prevention:")
    print("   FLASK_DEBUG=0 python run.py")
    print("   # OR")
    print("   python simple_run.py  # (with fixed settings)")
    
    if problematic_env:
        print("4. 🌍 Fix environment variables:")
        print("   export FLASK_DEBUG=0")
        print("   export FLASK_ENV=production")
    
    print("\n5. 🎯 If still looping, create simple_run.py:")
    print("""   cat > simple_run.py << 'EOF'
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
EOF""")
    
    print("\n✅ Diagnostic complete!")

if __name__ == "__main__":
    try:
        diagnose_restart_loop()
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        print("💡 Quick fix: FLASK_DEBUG=0 python run.py")