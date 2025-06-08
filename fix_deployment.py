#!/usr/bin/env python3
"""
Quick fix script for deployment issues
Run this script on the server to fix common problems
"""

import os
import subprocess
import sys
from pathlib import Path

def kill_gunicorn_processes():
    """Kill existing Gunicorn processes"""
    print("🔧 Stopping existing Gunicorn processes...")
    try:
        result = subprocess.run(['pkill', '-f', 'gunicorn'], capture_output=True, text=True)
        print("✅ Gunicorn processes stopped")
    except Exception as e:
        print(f"⚠️ Could not stop Gunicorn processes: {e}")

def check_database_file():
    """Check if database file exists and has proper permissions"""
    print("\n🔍 Checking database file...")
    
    db_paths = [
        './news.db',
        './news_aggregator.db',
        '/var/www/news_summary/news.db',
        '/var/www/news_summary/news_aggregator.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"✅ Found database: {db_path}")
            
            # Check permissions
            stat = os.stat(db_path)
            print(f"   Size: {stat.st_size} bytes")
            print(f"   Permissions: {oct(stat.st_mode)[-3:]}")
            
            # Try to make it writable
            try:
                os.chmod(db_path, 0o664)
                print("✅ Set database permissions to 664")
            except Exception as e:
                print(f"⚠️ Could not set permissions: {e}")
            
            return db_path
    
    print("❌ No database file found")
    return None

def initialize_database():
    """Initialize database tables"""
    print("\n🔧 Initializing database...")
    try:
        from app.database import engine
        from app.models.models import Base
        from sqlalchemy import text
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM news"))
            count = result.scalar()
            print(f"✅ Database connection verified - {count} articles found")
        
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def optimize_for_small_droplet():
    """Optimize systemd service for 512MB droplet"""
    print("\n🔧 Optimizing service for small droplet...")
    
    service_content = """[Unit]
Description=News Summary FastAPI Application
After=network.target

[Service]
Type=forking
User=deployer
Group=deployer
WorkingDirectory=/var/www/news_summary
Environment=PATH=/var/www/news_summary/venv/bin
# Reduced to 1 worker to prevent OOM on 512MB droplet
ExecStart=/var/www/news_summary/venv/bin/gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --daemon
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

# Memory limits for 512MB droplet
MemoryAccounting=yes
MemoryMax=400M
MemoryHigh=350M

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # Write the optimized service file
        with open('/tmp/news-summary.service', 'w') as f:
            f.write(service_content)
        
        # Copy to systemd directory
        subprocess.run(['sudo', 'cp', '/tmp/news-summary.service', '/etc/systemd/system/'], check=True)
        
        # Reload systemd
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        
        print("✅ Service optimized for 512MB droplet (1 worker instead of 4)")
        return True
    except Exception as e:
        print(f"❌ Service optimization failed: {e}")
        return False

def restart_service():
    """Restart the news-summary service"""
    print("\n🔧 Restarting news-summary service...")
    try:
        # Stop the service
        subprocess.run(['sudo', 'systemctl', 'stop', 'news-summary'], check=True)
        print("✅ Service stopped")
        
        # Start the service
        subprocess.run(['sudo', 'systemctl', 'start', 'news-summary'], check=True)
        print("✅ Service started")
        
        # Check status
        result = subprocess.run(['sudo', 'systemctl', 'status', 'news-summary'], 
                              capture_output=True, text=True)
        if 'active (running)' in result.stdout:
            print("✅ Service is running")
        else:
            print("⚠️ Service may not be running properly")
            print(result.stdout[:500])
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Service restart failed: {e}")
        return False

def test_endpoints():
    """Test the application endpoints"""
    print("\n🔍 Testing endpoints...")
    
    import time
    time.sleep(5)  # Wait longer for service to start with 1 worker
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get('http://127.0.0.1:8000/health', timeout=15)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            
    except ImportError:
        print("⚠️ Requests library not available, using curl instead")
        try:
            result = subprocess.run(['curl', '-s', 'http://127.0.0.1:8000/health'], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0 and result.stdout:
                print("✅ Health endpoint working")
                print(f"   Response: {result.stdout}")
            else:
                print("❌ Health endpoint not responding")
                print(f"   Error: {result.stderr}")
        except Exception as e:
            print(f"❌ Could not test endpoint: {e}")
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")

def check_memory_usage():
    """Check current memory usage"""
    print("\n📊 Checking memory usage...")
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Memory usage:")
            print(result.stdout)
        
        # Check if any processes were killed
        result = subprocess.run(['dmesg', '|', 'grep', '-i', 'killed'], 
                              shell=True, capture_output=True, text=True)
        if result.stdout:
            print("\n⚠️ Recent OOM kills:")
            print(result.stdout[-500:])  # Last 500 chars
            
    except Exception as e:
        print(f"❌ Could not check memory: {e}")

def check_logs():
    """Check recent service logs"""
    print("\n📋 Checking recent logs...")
    try:
        result = subprocess.run(['sudo', 'journalctl', '-u', 'news-summary', '--no-pager', '-n', '20'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Recent logs:")
            print(result.stdout)
        else:
            print("Could not retrieve logs")
    except Exception as e:
        print(f"❌ Could not check logs: {e}")

def main():
    """Main fix function"""
    print("🛠️  News Summary Deployment Fix Script (512MB Droplet Optimized)")
    print("=" * 70)
    
    # Change to the correct directory
    if os.path.exists('/var/www/news_summary'):
        os.chdir('/var/www/news_summary')
        print("✅ Changed to /var/www/news_summary")
    
    # Step 1: Check memory usage first
    check_memory_usage()
    
    # Step 2: Stop existing processes
    kill_gunicorn_processes()
    
    # Step 3: Check database
    db_path = check_database_file()
    
    # Step 4: Initialize database if found
    if db_path:
        initialize_database()
    
    # Step 5: Optimize service for small droplet
    optimize_for_small_droplet()
    
    # Step 6: Restart service
    restart_service()
    
    # Step 7: Test endpoints
    test_endpoints()
    
    # Step 8: Show logs
    check_logs()
    
    print("\n" + "=" * 70)
    print("🏁 Fix script completed!")
    print("\n💡 Manual checks you can do:")
    print("1. curl http://127.0.0.1:8000/health")
    print("2. sudo systemctl status news-summary")
    print("3. sudo journalctl -u news-summary -f")
    print("4. lsof -i :8000")
    print("5. free -h  # Check memory usage")

if __name__ == "__main__":
    main() 