#!/usr/bin/env python3
"""
Transfer local database to DigitalOcean server
"""

import os
import subprocess
import sys

def transfer_database():
    """Transfer local database to server"""
    print("🚀 Transferring Database to DigitalOcean Server")
    print("=" * 50)
    
    # Check if local database exists
    local_db = "news.db"
    if not os.path.exists(local_db):
        print(f"❌ Local database '{local_db}' not found")
        return False
    
    # Get database size
    size_mb = os.path.getsize(local_db) / (1024 * 1024)
    print(f"📊 Local database size: {size_mb:.2f} MB")
    
    # Server connection details
    server_ip = input("Enter your DigitalOcean server IP: ").strip()
    if not server_ip:
        print("❌ Server IP required")
        return False
    
    server_user = "deployer"
    server_path = "/var/www/news_summary/"
    
    print(f"\n🔄 Transferring to {server_user}@{server_ip}:{server_path}")
    
    try:
        # Use SCP to transfer the database
        scp_command = [
            "scp",
            "-o", "StrictHostKeyChecking=no",
            local_db,
            f"{server_user}@{server_ip}:{server_path}"
        ]
        
        print(f"🚀 Running: {' '.join(scp_command)}")
        result = subprocess.run(scp_command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database transferred successfully!")
            
            # Verify transfer
            print("\n🔍 Verifying transfer...")
            ssh_command = [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                f"{server_user}@{server_ip}",
                f"cd {server_path} && ls -la news.db && echo 'File size:' && du -h news.db"
            ]
            
            verify_result = subprocess.run(ssh_command, capture_output=True, text=True)
            if verify_result.returncode == 0:
                print("✅ Transfer verified!")
                print(verify_result.stdout)
                
                # Test database content on server
                print("\n🧪 Testing database content on server...")
                test_command = [
                    "ssh",
                    "-o", "StrictHostKeyChecking=no", 
                    f"{server_user}@{server_ip}",
                    f"cd {server_path} && python check_database.py"
                ]
                
                test_result = subprocess.run(test_command, capture_output=True, text=True)
                if test_result.returncode == 0:
                    print("✅ Database test successful!")
                    print(test_result.stdout)
                else:
                    print("⚠️  Database test had issues:")
                    print(test_result.stderr)
                    
            else:
                print("⚠️  Could not verify transfer:")
                print(verify_result.stderr)
                
        else:
            print("❌ Transfer failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Transfer error: {e}")
        return False
    
    return True

def main():
    print("This script will transfer your local database (3,333 articles) to your DigitalOcean server.")
    print("Make sure you have SSH access to your server.\n")
    
    confirm = input("Continue with transfer? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Transfer cancelled.")
        return
    
    success = transfer_database()
    
    if success:
        print("\n🎉 Database transfer completed!")
        print("\nNext steps:")
        print("1. Your server now has 3,333 articles")
        print("2. Test your FastAPI health endpoint")
        print("3. Start your news-summary service")
        print("4. Access your application at http://your-server-ip:8000")
    else:
        print("\n❌ Transfer failed. Check the errors above.")

if __name__ == "__main__":
    main() 