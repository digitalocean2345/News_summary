#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.models import News
from datetime import datetime

def check_latest_articles():
    print("Checking latest articles to verify encoding fix...")
    db = SessionLocal()
    
    try:
        today = datetime.now().date()
        
        # Get the latest 20 articles from today
        latest_articles = db.query(News).filter(
            News.collection_date == today
        ).order_by(News.id.desc()).limit(20).all()
        
        print(f"Checking latest {len(latest_articles)} articles from today:")
        
        for i, article in enumerate(latest_articles):
            url = article.source_url
            if '//' in url:
                domain = url.split('//')[1].split('/')[0]
            else:
                domain = 'unknown'
            
            print(f"\n{i+1}. ID: {article.id}")
            print(f"   Domain: {domain}")
            print(f"   Title: {article.title}")
            
            # Check for garbled characters
            if article.title and any(char in article.title for char in ['绔', '棣', 'ㄥ', '介', '璺', '璁']):
                print(f"   Status: ❌ GARBLED!")
            else:
                print(f"   Status: ✅ OK")
        
        # Check specifically for Guancha articles
        guancha_articles = db.query(News).filter(
            News.source_url.like('%guancha.cn%'),
            News.collection_date == today
        ).limit(5).all()
        
        print(f"\n=== Guancha Articles (Latest 5) ===")
        for i, article in enumerate(guancha_articles):
            print(f"{i+1}. {article.title}")
            if article.title and any(char in article.title for char in ['绔', '棣', 'ㄥ', '介', '璺', '璁']):
                print(f"   Status: ❌ GARBLED!")
            else:
                print(f"   Status: ✅ OK")
        
        # Check People's Daily articles from latest scraping
        pd_articles = db.query(News).filter(
            News.source_url.like('%people.com.cn%'),
            News.collection_date == today
        ).order_by(News.id.desc()).limit(5).all()
        
        print(f"\n=== People's Daily Articles (Latest 5) ===")
        for i, article in enumerate(pd_articles):
            print(f"{i+1}. {article.title}")
            if article.title and any(char in article.title for char in ['绔', '棣', 'ㄥ', '介', '璺', '璁']):
                print(f"   Status: ❌ GARBLED!")
            else:
                print(f"   Status: ✅ OK")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_latest_articles() 