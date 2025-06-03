"""
Quick offline test for content scraping system
Tests core functionality without network requests or translation
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import News
from app.services.scraper_config import get_selector_config, get_language_config
from bs4 import BeautifulSoup

def test_database_schema():
    """Test 1: Verify database schema has all required fields"""
    print("📋 Test 1: Database Schema")
    print("-" * 25)
    
    try:
        engine = create_engine("sqlite:///./news.db", echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Get a sample article
        article = db.query(News).first()
        if not article:
            print("❌ No articles in database")
            return False
        
        # Check for new translation fields
        required_fields = [
            'full_content', 'full_content_english', 'summary', 'summary_english',
            'content_language', 'source_domain', 'is_content_scraped', 
            'is_content_translated', 'is_summarized'
        ]
        
        print(f"📰 Testing article: {article.title[:30]}...")
        
        missing_fields = []
        for field in required_fields:
            if not hasattr(article, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        else:
            print("✅ All required fields present")
            print(f"   - Domain: {article.source_domain}")
            print(f"   - Language: {article.content_language}")
            print(f"   - Content scraped: {article.is_content_scraped}")
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    finally:
        db.close()

def test_selector_configs():
    """Test 2: Verify selector configurations"""
    print("\n🎯 Test 2: Selector Configurations")
    print("-" * 35)
    
    try:
        domains = [
            "society.people.com.cn", 
            "world.people.com.cn", 
            "politics.people.com.cn",
            "unknown-domain.com"
        ]
        
        for domain in domains:
            config = get_selector_config(domain)
            print(f"🌐 {domain}:")
            print(f"   Content: {config.content_selector}")
            print(f"   Title: {config.title_selector}")
            print(f"   Remove: {len(config.remove_selectors)} items")
        
        # Verify the updated society selector
        society_config = get_selector_config("society.people.com.cn")
        if "div.rm_txt_con p" in society_config.content_selector:
            print("✅ Society selector updated correctly")
        else:
            print("❌ Society selector not updated")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Selector config test failed: {e}")
        return False

def test_html_parsing():
    """Test 3: Test HTML parsing with sample content"""
    print("\n🔍 Test 3: HTML Parsing")
    print("-" * 23)
    
    try:
        # Create sample HTML that mimics People's Daily structure
        sample_html = """
        <html>
        <head><title>Sample News Article</title></head>
        <body>
            <h1 class="title">测试新闻标题</h1>
            <div class="rm_txt_con">
                <p>这是第一段新闻内容，包含了重要的信息。</p>
                <p>这是第二段内容，提供了更多详细信息。</p>
                <p>这是第三段，总结了整个新闻事件。</p>
            </div>
            <div class="ad">广告内容</div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        # Test society selector
        config = get_selector_config("society.people.com.cn")
        content_elements = soup.select(config.content_selector)
        
        if content_elements:
            total_text = " ".join([el.get_text(strip=True) for el in content_elements])
            print(f"✅ Extracted {len(content_elements)} paragraphs")
            print(f"   Total text: {len(total_text)} characters")
            print(f"   Preview: {total_text[:100]}...")
            
            if len(total_text) >= 50:  # Lower threshold for test
                print("✅ Substantial content extracted")
                return True
            else:
                print("❌ Insufficient content")
                return False
        else:
            print("❌ No content extracted")
            return False
            
    except Exception as e:
        print(f"❌ HTML parsing test failed: {e}")
        return False

def test_language_configs():
    """Test 4: Language configuration"""
    print("\n🌐 Test 4: Language Configurations")
    print("-" * 33)
    
    try:
        # Test Chinese config
        zh_config = get_language_config("zh")
        print(f"🇨🇳 Chinese config:")
        print(f"   Requires translation: {zh_config['require_translation']}")
        print(f"   Translation service: {zh_config['translation_service']}")
        
        # Test English config
        en_config = get_language_config("en")
        print(f"🇺🇸 English config:")
        print(f"   Requires translation: {en_config['require_translation']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Language config test failed: {e}")
        return False

def test_api_imports():
    """Test 5: Verify API components can be imported"""
    print("\n🔧 Test 5: API Component Imports")
    print("-" * 32)
    
    try:
        # Test critical imports
        from app.services.content_scraper import ContentScraper
        from app.api.content_endpoints import router
        from app.schemas.schemas import ContentScrapeRequest, ContentScrapeResponse
        
        print("✅ ContentScraper imported")
        print("✅ API router imported")
        print("✅ Schema classes imported")
        
        # Test ContentScraper initialization (without network calls)
        scraper = ContentScraper()
        print("✅ ContentScraper initialized")
        scraper.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Run all quick tests"""
    print("🚀 Quick Offline Content Scraping Tests")
    print("=" * 42)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Selector Configs", test_selector_configs),
        ("HTML Parsing", test_html_parsing),
        ("Language Configs", test_language_configs),
        ("API Imports", test_api_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 15)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED - Content scraping system ready!")
    else:
        print("⚠️ Some tests failed - check configuration")

if __name__ == "__main__":
    main() 