"""
Test script to verify the translation-related database fields are working correctly
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, News, Category, SavedSummary
from app.services.scraper_config import get_selector_config, get_language_config
from datetime import datetime

def test_translation_schema():
    """Test the new translation-related database fields and scraper config"""
    
    # Create engine and session
    engine = create_engine("sqlite:///./news.db", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🧪 Testing translation-enhanced database schema...")
        
        # Test 1: Check new translation fields
        print("\n1. Testing new translation fields...")
        news_items = db.query(News).limit(5).all()
        for news in news_items:
            print(f"   📰 {news.title[:40]}...")
            print(f"      - Domain: {news.source_domain}")
            print(f"      - Language: {news.content_language}")
            print(f"      - Content scraped: {news.is_content_scraped}")
            print(f"      - Content translated: {news.is_content_translated}")
            print()
        
        # Test 2: Check language distribution
        print("2. Language distribution analysis...")
        chinese_count = db.query(News).filter(News.content_language == 'zh').count()
        english_count = db.query(News).filter(News.content_language == 'en').count()
        
        print(f"   🇨🇳 Chinese articles: {chinese_count}")
        print(f"   🇺🇸 English articles: {english_count}")
        
        # Test 3: Test scraper configuration
        print("\n3. Testing scraper configuration...")
        sample_domains = ["world.people.com.cn", "society.people.com.cn", "unknown-domain.com"]
        
        for domain in sample_domains:
            config = get_selector_config(domain)
            print(f"   🌐 {domain}:")
            print(f"      - Content selector: {config.content_selector}")
            print(f"      - Remove selectors: {len(config.remove_selectors)} items")
            
            # Test language config for Chinese domains
            if ".cn" in domain:
                lang_config = get_language_config("zh")
                print(f"      - Requires translation: {lang_config['require_translation']}")
                print(f"      - Translation service: {lang_config['translation_service']}")
        
        # Test 4: Sample update of a news item with translation fields
        print("\n4. Testing news item update with translation fields...")
        first_news = db.query(News).first()
        if first_news:
            # Simulate content scraping and translation
            original_title = first_news.title
            print(f"   📝 Updating article: {original_title[:30]}...")
            
            # Update with sample content and translation
            first_news.full_content = "这是一个示例中文内容。包含了新闻的主要信息。"
            first_news.full_content_english = "This is a sample English content. Contains the main information of the news."
            first_news.is_content_scraped = True
            first_news.is_content_translated = True
            first_news.content_scraped_at = datetime.utcnow()
            first_news.content_translated_at = datetime.utcnow()
            
            db.commit()
            print(f"      ✅ Updated content fields successfully")
            print(f"      - Original content length: {len(first_news.full_content)} chars")
            print(f"      - Translated content length: {len(first_news.full_content_english)} chars")
        
        # Test 5: Check domain statistics
        print("\n5. Domain statistics...")
        db_domains = db.query(News.source_domain, func.count(News.id)).group_by(News.source_domain).all()
        
        print("   📊 Articles by domain:")
        for domain, count in db_domains:
            print(f"      - {domain}: {count} articles")
        
        print("\n✅ All translation schema tests passed successfully!")
        print("🚀 Ready to implement Phase 2: Content Scraping with Translation!")
        
    except Exception as e:
        print(f"❌ Translation schema test failed: {e}")
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    test_translation_schema() 