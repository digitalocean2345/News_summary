#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.models import News
from datetime import datetime

def check_encoding_issues():
    print("Checking for encoding issues in database...")
    db = SessionLocal()
    
    try:
        today = datetime.now().date()
        all_articles = db.query(News).filter(News.collection_date == today).all()
        
        print(f"Total articles today: {len(all_articles)}")
        
        # Group by domain
        domains = {}
        garbled_articles = []
        
        for article in all_articles:
            url = article.source_url
            if '//' in url:
                domain = url.split('//')[1].split('/')[0]
            else:
                domain = 'unknown'
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(article)
            
            # Check for garbled text (common garbled characters from encoding issues)
            if article.title and any(char in article.title for char in ['绔', '棣', 'ㄥ', '介', '璺', '璁']):
                garbled_articles.append({
                    'id': article.id,
                    'title': article.title,
                    'url': article.source_url,
                    'domain': domain
                })
        
        print("\nBy domain:")
        for domain, articles in domains.items():
            print(f"  {domain}: {len(articles)} articles")
        
        print(f"\nFound {len(garbled_articles)} articles with potential encoding issues:")
        for i, article in enumerate(garbled_articles[:5]):  # Show first 5
            print(f"\n{i+1}. ID: {article['id']}")
            print(f"   Domain: {article['domain']}")
            print(f"   Title: {article['title']}")
            print(f"   URL: {article['url']}")
        
        # Check People's Daily specifically
        pd_articles = [a for domain, articles in domains.items() 
                      if 'people.com.cn' in domain for a in articles]
        print(f"\nPeople's Daily articles: {len(pd_articles)}")
        if pd_articles:
            sample = pd_articles[0]
            print(f"Sample title: {sample.title}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_encoding_issues() 