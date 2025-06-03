#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.models import News
from datetime import datetime

def check_guancha_articles():
    print("Checking Guancha articles in database...")
    db = SessionLocal()
    
    try:
        # Get Guancha articles from today
        today = datetime.now().date()
        articles = db.query(News).filter(
            News.source_url.like('%guancha.cn%'),
            News.collection_date == today
        ).all()
        
        print(f"Found {len(articles)} Guancha articles for {today}")
        
        for i, article in enumerate(articles[:10]):  # Show first 10
            print(f"\n{i+1}. ID: {article.id}")
            print(f"   Title: {article.title}")
            print(f"   Title English: {article.title_english}")
            print(f"   Source Section: {article.source_section}")
            print(f"   URL: {article.source_url}")
            print(f"   Date: {article.collection_date}")
            
            # Check if title is garbled
            if article.title:
                try:
                    # Check if title can be properly decoded
                    encoded = article.title.encode('utf-8')
                    decoded = encoded.decode('utf-8')
                    print(f"   UTF-8 Check: OK")
                except Exception as e:
                    print(f"   UTF-8 Check: FAILED - {e}")
        
    finally:
        db.close()

def check_all_articles_today():
    print("\n" + "="*50)
    print("Checking all articles from today...")
    db = SessionLocal()
    
    try:
        today = datetime.now().date()
        articles = db.query(News).filter(News.collection_date == today).all()
        
        print(f"Total articles from {today}: {len(articles)}")
        
        # Group by source
        sources = {}
        for article in articles:
            url = article.source_url
            if 'people.com.cn' in url:
                source = "People's Daily"
            elif 'thepaper.cn' in url:
                source = "The Paper"
            elif 'gov.cn' in url:
                source = "State Council"
            elif 'stats.gov.cn' in url:
                source = "NBS"
            elif 'gwytb.gov.cn' in url:
                source = "Taiwan Affairs"
            elif 'mod.gov.cn' in url:
                source = "MND"
            elif 'guancha.cn' in url:
                source = "Guancha"
            else:
                source = "Other"
            
            if source not in sources:
                sources[source] = []
            sources[source].append(article)
        
        print("\nBy source:")
        for source, articles in sources.items():
            print(f"  {source}: {len(articles)} articles")
            if articles and 'Guancha' in source:
                print(f"    Sample: {articles[0].title}")
                print(f"    Section: {articles[0].source_section}")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_guancha_articles()
    check_all_articles_today() 