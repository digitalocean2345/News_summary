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
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM news")
            count = result.scalar()
            print(f"✅ Database connection verified - {count} articles found")
        
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
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
    time.sleep(3)  # Wait for service to start
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get('http://127.0.0.1:8000/health', timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            
    except ImportError:
        print("⚠️ Requests library not available, using curl instead")
        try:
            result = subprocess.run(['curl', '-s', 'http://127.0.0.1:8000/health'], 
                                  capture_output=True, text=True, timeout=10)
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
    print("🛠️  News Summary Deployment Fix Script")
    print("=" * 50)
    
    # Change to the correct directory
    if os.path.exists('/var/www/news_summary'):
        os.chdir('/var/www/news_summary')
        print("✅ Changed to /var/www/news_summary")
    
    # Step 1: Stop existing processes
    kill_gunicorn_processes()
    
    # Step 2: Check database
    db_path = check_database_file()
    
    # Step 3: Initialize database if found
    if db_path:
        initialize_database()
    
    # Step 4: Restart service
    restart_service()
    
    # Step 5: Test endpoints
    test_endpoints()
    
    # Step 6: Show logs
    check_logs()
    
    print("\n" + "=" * 50)
    print("🏁 Fix script completed!")
    print("\n💡 Manual checks you can do:")
    print("1. curl http://127.0.0.1:8000/health")
    print("2. sudo systemctl status news-summary")
    print("3. sudo journalctl -u news-summary -f")
    print("4. lsof -i :8000")

if __name__ == "__main__":
    main() 