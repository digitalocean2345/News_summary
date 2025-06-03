"""
Step-by-step debugging script for content scraping
Test each component individually to identify issues
"""

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import News
from app.services.scraper_config import get_selector_config
import time

def test_step_1_database_connection():
    """Test 1: Database connection and article retrieval"""
    print("🔧 Step 1: Testing database connection...")
    
    try:
        engine = create_engine("sqlite:///./news.db", echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Get a sample article
        article = db.query(News).filter(News.is_content_scraped == False).first()
        if not article:
            article = db.query(News).first()
        
        if article:
            print(f"   ✅ Database connected successfully")
            print(f"   📰 Test article: {article.title[:50]}...")
            print(f"   🌐 URL: {article.source_url}")
            print(f"   🏢 Domain: {article.source_domain}")
            return article
        else:
            print(f"   ❌ No articles found in database")
            return None
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return None
    finally:
        db.close()

def test_step_2_url_fetch(url):
    """Test 2: Basic URL fetching"""
    print(f"\n🌐 Step 2: Testing URL fetch...")
    print(f"   🔗 URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=10)
        fetch_time = time.time() - start_time
        
        print(f"   ⏱️ Fetch time: {fetch_time:.2f} seconds")
        print(f"   📊 Status code: {response.status_code}")
        print(f"   📏 Content length: {len(response.content)} bytes")
        print(f"   🔤 Encoding: {response.encoding}")
        
        if response.status_code == 200:
            print(f"   ✅ URL fetch successful")
            return response.content
        else:
            print(f"   ❌ URL fetch failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ URL fetch error: {e}")
        return None

def test_step_3_html_parsing(content):
    """Test 3: HTML parsing with BeautifulSoup"""
    print(f"\n🔍 Step 3: Testing HTML parsing...")
    
    try:
        soup = BeautifulSoup(content, 'html.parser')
        
        # Basic HTML structure analysis
        title_tag = soup.find('title')
        print(f"   📄 Page title: {title_tag.get_text()[:100] if title_tag else 'No title found'}...")
        
        # Look for common content containers
        common_selectors = [
            'div.show_text',
            'div.article_content', 
            'div.content',
            'article',
            '.article',
            '.content'
        ]
        
        print(f"   🔍 Testing common selectors:")
        for selector in common_selectors:
            elements = soup.select(selector)
            if elements:
                text_length = sum(len(el.get_text()) for el in elements)
                print(f"      ✅ {selector}: {len(elements)} elements, {text_length} chars")
            else:
                print(f"      ❌ {selector}: No elements found")
        
        # Check if there's any substantial text content
        all_text = soup.get_text()
        print(f"   📏 Total page text: {len(all_text)} characters")
        
        return soup
        
    except Exception as e:
        print(f"   ❌ HTML parsing error: {e}")
        return None

def test_step_4_selector_config(domain):
    """Test 4: Selector configuration"""
    print(f"\n⚙️ Step 4: Testing selector configuration...")
    print(f"   🏢 Domain: {domain}")
    
    try:
        config = get_selector_config(domain)
        print(f"   🎯 Content selector: {config.content_selector}")
        print(f"   🏷️ Title selector: {config.title_selector}")
        print(f"   🗑️ Remove selectors: {config.remove_selectors}")
        
        return config
        
    except Exception as e:
        print(f"   ❌ Selector config error: {e}")
        return None

def test_step_5_content_extraction(soup, config):
    """Test 5: Content extraction with selectors"""
    print(f"\n📝 Step 5: Testing content extraction...")
    
    try:
        # Test content selector
        print(f"   🎯 Testing content selector: {config.content_selector}")
        content_elements = soup.select(config.content_selector)
        
        if content_elements:
            print(f"      ✅ Found {len(content_elements)} content elements")
            
            total_text = ""
            for i, element in enumerate(content_elements):
                text = element.get_text(strip=True)
                total_text += text + " "
                print(f"      📝 Element {i+1}: {len(text)} chars")
                if len(text) > 0:
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"         Preview: {preview}")
            
            print(f"   📏 Total extracted content: {len(total_text)} characters")
            
            if len(total_text) >= 100:
                print(f"   ✅ Substantial content found!")
                return total_text
            else:
                print(f"   ⚠️ Content too short (< 100 chars)")
                return total_text
        else:
            print(f"      ❌ No elements found with content selector")
            
            # Try alternative selectors
            print(f"   🔄 Trying alternative selectors...")
            alternatives = [
                'div[class*="content"]',
                'div[class*="text"]', 
                'div[class*="article"]',
                'p',
                'div p'
            ]
            
            for alt_selector in alternatives:
                alt_elements = soup.select(alt_selector)
                if alt_elements:
                    alt_text = " ".join([el.get_text(strip=True) for el in alt_elements])
                    if len(alt_text) > 100:
                        print(f"      ✅ Alternative {alt_selector}: {len(alt_text)} chars")
                        return alt_text
                    else:
                        print(f"      ⚠️ Alternative {alt_selector}: {len(alt_text)} chars (too short)")
            
            return None
            
    except Exception as e:
        print(f"   ❌ Content extraction error: {e}")
        return None

def main():
    """Run all debugging steps"""
    print("🐛 Content Scraping Step-by-Step Debugging")
    print("=" * 50)
    
    # Step 1: Database connection
    article = test_step_1_database_connection()
    if not article:
        print("❌ Cannot proceed without test article")
        return
    
    # Step 2: URL fetch
    content = test_step_2_url_fetch(article.source_url)
    if not content:
        print("❌ Cannot proceed without webpage content")
        return
    
    # Step 3: HTML parsing
    soup = test_step_3_html_parsing(content)
    if not soup:
        print("❌ Cannot proceed without parsed HTML")
        return
    
    # Step 4: Selector configuration
    config = test_step_4_selector_config(article.source_domain)
    if not config:
        print("❌ Cannot proceed without selector config")
        return
    
    # Step 5: Content extraction
    extracted_content = test_step_5_content_extraction(soup, config)
    
    # Summary
    print(f"\n📋 DEBUGGING SUMMARY")
    print("=" * 30)
    print(f"🎯 Article: {article.title[:50]}...")
    print(f"🌐 Domain: {article.source_domain}")
    print(f"✅ URL Fetch: {'Success' if content else 'Failed'}")
    print(f"✅ HTML Parse: {'Success' if soup else 'Failed'}")
    print(f"✅ Config Load: {'Success' if config else 'Failed'}")
    print(f"✅ Content Extract: {'Success' if extracted_content and len(extracted_content) >= 100 else 'Failed'}")
    
    if extracted_content and len(extracted_content) >= 100:
        print(f"🎉 DEBUGGING SUCCESSFUL - Found {len(extracted_content)} characters of content!")
    else:
        print(f"❌ DEBUGGING FAILED - Need to investigate selector configuration")

if __name__ == "__main__":
    main() 