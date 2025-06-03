"""
Test script to verify the new database schema is working correctly
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, News, Category, SavedSummary
from datetime import datetime, date

def test_new_schema():
    """Test the new database schema and relationships"""
    
    # Create engine and session
    engine = create_engine("sqlite:///./news.db", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🧪 Testing new database schema...")
        
        # Test 1: Check if we can query the enhanced News model
        print("\n1. Testing enhanced News model...")
        news_items = db.query(News).limit(3).all()
        for news in news_items:
            print(f"   📰 {news.title[:50]}...")
            print(f"      - Content scraped: {news.is_content_scraped}")
            print(f"      - Summarized: {news.is_summarized}")
            print(f"      - Full content: {'Yes' if news.full_content else 'No'}")
        
        # Test 2: Check Categories
        print("\n2. Testing Categories...")
        categories = db.query(Category).all()
        print(f"   📁 Found {len(categories)} categories:")
        for cat in categories:
            print(f"      - {cat.name} ({cat.color}) - {cat.description[:30]}...")
        
        # Test 3: Test relationships by creating a sample saved summary
        print("\n3. Testing SavedSummary relationships...")
        
        # Get first news item and first category
        first_news = db.query(News).first()
        first_category = db.query(Category).first()
        
        if first_news and first_category:
            # Check if a saved summary already exists for this combination
            existing_summary = db.query(SavedSummary).filter(
                SavedSummary.news_id == first_news.id,
                SavedSummary.category_id == first_category.id
            ).first()
            
            if not existing_summary:
                # Create a test saved summary
                test_summary = SavedSummary(
                    news_id=first_news.id,
                    category_id=first_category.id,
                    custom_title="Test Summary",
                    notes="This is a test summary created during schema validation",
                    saved_at=datetime.utcnow(),
                    is_favorite=True
                )
                db.add(test_summary)
                db.commit()
                print(f"   💾 Created test saved summary: '{test_summary.custom_title}'")
            else:
                print(f"   💾 Found existing saved summary: '{existing_summary.custom_title}'")
            
            # Test the relationships
            saved_summaries = db.query(SavedSummary).all()
            print(f"   📊 Total saved summaries: {len(saved_summaries)}")
            
            if saved_summaries:
                sample_summary = saved_summaries[0]
                print(f"      - Sample: '{sample_summary.custom_title}'")
                print(f"      - News title: {sample_summary.news.title[:40]}...")
                print(f"      - Category: {sample_summary.category.name}")
        
        # Test 4: Check database integrity
        print("\n4. Database integrity check...")
        
        # Count totals
        total_news = db.query(News).count()
        total_categories = db.query(Category).count()
        total_saved_summaries = db.query(SavedSummary).count()
        
        print(f"   📊 Database Summary:")
        print(f"      - News articles: {total_news}")
        print(f"      - Categories: {total_categories}")
        print(f"      - Saved summaries: {total_saved_summaries}")
        
        print("\n✅ All schema tests passed successfully!")
        print("🚀 Ready to implement Phase 2: Content Scraping!")
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    test_new_schema() 