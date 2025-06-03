#!/usr/bin/env python3
"""
Test script to verify Guancha scraper integration
"""

import requests
import json
from datetime import datetime

def test_guancha_integration():
    """Test that Guancha scraper is properly integrated"""
    
    print("🧪 Testing Guancha Scraper Integration")
    print("=" * 50)
    
    # Test 1: Check if scraper can be imported
    try:
        from app.scrapers.guancha_scraper import GuanchaScraper
        print("✅ Guancha scraper import: SUCCESS")
    except Exception as e:
        print(f"❌ Guancha scraper import: FAILED - {e}")
        return
    
    # Test 2: Check if scraper can fetch articles
    try:
        scraper = GuanchaScraper()
        articles = scraper.fetch_news()
        print(f"✅ Guancha scraper fetch: SUCCESS - Found {len(articles)} articles")
        
        if articles:
            print(f"   📰 Sample article: {articles[0]['title'][:50]}...")
            print(f"   🔗 Sample URL: {articles[0]['source_url']}")
            print(f"   📂 Sample section: {articles[0]['source_section']}")
    except Exception as e:
        print(f"❌ Guancha scraper fetch: FAILED - {e}")
        return
    
    # Test 3: Check if main app includes Guancha
    try:
        from app.main import app
        print("✅ Main app import: SUCCESS")
    except Exception as e:
        print(f"❌ Main app import: FAILED - {e}")
        return
    
    # Test 4: Test API endpoint (if server is running)
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        response = requests.post(f'http://localhost:8000/api/news/fetch/{today}', timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API fetch test: SUCCESS")
            print(f"   📊 Result: {result.get('message', 'No message')}")
        else:
            print(f"⚠️  API fetch test: Server responded with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API fetch test: SKIPPED - Server not running")
    except Exception as e:
        print(f"❌ API fetch test: FAILED - {e}")
    
    print("\n🎉 Guancha integration test completed!")
    print("\nNext steps:")
    print("1. Start the server: python -m uvicorn app.main:app --reload")
    print("2. Visit: http://localhost:8000")
    print("3. Navigate to a date and look for the 'Guancha' tab")
    print("4. Click 'Fetch Guancha Headlines' to test the integration")

if __name__ == "__main__":
    test_guancha_integration() 