#!/usr/bin/env python3
"""
Test script to check API response encoding
"""

import requests
import json

def test_api_encoding():
    """Test the API response encoding"""
    try:
        response = requests.get('http://localhost:8000/api/debug/articles')
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"Total articles: {data['count']}")
            
            if data['articles']:
                first_article = data['articles'][0]
                
                print(f"\nFirst article:")
                print(f"ID: {first_article['id']}")
                print(f"Title (repr): {repr(first_article['title'])}")
                print(f"Title (display): {first_article['title']}")
                print(f"Title English: {first_article.get('title_english', 'N/A')}")
                
                # Check if title contains Chinese characters
                title = first_article['title']
                chinese_chars = [char for char in title if '\u4e00' <= char <= '\u9fff']
                print(f"Chinese characters found: {len(chinese_chars)}")
                
                if chinese_chars:
                    print("✅ Chinese text is properly encoded!")
                else:
                    print("❌ No Chinese characters detected - possible encoding issue")
                    
                    # Try to detect garbled patterns
                    garbled_patterns = ['ç', 'â', '¦', 'å', 'è', 'ä']
                    garbled_found = [p for p in garbled_patterns if p in title]
                    if garbled_found:
                        print(f"Garbled patterns found: {garbled_found}")
        else:
            print(f"API request failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_encoding() 