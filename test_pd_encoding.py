#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

def test_peoples_daily_encoding():
    """Test what encoding People's Daily actually uses"""
    test_urls = [
        "http://fanfu.people.com.cn/",
        "http://renshi.people.com.cn/",
        "http://world.people.com.cn/GB/157278/index.html",
        "http://society.people.com.cn/GB/136657/index.html",
        "http://finance.people.com.cn/GB/70846/index.html"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    for url in test_urls:
        try:
            print(f"\n=== Testing {url} ===")
            response = requests.get(url, headers=headers, timeout=30)
            
            print(f"Status: {response.status_code}")
            print(f"Default encoding: {response.encoding}")
            print(f"Apparent encoding: {response.apparent_encoding}")
            
            # Test with different encodings
            encodings_to_test = ['utf-8', 'gb2312', 'gbk', response.apparent_encoding]
            
            for encoding in encodings_to_test:
                if encoding:
                    try:
                        response.encoding = encoding
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Find some Chinese text to test
                        links = soup.find_all('a', href=True)
                        for link in links[:3]:
                            title = link.get_text().strip()
                            if title and any('\u4e00' <= char <= '\u9fff' for char in title):
                                print(f"  {encoding}: {title}")
                                # Check for garbled characters
                                if '绔' in title or '棣' in title or 'ㄥ' in title:
                                    print(f"    ❌ GARBLED!")
                                else:
                                    print(f"    ✅ OK")
                                break
                    except Exception as e:
                        print(f"  {encoding}: Error - {e}")
                        
        except Exception as e:
            print(f"Error fetching {url}: {e}")

if __name__ == "__main__":
    test_peoples_daily_encoding() 