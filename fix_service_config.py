#!/usr/bin/env python3
"""
Fix the systemd service configuration issue
"""

import subprocess
import time

def fix_service_configuration():
    """Fix the service configuration that's causing SIGKILL issues"""
    print("🔧 Fixing service configuration (removing daemon conflict)...")
    
    # The issue: Type=exec with --daemon flag causes systemd confusion
    # Solution: Use Type=exec WITHOUT --daemon flag
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

# Use Type=exec WITHOUT --daemon flag (this was the issue!)
ExecStart=/var/www/news_summary/venv/bin/gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --timeout 30 --preload
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
MemoryMax=700M
MemoryHigh=600M

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # Stop the problematic service
        print("Stopping current service...")
        subprocess.run(['sudo', 'systemctl', 'stop', 'news-summary'], check=False)
        
        # Kill any remaining processes to clean slate
        subprocess.run(['sudo', 'pkill', '-f', 'gunicorn.*app.main'], check=False)
        time.sleep(3)
        
        # Write fixed service file
        with open('/tmp/news-summary-fixed.service', 'w') as f:
            f.write(service_content)
        
        subprocess.run(['sudo', 'cp', '/tmp/news-summary-fixed.service', 
                       '/etc/systemd/system/news-summary.service'], check=True)
        
        # Reset the failed state and restart counter
        subprocess.run(['sudo', 'systemctl', 'reset-failed', 'news-summary'], check=False)
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        
        print("✅ Service configuration fixed (removed daemon flag conflict)")
        return True
        
    except Exception as e:
        print(f"❌ Service fix failed: {e}")
        return False

def start_and_verify_service():
    """Start the service and verify it's working"""
    print("\n🚀 Starting fixed service...")
    
    try:
        # Start the service
        result = subprocess.run(['sudo', 'systemctl', 'start', 'news-summary'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to start service: {result.stderr}")
            return False
        
        # Wait for startup
        print("Waiting 10 seconds for startup...")
        time.sleep(10)
        
        # Check status
        status_result = subprocess.run(['sudo', 'systemctl', 'status', 'news-summary'], 
                                     capture_output=True, text=True)
        
        print("Service status:")
        print(status_result.stdout[:500])
        
        if 'active (running)' in status_result.stdout:
            print("✅ Service is running properly!")
            
            # Test health endpoint
            print("\nTesting health endpoint...")
            for attempt in range(3):
                try:
                    health_result = subprocess.run([
                        'curl', '-s', '--connect-timeout', '10', 
                        'http://127.0.0.1:8000/health'
                    ], capture_output=True, text=True, timeout=15)
                    
                    if health_result.returncode == 0 and health_result.stdout:
                        print(f"✅ Health endpoint working: {health_result.stdout}")
                        return True
                    else:
                        print(f"Attempt {attempt + 1}: Health endpoint not ready...")
                        time.sleep(3)
                        
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(3)
            
            print("⚠️ Service running but health endpoint not responding")
            return False
            
        else:
            print("❌ Service not running properly")
            return False
            
    except Exception as e:
        print(f"❌ Service verification failed: {e}")
        return False

def check_final_memory():
    """Check memory usage after fix"""
    print("\n📊 Checking memory usage...")
    
    try:
        # Overall memory
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print("System memory:")
        print(result.stdout)
        
        # Process memory
        ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        gunicorn_lines = [line for line in ps_result.stdout.split('\n') 
                         if 'gunicorn' in line and 'app.main:app' in line]
        
        if gunicorn_lines:
            print(f"\nFound {len(gunicorn_lines)} Gunicorn processes:")
            total_memory = 0
            for line in gunicorn_lines:
                parts = line.split()
                if len(parts) >= 6:
                    pid = parts[1]
                    mem_kb = int(parts[5])
                    mem_mb = mem_kb / 1024
                    total_memory += mem_mb
                    print(f"  PID {pid}: {mem_mb:.1f}MB")
            
            print(f"Total Gunicorn memory: {total_memory:.1f}MB")
        
    except Exception as e:
        print(f"Could not check memory: {e}")

def main():
    """Main fix function"""
    print("🔧 Service Configuration Fix")
    print("=" * 50)
    print("Issue: systemd Type=exec conflicts with Gunicorn --daemon flag")
    print("Fix: Remove --daemon flag, use proper Type=exec configuration")
    print()
    
    success = False
    
    # Fix the service configuration
    if fix_service_configuration():
        # Start and verify
        if start_and_verify_service():
            success = True
            
            # Check memory usage
            check_final_memory()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS! Service is now running properly!")
        print("\n🔗 Your application should now work:")
        print("   curl http://127.0.0.1:8000/health")
        print("   curl http://167.99.66.200/health")
        print("\n📊 Monitor with:")
        print("   sudo systemctl status news-summary")
        print("   sudo journalctl -u news-summary -f")
    else:
        print("❌ Fix incomplete. Check the errors above.")
        print("The service configuration has been updated, but may need manual intervention.")

if __name__ == "__main__":
    main() 