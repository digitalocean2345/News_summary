#!/usr/bin/env python3
"""
Test script for Railway deployment endpoints
"""

import requests
import json
import time
from datetime import datetime

# Replace this with your actual Railway app URL
RAILWAY_URL = "https://YOUR_APP_NAME.up.railway.app"

def test_endpoint(url, method="GET", data=None, description=""):
    """Test a single endpoint"""
    print(f"\n🧪 Testing: {description}")
    print(f"📍 URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"📊 Response preview: {json.dumps(result, indent=2)[:300]}...")
                return True
            except:
                print(f"📊 Response: {response.text[:200]}...")
                return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return False

def main():
    """Run all endpoint tests"""
    print("🚀 Testing Railway Deployment Endpoints")
    print("=" * 50)
    
    # Ask user for their Railway URL
    global RAILWAY_URL
    user_url = input(f"\n📝 Enter your Railway app URL (or press Enter to use default): ").strip()
    if user_url:
        RAILWAY_URL = user_url.rstrip('/')
    
    print(f"\n🎯 Testing endpoints at: {RAILWAY_URL}")
    
    tests = [
        {
            "url": f"{RAILWAY_URL}/",
            "method": "GET",
            "description": "Root endpoint - API info"
        },
        {
            "url": f"{RAILWAY_URL}/health",
            "method": "GET", 
            "description": "Health check - Database connection"
        },
        {
            "url": f"{RAILWAY_URL}/api/debug/articles",
            "method": "GET",
            "description": "Articles endpoint - View stored articles"
        },
        {
            "url": f"{RAILWAY_URL}/api/categories",
            "method": "GET",
            "description": "Categories endpoint - View categories"
        },
        {
            "url": f"{RAILWAY_URL}/api/news/fetch",
            "method": "POST",
            "description": "News scraper - Fetch latest articles (This may take 1-2 minutes)"
        }
    ]
    
    results = []
    
    for test in tests:
        success = test_endpoint(
            test["url"], 
            test["method"], 
            test.get("data"),
            test["description"]
        )
        results.append(success)
        
        # Wait a bit between requests
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 50)
    print("📈 Test Results Summary:")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    for i, test in enumerate(tests):
        status = "✅ PASSED" if results[i] else "❌ FAILED"
        print(f"{status} - {test['description']}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your Railway deployment is working perfectly!")
        print("\n📝 Next steps:")
        print("1. Copy your Railway URL for GitHub Actions setup")
        print("2. Set up GitHub repository secrets")
        print("3. Test GitHub Actions automation")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 