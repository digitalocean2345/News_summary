"""
Quick test for the updated society.people.com.cn selector
"""

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import News
from app.services.scraper_config import get_selector_config

def test_society_selector():
    """Test the updated selector for society.people.com.cn"""
    
    print("🧪 Testing Society People's Daily Selector")
    print("=" * 45)
    
    # Get a society.people.com.cn article
    engine = create_engine("sqlite:///./news.db", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find a society article
        society_article = db.query(News).filter(
            News.source_domain == "society.people.com.cn"
        ).first()
        
        if not society_article:
            print("❌ No society.people.com.cn articles found in database")
            return
        
        print(f"📰 Testing article: {society_article.title[:50]}...")
        print(f"🔗 URL: {society_article.source_url}")
        
        # Get selector config
        config = get_selector_config("society.people.com.cn")
        print(f"🎯 Using selector: {config.content_selector}")
        
        # Fetch page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print("🌐 Fetching page...")
        response = requests.get(society_article.source_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch page: {response.status_code}")
            return
        
        print(f"✅ Page fetched: {len(response.content)} bytes")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test the new selector
        print(f"\n🔍 Testing selector: {config.content_selector}")
        content_elements = soup.select(config.content_selector)
        
        if content_elements:
            print(f"✅ Found {len(content_elements)} content elements")
            
            total_text = ""
            for i, element in enumerate(content_elements):
                text = element.get_text(strip=True)
                total_text += text + " "
                print(f"   📝 Paragraph {i+1}: {len(text)} chars")
                if len(text) > 0:
                    preview = text[:80] + "..." if len(text) > 80 else text
                    print(f"      Preview: {preview}")
            
            print(f"\n📏 Total content length: {len(total_text)} characters")
            
            if len(total_text) >= 100:
                print("🎉 SUCCESS: Substantial content found!")
                
                # Save a preview to see the quality
                preview = total_text[:300] + "..." if len(total_text) > 300 else total_text
                print(f"\n📄 Content preview:")
                print(f"   {preview}")
                
            else:
                print("⚠️ WARNING: Content too short")
        
        else:
            print("❌ No content found with the selector")
            
            # Try to see what's actually on the page
            print("\n🔍 Checking page structure...")
            
            # Look for potential content containers
            potential_selectors = [
                'div.rm_txt_con',
                'div.rm_txt_con p',
                'div[class*="txt"]',
                'div[class*="content"]',
                '.article',
                'article'
            ]
            
            for selector in potential_selectors:
                elements = soup.select(selector)
                if elements:
                    text_len = sum(len(el.get_text()) for el in elements)
                    print(f"   ✅ {selector}: {len(elements)} elements, {text_len} chars")
                else:
                    print(f"   ❌ {selector}: No elements")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_society_selector() 