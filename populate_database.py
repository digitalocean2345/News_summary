#!/usr/bin/env python3
"""
Direct database population script for the deployed app
This script connects directly to the database to add test data
"""

import os
import sys
from datetime import datetime, date

# Set environment to production to use the same database path as deployed app
os.environ["ENVIRONMENT"] = "production"

# Add app directory to path so we can import modules
sys.path.append("./app")

from database import SessionLocal, engine
from models.models import Base, News, Category, Comment

def create_test_data():
    """Create test data directly in the database"""
    
    print("🚀 Creating test data in production database...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Add test categories
        categories_data = [
            {"name": "Technology", "description": "Tech news and innovations"},
            {"name": "Business", "description": "Business and finance news"},
            {"name": "Environment", "description": "Environmental and climate news"},
            {"name": "Health", "description": "Health and medical news"}
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not category:
                category = Category(**cat_data)
                db.add(category)
                db.commit()
                db.refresh(category)
                print(f"✅ Created category: {category.name}")
            categories[cat_data["name"]] = category
        
        # Add test news articles
        today = date.today()
        test_articles = [
            {
                "title": "Tech Giants Report Strong Q4 Earnings",
                "full_content": "Technology giants reported strong earnings for Q4 2024, with cloud computing and AI investments paying off significantly. The sector showed resilience despite global economic uncertainties.",
                "source_url": "https://example.com/tech-earnings",
                "collection_date": today,
                "source_domain": "example.com",
                "content_language": "en",
                "is_content_scraped": True,
                "content_scraped_at": datetime.now()
            },
            {
                "title": "Global Climate Summit Reaches Historic Agreement",
                "full_content": "The global climate summit concluded with unprecedented agreement on carbon emission reduction targets. The historic deal includes commitments from major economies to achieve net-zero emissions by 2050.",
                "source_url": "https://example.com/climate-summit",
                "collection_date": today,
                "source_domain": "example.com",
                "content_language": "en",
                "is_content_scraped": True,
                "content_scraped_at": datetime.now()
            },
            {
                "title": "Revolutionary Medical Breakthrough in Cancer Treatment",
                "full_content": "Researchers have developed a new personalized cancer treatment approach that shows remarkable success rates in clinical trials. The therapy targets specific genetic markers in tumor cells.",
                "source_url": "https://example.com/cancer-breakthrough",
                "collection_date": today,
                "source_domain": "example.com",
                "content_language": "en",
                "is_content_scraped": True,
                "content_scraped_at": datetime.now()
            },
            {
                "title": "Asian Markets Rally on Economic Optimism",
                "full_content": "Asian stock markets experienced significant rallies as positive economic data and supportive policy measures boosted investor confidence across the region.",
                "source_url": "https://example.com/asia-markets",
                "collection_date": today,
                "source_domain": "example.com",
                "content_language": "en",
                "is_content_scraped": True,
                "content_scraped_at": datetime.now()
            },
            {
                "title": "Breakthrough in Renewable Energy Storage",
                "full_content": "Scientists have developed a new type of battery that can store renewable energy for extended periods with 95% efficiency, potentially solving one of the biggest challenges in clean energy adoption.",
                "source_url": "https://example.com/energy-storage",
                "collection_date": today,
                "source_domain": "example.com",
                "content_language": "en",
                "is_content_scraped": True,
                "content_scraped_at": datetime.now()
            }
        ]
        
        added_count = 0
        for article_data in test_articles:
            # Check if article already exists
            existing = db.query(News).filter(News.title == article_data["title"]).first()
            if not existing:
                article = News(**article_data)
                db.add(article)
                db.commit()
                db.refresh(article)
                print(f"✅ Added article: {article.title[:50]}...")
                added_count += 1
            else:
                print(f"⏭️  Skipped existing article: {existing.title[:50]}...")
        
        # Verify the data
        total_articles = db.query(News).count()
        total_categories = db.query(Category).count()
        
        print(f"\n🎉 Database population complete!")
        print(f"📊 Total categories: {total_categories}")
        print(f"📰 Total articles: {total_articles}")
        print(f"➕ Articles added this run: {added_count}")
        print(f"\n🌐 Your app should now show news at:")
        print(f"   https://prefab-rampart-462215-a9.uc.r.appspot.com/")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data() 