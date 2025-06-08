#!/usr/bin/env python3
"""
Emergency fix for 512MB droplet with severe memory constraints
This script adds swap space and uses minimal uvicorn instead of gunicorn
"""

import subprocess
import os
import time

def add_swap_space():
    """Add 1GB swap file to give more memory headroom"""
    print("🔧 Adding swap space for memory relief...")
    
    try:
        # Check if swap already exists
        result = subprocess.run(['swapon', '--show'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Swap space already exists:")
            print(result.stdout)
            return True
        
        print("Creating 1GB swap file...")
        
        # Create swap file (1GB)
        subprocess.run(['sudo', 'fallocate', '-l', '1G', '/swapfile'], check=True)
        print("✅ Swap file created")
        
        # Set correct permissions
        subprocess.run(['sudo', 'chmod', '600', '/swapfile'], check=True)
        print("✅ Swap file permissions set")
        
        # Make it a swap file
        subprocess.run(['sudo', 'mkswap', '/swapfile'], check=True)
        print("✅ Swap file formatted")
        
        # Enable swap
        subprocess.run(['sudo', 'swapon', '/swapfile'], check=True)
        print("✅ Swap enabled")
        
        # Make it permanent
        with open('/tmp/fstab_entry', 'w') as f:
            f.write('/swapfile none swap sw 0 0\n')
        
        subprocess.run(['sudo', 'sh', '-c', 'echo "/swapfile none swap sw 0 0" >> /etc/fstab'], check=True)
        print("✅ Swap made permanent")
        
        # Check swap status
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print("New memory status:")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Swap creation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_minimal_service():
    """Create a minimal systemd service using uvicorn directly"""
    print("\n🔧 Creating minimal uvicorn service...")
    
    service_content = """[Unit]
Description=News Summary FastAPI Application (Minimal)
After=network.target

[Service]
Type=simple
User=deployer
Group=deployer
WorkingDirectory=/var/www/news_summary
Environment=PATH=/var/www/news_summary/venv/bin
Environment=PYTHONPATH=/var/www/news_summary

# Use uvicorn directly instead of gunicorn for lower memory usage
ExecStart=/var/www/news_summary/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=10

# Memory limits for 512MB droplet
MemoryAccounting=yes
MemoryMax=300M
MemoryHigh=250M

# Lower process priority to prevent overwhelming system
Nice=10

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # Stop existing service
        subprocess.run(['sudo', 'systemctl', 'stop', 'news-summary'], check=False)
        
        # Write the minimal service file
        with open('/tmp/news-summary-minimal.service', 'w') as f:
            f.write(service_content)
        
        # Copy to systemd directory
        subprocess.run(['sudo', 'cp', '/tmp/news-summary-minimal.service', '/etc/systemd/system/news-summary.service'], check=True)
        
        # Reload systemd
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        
        print("✅ Minimal uvicorn service created")
        return True
        
    except Exception as e:
        print(f"❌ Service creation failed: {e}")
        return False

def test_app_directly():
    """Test if the app can run with uvicorn directly"""
    print("\n🔍 Testing app with uvicorn directly...")
    
    try:
        # Change to project directory
        os.chdir('/var/www/news_summary')
        
        # Test import first
        print("Testing app import...")
        result = subprocess.run([
            '/var/www/news_summary/venv/bin/python', 
            '-c', 
            'from app.main import app; print("✅ App imported successfully")'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Import failed: {result.stderr}")
            return False
        
        print("✅ App can be imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ App test failed: {e}")
        return False

def start_service_and_test():
    """Start the service and test it"""
    print("\n🚀 Starting minimal service...")
    
    try:
        # Start service
        subprocess.run(['sudo', 'systemctl', 'start', 'news-summary'], check=True)
        print("✅ Service started")
        
        # Wait for startup
        print("Waiting 10 seconds for startup...")
        time.sleep(10)
        
        # Check status
        result = subprocess.run(['sudo', 'systemctl', 'status', 'news-summary'], 
                              capture_output=True, text=True)
        
        if 'active (running)' in result.stdout:
            print("✅ Service is running")
            
            # Test endpoint
            print("Testing health endpoint...")
            time.sleep(5)
            
            try:
                test_result = subprocess.run(['curl', '-s', '--connect-timeout', '10', 'http://127.0.0.1:8000/health'], 
                                           capture_output=True, text=True, timeout=15)
                
                if test_result.returncode == 0 and test_result.stdout:
                    print("✅ Health endpoint working!")
                    print(f"Response: {test_result.stdout}")
                    return True
                else:
                    print("❌ Health endpoint not responding")
                    print(f"Error: {test_result.stderr}")
                    
            except Exception as e:
                print(f"❌ Endpoint test failed: {e}")
        else:
            print("❌ Service not running properly")
            print(result.stdout[:500])
        
        return False
        
    except Exception as e:
        print(f"❌ Service start failed: {e}")
        return False

def show_final_status():
    """Show final system status"""
    print("\n📊 Final System Status:")
    
    # Memory usage
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print("Memory usage:")
        print(result.stdout)
    except:
        pass
    
    # Service status
    try:
        result = subprocess.run(['sudo', 'systemctl', 'status', 'news-summary'], 
                              capture_output=True, text=True)
        print("Service status:")
        print(result.stdout[:300])
    except:
        pass
    
    # Process list
    try:
        result = subprocess.run(['ps', 'aux', '|', 'grep', 'uvicorn'], 
                              shell=True, capture_output=True, text=True)
        if result.stdout:
            print("Uvicorn processes:")
            print(result.stdout)
    except:
        pass

def main():
    """Main emergency fix function"""
    print("🚨 Emergency Fix for 512MB Droplet")
    print("=" * 60)
    print("This will:")
    print("1. Add 1GB swap space")
    print("2. Replace gunicorn with lighter uvicorn")
    print("3. Set strict memory limits")
    print("4. Test the application")
    print()
    
    success_steps = []
    
    # Step 1: Add swap space
    if add_swap_space():
        success_steps.append("Swap space added")
    
    # Step 2: Test app
    if test_app_directly():
        success_steps.append("App imports successfully")
    
    # Step 3: Create minimal service
    if create_minimal_service():
        success_steps.append("Minimal service created")
    
    # Step 4: Start and test
    if start_service_and_test():
        success_steps.append("Service running and responding")
    
    # Final status
    show_final_status()
    
    print("\n" + "=" * 60)
    print("🏁 Emergency Fix Summary:")
    for step in success_steps:
        print(f"✅ {step}")
    
    if len(success_steps) >= 3:
        print("\n🎉 SUCCESS! Your application should now be working.")
        print("Test with: curl http://127.0.0.1:8000/health")
    else:
        print("\n⚠️ Some steps failed. You may need to:")
        print("1. Upgrade to a larger droplet (1GB+ RAM)")
        print("2. Further optimize the application")
        print("3. Consider using a lightweight framework")

if __name__ == "__main__":
    main() 