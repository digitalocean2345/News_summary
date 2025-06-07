#!/usr/bin/env python3
"""
Initialize database tables via API endpoint
"""

import requests
import json

RAILWAY_URL = "https://newssummary-production-140c.up.railway.app"

def initialize_tables():
    """Call the database initialization endpoint"""
    print("🚀 Initializing database tables via API...")
    
    try:
        response = requests.post(f"{RAILWAY_URL}/api/admin/init-database", timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Database initialized:")
            print(f"📊 Message: {data.get('message')}")
            print(f"📋 Tables created: {', '.join(data.get('tables_created', []))}")
            return True
        else:
            print(f"❌ Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_health():
    """Check if database is now healthy"""
    print("\n🔍 Verifying database health...")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Status: {data.get('status')}")
            print(f"📊 Database: {data.get('database')}")
            print(f"📊 Articles: {data.get('articles_count', 0)}")
            
            if data.get('database') == 'connected':
                print("✅ Database is now healthy!")
                return True
            else:
                print("⚠️ Database still has issues")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    print("🎯 Railway Database Table Initialization")
    print("=" * 50)
    
    # Initialize tables
    success = initialize_tables()
    
    if success:
        # Verify health
        verify_health()
        print("\n🎉 Database initialization complete!")
        print("✅ You can now test your endpoints!")
    else:
        print("\n❌ Database initialization failed")

if __name__ == "__main__":
    main() 