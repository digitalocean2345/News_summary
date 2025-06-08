#!/usr/bin/env python3
"""
Setup script for 1GB droplet - much more breathing room!
This script configures the optimal setup for your upgraded droplet
"""

import subprocess
import os
import time

def check_memory():
    """Check current memory status"""
    print("🔍 Checking current memory status...")
    
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print("Current memory:")
        print(result.stdout)
        
        # Parse memory info
        lines = result.stdout.strip().split('\n')
        mem_line = lines[1].split()
        total_mb = int(mem_line[1].replace('Mi', ''))
        
        if total_mb >= 900:  # Account for OS overhead
            print("✅ Sufficient memory detected!")
            return True
        else:
            print(f"⚠️ Only {total_mb}MB detected. Make sure droplet upgrade completed.")
            return False
            
    except Exception as e:
        print(f"❌ Could not check memory: {e}")
        return False

def create_optimized_service():
    """Create optimized systemd service for 1GB droplet"""
    print("\n🔧 Creating optimized service for 1GB droplet...")
    
    service_content = """[Unit]
Description=News Summary FastAPI Application (1GB Optimized)
After=network.target

[Service]
Type=forking
User=deployer
Group=deployer
WorkingDirectory=/var/www/news_summary
Environment=PATH=/var/www/news_summary/venv/bin
Environment=PYTHONPATH=/var/www/news_summary

# Optimal configuration for 1GB droplet: 2 workers
ExecStart=/var/www/news_summary/venv/bin/gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --daemon
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=10
PrivateTmp=true

Restart=always
RestartSec=10

# Memory limits for 1GB droplet (generous but safe)
MemoryAccounting=yes
MemoryMax=800M
MemoryHigh=700M

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # Stop existing service
        subprocess.run(['sudo', 'systemctl', 'stop', 'news-summary'], check=False)
        
        # Write the optimized service file
        with open('/tmp/news-summary-1gb.service', 'w') as f:
            f.write(service_content)
        
        # Copy to systemd directory
        subprocess.run(['sudo', 'cp', '/tmp/news-summary-1gb.service', '/etc/systemd/system/news-summary.service'], check=True)
        
        # Reload systemd
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        
        print("✅ Optimized service created (2 Gunicorn workers)")
        return True
        
    except Exception as e:
        print(f"❌ Service creation failed: {e}")
        return False

def test_database():
    """Test database connectivity"""
    print("\n🔍 Testing database...")
    
    try:
        os.chdir('/var/www/news_summary')
        
        # Test database
        result = subprocess.run([
            '/var/www/news_summary/venv/bin/python', 
            '-c', 
            'from app.database import engine; from sqlalchemy import text; '
            'with engine.connect() as conn: '
            'result = conn.execute(text("SELECT COUNT(*) FROM news")); '
            'print(f"Database OK - {result.scalar()} articles")'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Database test passed")
            print(result.stdout.strip())
            return True
        else:
            print(f"❌ Database test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def start_and_test_service():
    """Start the service and test it thoroughly"""
    print("\n🚀 Starting optimized service...")
    
    try:
        # Start service
        subprocess.run(['sudo', 'systemctl', 'start', 'news-summary'], check=True)
        print("✅ Service started")
        
        # Wait for startup
        print("Waiting 15 seconds for startup...")
        time.sleep(15)
        
        # Check status
        result = subprocess.run(['sudo', 'systemctl', 'status', 'news-summary'], 
                              capture_output=True, text=True)
        
        if 'active (running)' in result.stdout:
            print("✅ Service is running")
            
            # Test health endpoint
            print("Testing health endpoint...")
            for attempt in range(3):
                try:
                    test_result = subprocess.run(['curl', '-s', '--connect-timeout', '10', 'http://127.0.0.1:8000/health'], 
                                               capture_output=True, text=True, timeout=15)
                    
                    if test_result.returncode == 0 and test_result.stdout:
                        print("✅ Health endpoint working!")
                        print(f"Response: {test_result.stdout}")
                        
                        # Test a few more endpoints
                        print("\nTesting additional endpoints...")
                        
                        # Test root endpoint
                        root_result = subprocess.run(['curl', '-s', '--connect-timeout', '5', 'http://127.0.0.1:8000/'], 
                                                   capture_output=True, text=True, timeout=10)
                        if root_result.returncode == 0:
                            print("✅ Root endpoint responding")
                        
                        return True
                    else:
                        print(f"Attempt {attempt + 1}: Endpoint not ready yet...")
                        time.sleep(5)
                        
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(5)
            
            print("❌ Health endpoint not responding after 3 attempts")
        else:
            print("❌ Service not running properly")
            print(result.stdout[:500])
        
        return False
        
    except Exception as e:
        print(f"❌ Service start failed: {e}")
        return False

def check_process_memory():
    """Check memory usage of running processes"""
    print("\n📊 Checking process memory usage...")
    
    try:
        # Check Gunicorn processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        gunicorn_lines = [line for line in result.stdout.split('\n') if 'gunicorn' in line and 'app.main:app' in line]
        
        if gunicorn_lines:
            print(f"Found {len(gunicorn_lines)} Gunicorn processes:")
            total_memory = 0
            for line in gunicorn_lines:
                parts = line.split()
                if len(parts) >= 6:
                    pid = parts[1]
                    mem_percent = parts[3]
                    mem_kb = int(parts[5])
                    mem_mb = mem_kb / 1024
                    total_memory += mem_mb
                    print(f"  PID {pid}: {mem_mb:.1f}MB ({mem_percent}%)")
            
            print(f"Total Gunicorn memory: {total_memory:.1f}MB")
            
            if total_memory < 400:  # Should be well under 400MB with 2 workers
                print("✅ Memory usage looks good for 1GB droplet")
            else:
                print("⚠️ Higher than expected memory usage")
        else:
            print("❌ No Gunicorn processes found")
            
    except Exception as e:
        print(f"❌ Could not check process memory: {e}")

def enable_service():
    """Enable service to start on boot"""
    print("\n🔧 Enabling service for auto-start...")
    
    try:
        subprocess.run(['sudo', 'systemctl', 'enable', 'news-summary'], check=True)
        print("✅ Service enabled for auto-start on boot")
        return True
    except Exception as e:
        print(f"❌ Could not enable service: {e}")
        return False

def show_final_status():
    """Show comprehensive final status"""
    print("\n📊 Final Status Report:")
    print("=" * 50)
    
    # Memory usage
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print("💾 Memory usage:")
        print(result.stdout)
    except:
        pass
    
    # Service status
    try:
        result = subprocess.run(['sudo', 'systemctl', 'status', 'news-summary'], 
                              capture_output=True, text=True)
        print("🔧 Service status:")
        print(result.stdout[:400])
    except:
        pass
    
    # Port check
    try:
        result = subprocess.run(['sudo', 'lsof', '-i', ':8000'], 
                              capture_output=True, text=True)
        if result.stdout:
            print("🌐 Port 8000 usage:")
            print(result.stdout)
    except:
        pass

def main():
    """Main setup function for 1GB droplet"""
    print("🚀 1GB Droplet Optimization Setup")
    print("=" * 60)
    print("This script will configure your FastAPI app optimally for 1GB RAM")
    print()
    
    success_steps = []
    
    # Step 1: Check memory
    if check_memory():
        success_steps.append("Memory upgrade confirmed")
    
    # Step 2: Test database
    if test_database():
        success_steps.append("Database connectivity verified")
    
    # Step 3: Create optimized service
    if create_optimized_service():
        success_steps.append("Optimized service created")
    
    # Step 4: Start and test
    if start_and_test_service():
        success_steps.append("Service running and responding")
        
        # Step 5: Check memory usage
        check_process_memory()
        
        # Step 6: Enable auto-start
        if enable_service():
            success_steps.append("Auto-start enabled")
    
    # Final status
    show_final_status()
    
    print("\n" + "=" * 60)
    print("🏁 Setup Summary:")
    for step in success_steps:
        print(f"✅ {step}")
    
    if len(success_steps) >= 4:
        print("\n🎉 SUCCESS! Your 1GB droplet is optimally configured!")
        print("\n🔗 Test your application:")
        print("   curl http://127.0.0.1:8000/health")
        print("   curl http://167.99.66.200/health")
        print("\n📊 Monitor with:")
        print("   python memory_monitor.py")
        print("   sudo systemctl status news-summary")
    else:
        print(f"\n⚠️ Some steps failed. Please check the errors above.")
        print("You may need to run individual commands manually.")

if __name__ == "__main__":
    main() 