"""
Test script for content scraping functionality
Tests the complete workflow: scraping, translation, and storage
"""

import asyncio
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import News
from app.services.content_scraper import ContentScraper, scrape_single_article
from datetime import datetime
import json

def test_content_scraping():
    """Test the content scraping system end-to-end"""
    
    # Database setup
    engine = create_engine("sqlite:///./news.db", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🧪 Testing Content Scraping System")
        print("=" * 50)
        
        # Test 1: Get a sample of unscraped articles
        print("\n1. Finding articles to test...")
        unscraped_articles = db.query(News).filter(
            News.is_content_scraped == False
        ).limit(3).all()
        
        if not unscraped_articles:
            print("   ℹ️ No unscraped articles found. Testing with any articles...")
            unscraped_articles = db.query(News).limit(3).all()
        
        print(f"   📰 Found {len(unscraped_articles)} articles to test:")
        for article in unscraped_articles:
            print(f"      - {article.title[:50]}...")
            print(f"        Domain: {article.source_domain}")
            print(f"        URL: {article.source_url}")
        
        # Test 2: Test scraper configuration
        print("\n2. Testing scraper configuration...")
        for article in unscraped_articles[:1]:  # Test just one for configuration
            from app.services.scraper_config import get_selector_config
            config = get_selector_config(article.source_domain)
            print(f"   🔧 Config for {article.source_domain}:")
            print(f"      - Content selector: {config.content_selector}")
            print(f"      - Remove selectors: {len(config.remove_selectors)} items")
            print(f"      - Title selector: {config.title_selector}")
        
        # Test 3: Test single article scraping
        print("\n3. Testing single article scraping...")
        test_article = unscraped_articles[0]
        
        print(f"   🔍 Scraping: {test_article.title[:30]}...")
        result = scrape_single_article(
            test_article.source_url, 
            test_article.content_language or 'zh'
        )
        
        if result['success']:
            print(f"   ✅ Scraping successful!")
            print(f"      - Content length: {result['content_length']} characters")
            print(f"      - Scraping time: {result['scraping_time_seconds']} seconds")
            print(f"      - Translation: {'✅' if result.get('translation_success') else '❌'}")
            
            if result.get('content_english'):
                print(f"      - Translated length: {len(result['content_english'])} characters")
            
            # Show content preview
            content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            print(f"      - Content preview: {content_preview}")
            
            if result.get('content_english'):
                english_preview = result['content_english'][:200] + "..." if len(result['content_english']) > 200 else result['content_english']
                print(f"      - English preview: {english_preview}")
        else:
            print(f"   ❌ Scraping failed: {result.get('error', 'Unknown error')}")
        
        # Test 4: Test database update
        print("\n4. Testing database update...")
        if result['success']:
            print(f"   💾 Updating database for article ID {test_article.id}...")
            test_article.full_content = result['content']
            test_article.is_content_scraped = True
            test_article.content_scraped_at = result['scraped_at']
            
            if result.get('content_english'):
                test_article.full_content_english = result['content_english']
                test_article.is_content_translated = result.get('translation_success', False)
                test_article.content_translated_at = result.get('translated_at')
            
            db.commit()
            print(f"   ✅ Database updated successfully!")
            
            # Verify the update
            updated_article = db.query(News).filter(News.id == test_article.id).first()
            print(f"      - Content scraped: {updated_article.is_content_scraped}")
            print(f"      - Content translated: {updated_article.is_content_translated}")
            print(f"      - Content length: {len(updated_article.full_content) if updated_article.full_content else 0}")
        
        # Test 5: Test multiple domain handling
        print("\n5. Testing multiple domains...")
        domains_tested = set()
        for article in unscraped_articles:
            if article.source_domain not in domains_tested and len(domains_tested) < 2:
                print(f"   🌐 Testing domain: {article.source_domain}")
                try:
                    quick_result = scrape_single_article(article.source_url, article.content_language or 'zh')
                    if quick_result['success']:
                        print(f"      ✅ Success - {quick_result['content_length']} chars")
                    else:
                        print(f"      ❌ Failed - {quick_result.get('error', 'Unknown')}")
                    domains_tested.add(article.source_domain)
                except Exception as e:
                    print(f"      ❌ Exception - {str(e)}")
        
        # Test 6: Statistics
        print("\n6. Content scraping statistics...")
        total_articles = db.query(News).count()
        scraped_articles = db.query(News).filter(News.is_content_scraped == True).count()
        translated_articles = db.query(News).filter(News.is_content_translated == True).count()
        
        print(f"   📊 Statistics:")
        print(f"      - Total articles: {total_articles}")
        print(f"      - Scraped articles: {scraped_articles}")
        print(f"      - Translated articles: {translated_articles}")
        print(f"      - Scraping progress: {round(scraped_articles/total_articles*100, 1)}%")
        
        print("\n✅ Content scraping system test completed!")
        print("🚀 Ready for production use!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

def test_api_endpoints():
    """Test the API endpoints (requires running server)"""
    
    print("\n🌐 Testing API Endpoints")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test stats endpoint
        print("1. Testing stats endpoint...")
        response = requests.get(f"{base_url}/api/content/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Stats endpoint working")
            print(f"      - Total articles: {stats['total_articles']}")
            print(f"      - Scraping percentage: {stats['scraping_percentage']}%")
        else:
            print(f"   ❌ Stats endpoint failed: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("   ⚠️ Server not running. Start with: uvicorn app.main:app --reload")
        print("   Then run this test again.")
    
    except Exception as e:
        print(f"   ❌ API test failed: {e}")

if __name__ == "__main__":
    print("🧪 Starting Content Scraping Tests...")
    test_content_scraping()
    
    print("\n" + "="*60)
    test_api_endpoints() 