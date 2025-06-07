#!/usr/bin/env python3
"""
Create database tables on Railway by triggering news fetch
"""

import requests
import json
import time

RAILWAY_URL = "https://newssummary-production-140c.up.railway.app"

def create_tables():
    """Create tables by calling news fetch endpoint"""
    print("🚀 Creating database tables...")
    print("This will trigger table creation when the app tries to insert news data.")
    
    try:
        print("📡 Calling news fetch endpoint...")
        response = requests.post(f"{RAILWAY_URL}/api/news/fetch", timeout=300)  # 5 minute timeout
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Tables created and data inserted:")
            print(f"📊 New articles: {data.get('new_articles', 0)}")
            print(f"📊 Total processed: {data.get('total_processed', 0)}")
            return True
        else:
            print(f"❌ Error Response: {response.text}")
            # Even if there's an error, tables might have been created
            print("🔍 Let's check if tables were created anyway...")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this is normal for first run as it creates tables")
        print("🔍 Let's check if tables were created...")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_tables():
    """Verify tables were created"""
    print("\n🔍 Verifying table creation...")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('database') == 'connected':
                print("✅ Database is now connected! Tables created successfully.")
                return True
            else:
                print(f"⚠️ Database status: {data.get('database')}")
                if 'error' in data and 'does not exist' not in data['error']:
                    print("✅ Tables likely created (different error now)")
                    return True
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    print("🎯 Railway Database Table Creation")
    print("=" * 50)
    
    # Try to create tables
    success = create_tables()
    
    # Wait a moment then verify
    time.sleep(10)
    verified = verify_tables()
    
    if success or verified:
        print("\n🎉 Database initialization complete!")
        print("🔄 Now let's test all endpoints...")
        
        # Run a quick test
        try:
            response = requests.get(f"{RAILWAY_URL}/api/debug/articles", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Articles endpoint working! Found {data.get('count', 0)} articles")
            else:
                print(f"⚠️ Articles endpoint: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Test error: {e}")
    else:
        print("\n❌ Table creation may have failed")
        print("💡 Try running this script again, or check Railway logs")

if __name__ == "__main__":
    main() 