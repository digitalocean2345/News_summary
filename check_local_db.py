#!/usr/bin/env python3
"""
Quick check of local database content
"""
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.models import News

def check_local_database():
    db = SessionLocal()
    try:
        # Get total count
        total_count = db.query(News).count()
        print(f"📊 Total articles in local database: {total_count}")
        
        # Get sample articles
        sample_articles = db.query(News).limit(5).all()
        
        if sample_articles:
            print("\n📝 Sample articles:")
            for i, article in enumerate(sample_articles, 1):
                title_preview = article.title[:60] + "..." if len(article.title) > 60 else article.title
                english_preview = article.title_english[:60] + "..." if article.title_english and len(article.title_english) > 60 else article.title_english
                
                print(f"{i}. Chinese: {title_preview}")
                print(f"   English: {english_preview or '❌ No English translation'}")
                print(f"   Date: {article.collection_date}")
                print()
            
            # Count articles with English translations
            with_english = db.query(News).filter(News.title_english.isnot(None)).count()
            print(f"✅ Articles with English translations: {with_english}/{total_count}")
            print(f"📈 Translation coverage: {(with_english/total_count*100):.1f}%")
        else:
            print("❌ No articles found in local database")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_local_database() 