#!/usr/bin/env python3
"""
Check server database content and structure
"""

import os
import sys
sys.path.insert(0, '/var/www/news_summary')

from app.database import engine
from sqlalchemy import text

def check_database():
    """Check database file, structure, and content"""
    print("🔍 Checking server database...")
    
    # Check database file
    db_path = 'news.db'
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ Database file exists: {size} bytes")
    else:
        print("❌ Database file missing")
        return
    
    try:
        with engine.connect() as conn:
            # Check news table
            result = conn.execute(text("SELECT COUNT(*) FROM news"))
            count = result.scalar()
            print(f"📊 News articles: {count}")
            
            # Check table structure
            result = conn.execute(text("PRAGMA table_info(news)"))
            columns = result.fetchall()
            print(f"📋 Table columns ({len(columns)}):")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # If there are articles, show a sample
            if count > 0:
                result = conn.execute(text("SELECT title, collection_date, source_domain FROM news LIMIT 3"))
                articles = result.fetchall()
                print(f"\n📰 Sample articles:")
                for i, article in enumerate(articles, 1):
                    print(f"  {i}. {article[0][:50]}... ({article[1]}) - {article[2]}")
            
            # Check date range
            if count > 0:
                result = conn.execute(text("SELECT MIN(collection_date), MAX(collection_date) FROM news"))
                date_range = result.fetchone()
                print(f"📅 Date range: {date_range[0]} to {date_range[1]}")
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def check_recent_dates():
    """Check what dates have articles"""
    print("\n🔍 Checking available dates...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT collection_date, COUNT(*) as article_count 
                FROM news 
                GROUP BY collection_date 
                ORDER BY collection_date DESC 
                LIMIT 10
            """))
            dates = result.fetchall()
            
            if dates:
                print("📅 Recent dates with articles:")
                for date, count in dates:
                    print(f"  - {date}: {count} articles")
            else:
                print("❌ No dates found with articles")
                
    except Exception as e:
        print(f"❌ Date check failed: {e}")

if __name__ == "__main__":
    print("🔍 Server Database Analysis")
    print("=" * 40)
    check_database()
    check_recent_dates()
    
    print("\n💡 If database is empty, you need to:")
    print("1. Transfer your local database to server, OR")
    print("2. Run the news scraping/population scripts on server") 