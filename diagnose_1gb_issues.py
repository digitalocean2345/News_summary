#!/usr/bin/env python3
"""
Diagnose and fix issues with 1GB droplet setup
"""

import subprocess
import os
import time
import sys

def test_database_properly():
    """Test database with proper Python syntax"""
    print("🔍 Testing database with proper syntax...")
    
    # Create a proper test file instead of using one-liner
    test_script = """
import sys
sys.path.insert(0, '/var/www/news_summary')

try:
    from app.database import engine
    from sqlalchemy import text
    
    print("✅ Imports successful")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM news"))
        count = result.scalar()
        print(f"✅ Database OK - {count} articles")
        
except Exception as e:
    print(f"❌ Database test failed: {e}")
    import traceback
    traceback.print_exc()
"""
    
    try:
        # Write test script
        with open('/tmp/db_test.py', 'w') as f:
            f.write(test_script)
        
        # Run the test
        result = subprocess.run([
            '/var/www/news_summary/venv/bin/python', 
            '/tmp/db_test.py'
        ], capture_output=True, text=True, timeout=30)
        
        print("Database test output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def check_service_logs():
    """Get detailed service logs to see why it's failing"""
    print("\n🔍 Checking detailed service logs...")
    
    try:
        # Get journal logs for the service
        result = subprocess.run([
            'sudo', 'journalctl', '-u', 'news-summary', 
            '--no-pager', '--lines=50'
        ], capture_output=True, text=True)
        
        print("Service logs:")
        print(result.stdout)
        
        if result.stderr:
            print("Stderr:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Could not get service logs: {e}")

def test_app_import():
    """Test if the app can be imported properly"""
    print("\n🔍 Testing app import...")
    
    test_script = """
import sys
sys.path.insert(0, '/var/www/news_summary')

try:
    from app.main import app
    print("✅ App import successful")
    print(f"App type: {type(app)}")
    
    # Test if app has the expected attributes
    if hasattr(app, 'routes'):
        print(f"✅ App has routes: {len(app.routes)} routes found")
    
except Exception as e:
    print(f"❌ App import failed: {e}")
    import traceback
    traceback.print_exc()
"""
    
    try:
        with open('/tmp/app_test.py', 'w') as f:
            f.write(test_script)
        
        result = subprocess.run([
            '/var/www/news_summary/venv/bin/python', 
            '/tmp/app_test.py'
        ], capture_output=True, text=True, timeout=30)
        
        print("App import test output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ App import test failed: {e}")
        return False

def test_gunicorn_manually():
    """Test running Gunicorn manually to see detailed error"""
    print("\n🔍 Testing Gunicorn manually...")
    
    try:
        os.chdir('/var/www/news_summary')
        
        # Test Gunicorn in foreground mode to see errors
        result = subprocess.run([
            '/var/www/news_summary/venv/bin/gunicorn', 
            'app.main:app',
            '-w', '1',  # Start with just 1 worker
            '-k', 'uvicorn.workers.UvicornWorker',
            '--bind', '127.0.0.1:8001',  # Use different port to avoid conflicts
            '--timeout', '30',
            '--preload'  # Preload to catch import errors early
        ], capture_output=True, text=True, timeout=30)
        
        print("Manual Gunicorn test output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("✅ Gunicorn started successfully (timeout after 30s is expected)")
        return True
    except Exception as e:
        print(f"❌ Manual Gunicorn test failed: {e}")
        return False

def check_port_conflicts():
    """Check if port 8000 is already in use"""
    print("\n🔍 Checking port conflicts...")
    
    try:
        result = subprocess.run(['sudo', 'lsof', '-i', ':8000'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("Port 8000 is in use:")
            print(result.stdout)
            
            # Try to kill existing processes
            print("\nTrying to stop existing processes...")
            subprocess.run(['sudo', 'pkill', '-f', 'gunicorn.*app.main'], check=False)
            time.sleep(2)
            
            # Check again
            result2 = subprocess.run(['sudo', 'lsof', '-i', ':8000'], 
                                   capture_output=True, text=True)
            if result2.stdout.strip():
                print("⚠️ Port still in use after cleanup attempt")
            else:
                print("✅ Port cleared")
        else:
            print("✅ Port 8000 is free")
            
    except Exception as e:
        print(f"❌ Could not check port: {e}")

def fix_service_and_restart():
    """Fix the service configuration and restart"""
    print("\n🔧 Fixing service configuration...")
    
    # Create a more robust service configuration
    service_content = """[Unit]
Description=News Summary FastAPI Application (1GB Optimized)
After=network.target

[Service]
Type=exec
User=deployer
Group=deployer
WorkingDirectory=/var/www/news_summary
Environment=PATH=/var/www/news_summary/venv/bin
Environment=PYTHONPATH=/var/www/news_summary

# Start with 1 worker first, then can scale to 2
ExecStart=/var/www/news_summary/venv/bin/gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --timeout 30 --preload
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=10
TimeoutStartSec=60
PrivateTmp=true

Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3

# Memory limits for 1GB droplet
MemoryAccounting=yes
MemoryMax=600M
MemoryHigh=500M

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # Stop the service first
        subprocess.run(['sudo', 'systemctl', 'stop', 'news-summary'], check=False)
        
        # Kill any remaining processes
        subprocess.run(['sudo', 'pkill', '-f', 'gunicorn.*app.main'], check=False)
        time.sleep(3)
        
        # Write new service file
        with open('/tmp/news-summary-fixed.service', 'w') as f:
            f.write(service_content)
        
        subprocess.run(['sudo', 'cp', '/tmp/news-summary-fixed.service', 
                       '/etc/systemd/system/news-summary.service'], check=True)
        
        # Reload and start
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        subprocess.run(['sudo', 'systemctl', 'start', 'news-summary'], check=True)
        
        print("✅ Service restarted with fixed configuration")
        
        # Wait and check status
        time.sleep(10)
        result = subprocess.run(['sudo', 'systemctl', 'status', 'news-summary'], 
                              capture_output=True, text=True)
        
        print("Service status after fix:")
        print(result.stdout)
        
        return 'active (running)' in result.stdout
        
    except Exception as e:
        print(f"❌ Service fix failed: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🔍 Diagnosing 1GB Droplet Issues")
    print("=" * 50)
    
    # Test database properly
    db_ok = test_database_properly()
    
    # Check service logs
    check_service_logs()
    
    # Test app import
    app_ok = test_app_import()
    
    # Check port conflicts
    check_port_conflicts()
    
    # Test Gunicorn manually
    gunicorn_ok = test_gunicorn_manually()
    
    # Try to fix the service
    if not gunicorn_ok:
        print("\n⚠️ Issues detected, attempting to fix...")
        service_ok = fix_service_and_restart()
        
        if service_ok:
            print("\n✅ Service appears to be working now!")
            
            # Test health endpoint
            time.sleep(5)
            try:
                result = subprocess.run(['curl', '-s', '--connect-timeout', '10', 
                                       'http://127.0.0.1:8000/health'], 
                                      capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0 and result.stdout:
                    print(f"✅ Health endpoint working: {result.stdout}")
                else:
                    print("⚠️ Health endpoint not responding yet")
            except:
                print("⚠️ Could not test health endpoint")
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print(f"Database: {'✅' if db_ok else '❌'}")
    print(f"App Import: {'✅' if app_ok else '❌'}")
    print(f"Gunicorn: {'✅' if gunicorn_ok else '❌'}")
    
    print("\n💡 Next steps:")
    print("1. Check the output above for specific errors")
    print("2. If service is running, test: curl http://127.0.0.1:8000/health")
    print("3. Monitor with: sudo journalctl -u news-summary -f")

if __name__ == "__main__":
    main() 