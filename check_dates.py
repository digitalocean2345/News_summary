#!/usr/bin/env python3
"""
Check available dates in the database
"""
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.models import News
from sqlalchemy import func
from collections import defaultdict

def check_dates():
    """Check available dates in the database"""
    print("📅 Checking available dates in database...")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Get all distinct dates with counts
        date_counts = db.query(
            News.collection_date, 
            func.count(News.id)
        ).group_by(News.collection_date).order_by(News.collection_date.desc()).all()
        
        print(f"📊 Total unique dates: {len(date_counts)}")
        print("\n📋 Available dates and article counts:")
        
        for date, count in date_counts[:15]:  # Show last 15 dates
            print(f"  {date}: {count} articles")
        
        if len(date_counts) > 15:
            print(f"\n... and {len(date_counts) - 15} more dates")
        
        # Check specifically for June 6th and 7th, 2025
        print("\n🔍 Checking for June 6th and 7th, 2025:")
        
        for target_date in ['2025-06-06', '2025-06-07']:
            count = db.query(News).filter(News.collection_date == target_date).count()
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {target_date}: {count} articles")
            
            if count > 0:
                # Show sample titles for that date
                sample_articles = db.query(News).filter(News.collection_date == target_date).limit(3).all()
                for article in sample_articles:
                    title_preview = article.title[:50] + "..." if len(article.title) > 50 else article.title
                    print(f"    📰 {title_preview}")
        
        # Check for recent dates around June 6-7
        print("\n📅 Recent dates around June 6-7:")
        recent_dates = ['2025-06-05', '2025-06-06', '2025-06-07', '2025-06-08', '2025-06-09']
        
        for target_date in recent_dates:
            count = db.query(News).filter(News.collection_date == target_date).count()
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {target_date}: {count} articles")
        
        # Show what dates are actually available (latest 10)
        print("\n📅 Most recent dates with articles:")
        for date, count in date_counts[:10]:
            print(f"  ✅ {date}: {count} articles")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_dates() 