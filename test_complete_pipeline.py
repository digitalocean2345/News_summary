#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.content_scraper import ContentScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_pipeline():
    """Test the complete content scraping and translation pipeline"""
    
    # Test with a People's Daily article URL
    test_url = "http://world.people.com.cn/n1/2025/0530/c1002-40491493.html"
    
    print(f"=== TESTING COMPLETE PIPELINE ===")
    print(f"URL: {test_url}\n")
    
    try:
        scraper = ContentScraper()
        result = scraper.scrape_article_content(test_url, 'zh')
        
        if result['success']:
            content = result['content']
            print(f"✅ Content scraping successful!")
            print(f"   Content length: {len(content)} characters")
            print(f"   Scraping time: {result['scraping_time_seconds']:.2f}s")
            print(f"   Content preview (first 300 chars):")
            print(f"   {content[:300]}...")
            
            # Check for proper Chinese characters (no garbled text)
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in content)
            has_garbled = any(char in ['�', '锛', '浼'] for char in content[:500])  # Check first 500 chars
            
            print(f"\n   ✅ Encoding check:")
            print(f"      Has Chinese characters: {has_chinese}")
            print(f"      Has garbled text: {has_garbled}")
            
            if has_chinese and not has_garbled:
                print(f"      🎉 Encoding is perfect!")
            else:
                print(f"      ⚠️  Potential encoding issues detected")
            
            # Check translation if available
            if result.get('content_english'):
                english_content = result['content_english']
                print(f"\n   ✅ Translation successful!")
                print(f"      English content length: {len(english_content)} characters")
                print(f"      Translation time: {result.get('translation_time_seconds', 0):.2f}s")
                print(f"      English preview (first 200 chars):")
                print(f"      {english_content[:200]}...")
                
                # Check if translation looks reasonable
                has_english = any(char.isalpha() and ord(char) < 128 for char in english_content)
                has_chinese_in_translation = any('\u4e00' <= char <= '\u9fff' for char in english_content)
                
                print(f"\n      Translation quality check:")
                print(f"         Has English text: {has_english}")
                print(f"         Still has Chinese: {has_chinese_in_translation}")
                
                if has_english and not has_chinese_in_translation:
                    print(f"         🎉 Translation quality looks good!")
                else:
                    print(f"         ⚠️  Translation may have issues")
            else:
                print(f"\n   ❌ Translation failed or not available")
                if result.get('translation_error'):
                    print(f"      Error: {result['translation_error']}")
        else:
            print(f"❌ Content scraping failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        scraper.close()
        
    except Exception as e:
        print(f"❌ Pipeline test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_pipeline() 