#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.guancha_scraper import GuanchaScraper

def test_guancha_scraping():
    print("Testing Guancha scraper...")
    scraper = GuanchaScraper()
    
    # Test scraping
    articles = scraper.scrape_page('https://www.guancha.cn/GuoJi%C2%B7ZhanLue/list_1.shtml')
    
    print(f"Found {len(articles)} articles")
    print("\nFirst 5 articles:")
    for i, article in enumerate(articles[:5]):
        print(f"{i+1}. Title: {article['title']}")
        print(f"   URL: {article['source_url']}")
        print(f"   Bytes: {article['title'].encode('utf-8')}")
        print()

def test_full_fetch():
    print("\nTesting full fetch...")
    scraper = GuanchaScraper()
    all_articles = scraper.fetch_news()
    
    print(f"Total articles found: {len(all_articles)}")
    
    # Group by source section
    sections = {}
    for article in all_articles:
        section = article.get('source_section', 'Unknown')
        if section not in sections:
            sections[section] = []
        sections[section].append(article)
    
    print("\nBy section:")
    for section, articles in sections.items():
        print(f"{section}: {len(articles)} articles")
        if articles:
            print(f"  Sample: {articles[0]['title']}")

if __name__ == "__main__":
    test_guancha_scraping()
    test_full_fetch() 