#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.content_scraper import ContentScraper
import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_encoding_step_by_step():
    """Debug encoding issues step by step in the content scraping process"""
    
    # Test with a People's Daily article URL
    test_url = "http://world.people.com.cn/n1/2025/0530/c1002-40491493.html"
    
    print(f"=== DEBUGGING ENCODING FOR: {test_url} ===\n")
    
    # Step 1: Test direct requests with different encoding methods
    print("STEP 1: Testing direct requests with different encoding methods")
    print("-" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        # Method 3: Use apparent encoding (the working one)
        print("Method 3: Use apparent encoding (the working one)")
        response3 = requests.get(test_url, headers=headers, timeout=30)
        if response3.apparent_encoding:
            response3.encoding = response3.apparent_encoding
        print(f"  Used encoding: {response3.encoding}")
        
        soup3 = BeautifulSoup(response3.text, 'html.parser')
        title3 = soup3.find('title')
        if title3:
            print(f"  Title text: {title3.get_text()[:100]}...")
        
        # Check different content selectors
        print("\n  Testing different content selectors:")
        
        selectors_to_test = [
            "div.text_c",
            "div.show_text", 
            "div.article_content",
            "div.text_content",
            "div.rm_txt_con",
            ".article-content",
            "#article-content"
        ]
        
        for selector in selectors_to_test:
            content = soup3.select(selector)
            if content:
                sample_text = content[0].get_text()[:200]
                print(f"    ✅ {selector}: Found content - {sample_text}...")
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in sample_text)
                has_garbled = any(char in ['', '锛', '浼'] for char in sample_text)
                print(f"      Has Chinese: {has_chinese}, Has garbled: {has_garbled}")
            else:
                print(f"    ❌ {selector}: No content found")
        
        # Also check for paragraphs within content areas
        print("\n  Testing paragraph selectors within content areas:")
        content_areas = soup3.select("div.text_c, div.show_text, div.article_content")
        if content_areas:
            for i, area in enumerate(content_areas):
                paragraphs = area.find_all('p')
                if paragraphs:
                    sample_text = ' '.join([p.get_text() for p in paragraphs[:3]])[:200]
                    print(f"    ✅ Content area {i+1} paragraphs: {sample_text}...")
                    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in sample_text)
                    has_garbled = any(char in ['', '锛', '浼'] for char in sample_text)
                    print(f"      Has Chinese: {has_chinese}, Has garbled: {has_garbled}")
        
        print()
        
    except Exception as e:
        print(f"Error in step 1: {e}")
    
    # Step 2: Test ContentScraper method
    print("STEP 2: Testing ContentScraper.fetch_page_content method")
    print("-" * 60)
    
    try:
        scraper = ContentScraper()
        soup = scraper.fetch_page_content(test_url)
        
        if soup:
            title = soup.find('title')
            if title:
                print(f"  ContentScraper title: {title.get_text()[:100]}...")
            
            # Test different selectors again with ContentScraper's result
            print("\n  Testing selectors with ContentScraper's soup:")
            selectors_to_test = [
                "div.text_c",
                "div.show_text", 
                "div.article_content",
                "div.text_content",
                "div.rm_txt_con"
            ]
            
            for selector in selectors_to_test:
                content = soup.select(selector)
                if content:
                    sample_text = content[0].get_text()[:200]
                    print(f"    ✅ {selector}: {sample_text}...")
                    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in sample_text)
                    has_garbled = any(char in ['', '锛', '浼'] for char in sample_text)
                    print(f"      Has Chinese: {has_chinese}, Has garbled: {has_garbled}")
                else:
                    print(f"    ❌ {selector}: No content found")
        else:
            print("  ContentScraper failed to fetch content")
        
        scraper.close()
        print()
        
    except Exception as e:
        print(f"Error in step 2: {e}")

if __name__ == "__main__":
    debug_encoding_step_by_step() 