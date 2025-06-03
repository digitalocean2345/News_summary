#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.content_scraper import ContentScraper
from app.services.translator import MicrosoftTranslator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_encoding_fix():
    """Test that Chinese characters are properly handled"""
    
    # Test URLs with Chinese content
    test_urls = [
        "http://world.people.com.cn/GB/157278/index.html",  # People's Daily International
        "http://society.people.com.cn/GB/136657/index.html"  # People's Daily Society
    ]
    
    scraper = ContentScraper()
    
    for url in test_urls:
        print(f"\n=== Testing encoding for: {url} ===")
        
        # Test the fetch_page_content method
        soup = scraper.fetch_page_content(url)
        
        if soup:
            # Find some Chinese text elements
            links = soup.select('a[href*="/n1/"]')[:3]  # Get first 3 links
            
            print(f"Found {len(links)} test links")
            
            for i, link in enumerate(links):
                title = link.get_text(strip=True)
                href = link.get('href')
                
                print(f"Link {i+1}: {title[:100]}...")
                print(f"URL: {href}")
                
                # Check if we have proper Chinese characters (not garbled)
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in title)
                has_garbled = any(char in ['�', '锛', '浼'] for char in title)
                
                print(f"Has Chinese characters: {has_chinese}")
                print(f"Has garbled characters: {has_garbled}")
                
                if has_chinese and not has_garbled:
                    print("✅ Encoding appears correct!")
                else:
                    print("❌ Encoding may be incorrect!")
                
                print("-" * 50)
        else:
            print("❌ Failed to fetch page content")
    
    scraper.close()

def test_translation_encoding():
    """Test that translation handles Chinese characters properly"""
    
    # Test Chinese text
    test_texts = [
        "这是一个测试",  # "This is a test"
        "中国政府发布重要声明",  # "Chinese government releases important statement"
        "北京时间今天上午"  # "Beijing time this morning"
    ]
    
    try:
        translator = MicrosoftTranslator()
        
        for text in test_texts:
            print(f"\n=== Testing translation for: {text} ===")
            
            # Check if original text has proper Chinese characters
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
            print(f"Original text has Chinese: {has_chinese}")
            
            translated = translator.translate(text)
            
            if translated:
                print(f"Original: {text}")
                print(f"Translated: {translated}")
                print("✅ Translation successful!")
            else:
                print("❌ Translation failed!")
                
    except Exception as e:
        print(f"❌ Translation test failed: {e}")

if __name__ == "__main__":
    print("Testing encoding fixes...")
    
    print("\n1. Testing web scraping encoding...")
    test_encoding_fix()
    
    print("\n2. Testing translation encoding...")
    test_translation_encoding()
    
    print("\nTesting complete!") 