#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

def test_api_fixes():
    """Test the encoding and constraint fixes"""
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Testing fetch for date: {today}")
    
    try:
        response = requests.post(f'http://localhost:8000/api/news/fetch/{today}')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
        print("Make sure the server is running with: uvicorn app.main:app --reload")

def test_peoples_daily_scraper():
    """Test the People's Daily scraper directly"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.scrapers.peoples_daily_scraper import PeoplesDailyScraper
    
    print("\nTesting People's Daily scraper directly...")
    scraper = PeoplesDailyScraper()
    
    # Test a single page
    test_url = "http://fanfu.people.com.cn/"
    articles = scraper.scrape_page(test_url)
    
    print(f"Found {len(articles)} articles from {test_url}")
    if articles:
        sample = articles[0]
        print(f"Sample title: {sample['title']}")
        
        # Check for garbled characters
        if any(char in sample['title'] for char in ['绔', '棣', 'ㄥ', '介', '璺', '璁']):
            print("❌ ENCODING STILL BROKEN!")
        else:
            print("✅ ENCODING FIXED!")

if __name__ == "__main__":
    test_peoples_daily_scraper()
    print("\n" + "="*50)
    test_api_fixes() 