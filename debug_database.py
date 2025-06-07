#!/usr/bin/env python3
"""
Debug database connection for Railway
"""

import requests
import json

RAILWAY_URL = "https://newssummary-production-140c.up.railway.app"

def debug_database():
    """Get detailed database debug info"""
    print("🔍 Debugging database connection...")
    
    try:
        # Create a simple debug endpoint call
        response = requests.get(f"{RAILWAY_URL}/", timeout=30)
        print(f"API Status: {response.status_code}")
        
        # Check health endpoint for detailed error
        health_response = requests.get(f"{RAILWAY_URL}/health", timeout=30)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"\n📊 Health Check Details:")
            print(json.dumps(health_data, indent=2))
            
            # Look for specific error messages
            if 'error' in health_data:
                error_msg = health_data['error']
                if 'sqlite3' in error_msg:
                    print(f"\n❌ ISSUE FOUND: App is using SQLite instead of PostgreSQL!")
                    print(f"This means DATABASE_URL environment variable is not set on Railway.")
                    print(f"\n🔧 SOLUTION:")
                    print(f"1. Go to your Railway dashboard")
                    print(f"2. Click on your project")
                    print(f"3. Go to Variables tab")
                    print(f"4. Check if DATABASE_URL exists")
                    print(f"5. If missing, reconnect your PostgreSQL database")
                    
        else:
            print(f"Health check failed: {health_response.status_code}")
            
    except Exception as e:
        print(f"❌ Debug error: {e}")

if __name__ == "__main__":
    debug_database() 