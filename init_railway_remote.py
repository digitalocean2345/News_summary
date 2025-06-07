#!/usr/bin/env python3
"""
Initialize Railway database remotely via API
"""

import requests
import json
import time

RAILWAY_URL = "https://newssummary-production-140c.up.railway.app"

def check_health():
    """Check API health"""
    print("🔍 Checking API health...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data.get('status', 'unknown')}")
            print(f"📊 Database: {data.get('database', 'unknown')}")
            return data.get('database') != 'disconnected'
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def initialize_database():
    """Initialize database by fetching news (which creates tables)"""
    print("\n🚀 Initializing database by fetching news...")
    try:
        response = requests.post(f"{RAILWAY_URL}/api/news/fetch", timeout=180)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data.get('message', 'Success')}")
            print(f"📊 New articles: {data.get('new_articles', 0)}")
            print(f"📊 Total processed: {data.get('total_processed', 0)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def verify_database():
    """Verify database has data"""
    print("\n🔍 Verifying database...")
    try:
        response = requests.get(f"{RAILWAY_URL}/api/debug/articles", timeout=30)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"✅ Articles in database: {count}")
            return count > 0
        else:
            print(f"❌ Verification failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    print("🎯 Railway Database Remote Initialization")
    print("=" * 50)
    
    # Step 1: Check current health
    if not check_health():
        print("⚠️ API not responding properly")
        return
    
    # Step 2: Initialize database
    if initialize_database():
        print("✅ Database initialization successful!")
        
        # Step 3: Verify
        time.sleep(5)  # Wait a moment
        if verify_database():
            print("🎉 Database fully initialized and verified!")
        else:
            print("⚠️ Database initialized but verification failed")
    else:
        print("❌ Database initialization failed")

if __name__ == "__main__":
    main() 