#!/usr/bin/env python3
"""
Quick manual test for Railway deployment
"""

import requests
import json

# Replace with your actual Railway URL
RAILWAY_URL = input("Enter your Railway URL (e.g., https://yourapp.up.railway.app): ").strip().rstrip('/')

print(f"\n🧪 Testing Railway deployment at: {RAILWAY_URL}")

# Test 1: Health Check
print("\n1️⃣ Testing Health Check...")
try:
    response = requests.get(f"{RAILWAY_URL}/health", timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Database Status: {data.get('database_status', 'Unknown')}")
        print(f"✅ Articles Count: {data.get('stats', {}).get('total_articles', 0)}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: View Articles
print("\n2️⃣ Testing Articles Endpoint...")
try:
    response = requests.get(f"{RAILWAY_URL}/api/debug/articles", timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Articles in database: {data.get('count', 0)}")
        if data.get('count', 0) > 0:
            print("📰 Sample articles:")
            for article in data.get('articles', [])[:3]:  # Show first 3
                print(f"  - {article.get('title', 'No title')[:50]}...")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Fetch News (this might take a while)
print("\n3️⃣ Testing News Scraper (this may take 1-2 minutes)...")
try:
    response = requests.post(f"{RAILWAY_URL}/api/news/fetch", timeout=120)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data.get('message', 'Success')}")
        print(f"📊 New articles: {data.get('new_articles', 0)}")
        print(f"📊 Duplicates skipped: {data.get('duplicates_skipped', 0)}")
        print(f"📊 Total processed: {data.get('total_processed', 0)}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎉 Testing complete!") 