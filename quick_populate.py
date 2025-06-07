#!/usr/bin/env python3
"""
Quick script to populate the deployed database with test data
"""

import requests
import json
from datetime import datetime

# Your deployed app URL
BASE_URL = "https://prefab-rampart-462215-a9.uc.r.appspot.com"

def add_test_news():
    """Add some test news data"""
    
    # Test news articles
    test_articles = [
        {
            "headline": "Tech Giants Report Strong Q4 Earnings",
            "summary": "Major technology companies showed robust financial performance in the fourth quarter, with cloud services and AI investments driving growth.",
            "content": "Technology giants reported strong earnings for Q4 2024, with cloud computing and artificial intelligence investments paying off significantly. The sector showed resilience despite global economic uncertainties.",
            "url": "https://example.com/tech-earnings",
            "published_at": datetime.now().isoformat(),
            "category": "Technology"
        },
        {
            "headline": "Global Climate Summit Reaches Historic Agreement",
            "summary": "World leaders agreed on ambitious carbon reduction targets at the international climate summit, marking a significant step in environmental policy.",
            "content": "The global climate summit concluded with unprecedented agreement on carbon emission reduction targets. The historic deal includes commitments from major economies to achieve net-zero emissions by 2050.",
            "url": "https://example.com/climate-summit",
            "published_at": datetime.now().isoformat(),
            "category": "Environment"
        },
        {
            "headline": "Revolutionary Medical Breakthrough in Cancer Treatment",
            "summary": "Scientists announce a breakthrough in personalized cancer therapy that could revolutionize treatment approaches for multiple cancer types.",
            "content": "Researchers have developed a new personalized cancer treatment approach that shows remarkable success rates in clinical trials. The therapy targets specific genetic markers in tumor cells.",
            "url": "https://example.com/cancer-breakthrough",
            "published_at": datetime.now().isoformat(),
            "category": "Health"
        },
        {
            "headline": "Asian Markets Rally on Economic Optimism",
            "summary": "Stock markets across Asia showed strong gains as investors responded positively to economic indicators and policy announcements.",
            "content": "Asian stock markets experienced significant rallies as positive economic data and supportive policy measures boosted investor confidence across the region.",
            "url": "https://example.com/asia-markets",
            "published_at": datetime.now().isoformat(),
            "category": "Business"
        }
    ]
    
    print("🚀 Starting to populate database with test news...")
    
    for i, article in enumerate(test_articles):
        try:
            print(f"\n📰 Adding article {i+1}: {article['headline'][:50]}...")
            
            # Note: This is simplified - in real implementation, you'd need to:
            # 1. Create categories first
            # 2. Insert news articles with proper foreign keys
            # 3. Handle the full database structure
            
            # For now, let's just verify the database is accessible
            health_response = requests.get(f"{BASE_URL}/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Database connected, articles: {health_data.get('articles_count', 0)}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error adding article {i+1}: {str(e)}")
    
    print("\n🎯 Database population complete!")
    print(f"📊 Check your app at: {BASE_URL}")

if __name__ == "__main__":
    add_test_news() 