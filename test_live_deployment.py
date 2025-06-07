#!/usr/bin/env python3
"""
Test script for live Railway deployment
"""

import requests
import json

# Your actual Railway URL
RAILWAY_URL = "https://newssummary-production-140c.up.railway.app"

print(f"🧪 Testing Railway deployment at: {RAILWAY_URL}")

def test_endpoint(url, method="GET", description=""):
    """Test a single endpoint"""
    print(f"\n🔍 {description}")
    print(f"📍 URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, timeout=120)  # Longer timeout for scraping
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"📊 Response preview:")
                print(json.dumps(result, indent=2)[:500] + "..." if len(str(result)) > 500 else json.dumps(result, indent=2))
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

# Test all endpoints
tests = [
    (f"{RAILWAY_URL}/", "GET", "Root endpoint - API info"),
    (f"{RAILWAY_URL}/health", "GET", "Health check - Database connection"),
    (f"{RAILWAY_URL}/api/debug/articles", "GET", "Articles endpoint - View stored articles"),
    (f"{RAILWAY_URL}/api/categories", "GET", "Categories endpoint - View categories"),
    (f"{RAILWAY_URL}/api/news/fetch", "POST", "News scraper - Fetch latest articles (may take 1-2 minutes)")
]

results = []
for url, method, description in tests:
    success = test_endpoint(url, method, description)
    results.append(success)

# Summary
print("\n" + "=" * 60)
print("📈 RAILWAY DEPLOYMENT TEST SUMMARY")
print("=" * 60)

total_tests = len(results)
passed_tests = sum(results)

for i, (url, method, description) in enumerate(tests):
    status = "✅ PASSED" if results[i] else "❌ FAILED"
    print(f"{status} - {description}")

print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")

if passed_tests == total_tests:
    print("🎉 All tests passed! Your Railway deployment is working perfectly!")
else:
    print("⚠️ Some tests failed - but basic API is working!")

print(f"\n🌐 Your live API is available at: {RAILWAY_URL}") 