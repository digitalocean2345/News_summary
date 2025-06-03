#!/usr/bin/env python3
"""
Test script to diagnose and fix Chinese text encoding issues
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.models import News
from app.scrapers.peoples_daily_scraper import PeoplesDailyScraper
from app.scrapers.base_scraper import BaseScraper
import chardet
import requests
from bs4 import BeautifulSoup

def test_encoding_detection():
    """Test encoding detection with sample Chinese text"""
    print("=== Testing Encoding Detection ===")
    
    # Sample Chinese text in different encodings
    chinese_text = "端午假期首日全国铁路预计发送旅客1780万人次"
    
    # Test UTF-8 encoding
    utf8_bytes = chinese_text.encode('utf-8')
    print(f"UTF-8 bytes: {utf8_bytes}")
    
    # Test GB2312 encoding
    gb2312_bytes = chinese_text.encode('gb2312')
    print(f"GB2312 bytes: {gb2312_bytes}")
    
    # Test chardet detection
    utf8_detected = chardet.detect(utf8_bytes)
    gb2312_detected = chardet.detect(gb2312_bytes)
    
    print(f"UTF-8 detection: {utf8_detected}")
    print(f"GB2312 detection: {gb2312_detected}")
    
    # Test decoding
    print(f"UTF-8 decoded: {utf8_bytes.decode('utf-8')}")
    print(f"GB2312 decoded: {gb2312_bytes.decode('gb2312')}")

async def test_scraper_encoding():
    """Test the improved scraper encoding handling"""
    print("\n=== Testing Scraper Encoding ===")
    
    scraper = PeoplesDailyScraper()
    
    # Test with a People's Daily URL
    test_url = "http://renshi.people.com.cn/"
    
    try:
        content = await scraper.fetch_page(test_url)
        
        if content:
            print(f"Successfully fetched content, length: {len(content)}")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find some Chinese text
            links = soup.select('a[href*="/n1/"]')[:3]
            
            print("Sample titles found:")
            for i, link in enumerate(links):
                title = link.get_text(strip=True)
                print(f"  {i+1}. {title}")
                
                # Test encoding of the title
                title_bytes = title.encode('utf-8')
                detected = chardet.detect(title_bytes)
                print(f"     Encoding detected: {detected}")
        else:
            print("Failed to fetch content")
            
    except Exception as e:
        print(f"Error testing scraper: {e}")
    finally:
        await scraper.close_session()

def test_database_encoding():
    """Test encoding of data in the database"""
    print("\n=== Testing Database Encoding ===")
    
    db = next(get_db())
    
    try:
        # Get a few sample articles
        articles = db.query(News).limit(5).all()
        
        print(f"Found {len(articles)} articles in database")
        
        for article in articles:
            print(f"\nArticle ID: {article.id}")
            print(f"Title: {article.title}")
            print(f"Title English: {article.title_english}")
            
            # Test if the title is properly encoded
            if article.title:
                title_bytes = article.title.encode('utf-8')
                detected = chardet.detect(title_bytes)
                print(f"Title encoding detected: {detected}")
                
                # Try to fix garbled text
                try:
                    # If it looks like double-encoded UTF-8
                    if 'ç' in article.title or 'â' in article.title:
                        # Try to decode as latin-1 then encode as utf-8
                        fixed_title = article.title.encode('latin-1').decode('utf-8')
                        print(f"Potential fix: {fixed_title}")
                except Exception as fix_error:
                    print(f"Could not fix encoding: {fix_error}")
                    
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db.close()

async def test_fresh_scraping():
    """Test scraping fresh content with new encoding handling"""
    print("\n=== Testing Fresh Scraping ===")
    
    scraper = PeoplesDailyScraper()
    
    try:
        # Get fresh news
        articles = await scraper.get_news()
        
        print(f"Scraped {len(articles)} articles")
        
        for i, article in enumerate(articles[:3]):
            print(f"\nArticle {i+1}:")
            print(f"Title: {article['title']}")
            print(f"URL: {article['source_url']}")
            
            # Test encoding
            if article['title']:
                title_bytes = article['title'].encode('utf-8')
                detected = chardet.detect(title_bytes)
                print(f"Encoding: {detected}")
                
    except Exception as e:
        print(f"Scraping error: {e}")
    finally:
        await scraper.close_session()

def fix_database_encoding():
    """Attempt to fix encoding issues in the database"""
    print("\n=== Attempting to Fix Database Encoding ===")
    
    db = next(get_db())
    
    try:
        # Get articles with potential encoding issues
        articles = db.query(News).filter(
            News.title.contains('ç') | 
            News.title.contains('â') |
            News.title.contains('¦') |
            News.title.contains('å')
        ).limit(10).all()
        
        print(f"Found {len(articles)} articles with potential encoding issues")
        
        fixed_count = 0
        for article in articles:
            try:
                original_title = article.title
                
                # Try to fix double-encoded UTF-8
                if any(char in original_title for char in ['ç', 'â', '¦', 'å']):
                    # Method 1: Decode as latin-1 then encode as utf-8
                    try:
                        fixed_title = original_title.encode('latin-1').decode('utf-8')
                        
                        # Verify the fix looks reasonable (contains Chinese characters)
                        if any('\u4e00' <= char <= '\u9fff' for char in fixed_title):
                            print(f"Fixing: '{original_title}' -> '{fixed_title}'")
                            article.title = fixed_title
                            fixed_count += 1
                            
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        # Method 2: Try other encoding combinations
                        try:
                            fixed_title = original_title.encode('cp1252').decode('utf-8')
                            if any('\u4e00' <= char <= '\u9fff' for char in fixed_title):
                                print(f"Fixing (cp1252): '{original_title}' -> '{fixed_title}'")
                                article.title = fixed_title
                                fixed_count += 1
                        except:
                            print(f"Could not fix: {original_title}")
                            
            except Exception as e:
                print(f"Error fixing article {article.id}: {e}")
        
        if fixed_count > 0:
            print(f"\nCommitting {fixed_count} fixes to database...")
            db.commit()
            print("✅ Database fixes committed")
        else:
            print("No fixes applied")
            
    except Exception as e:
        print(f"Fix error: {e}")
        db.rollback()
    finally:
        db.close()

async def main():
    """Run all encoding tests"""
    print("🔍 Chinese Text Encoding Diagnostic Tool")
    print("=" * 50)
    
    # Run tests
    test_encoding_detection()
    await test_scraper_encoding()
    test_database_encoding()
    await test_fresh_scraping()
    
    # Ask user if they want to attempt fixes
    response = input("\nDo you want to attempt to fix database encoding issues? (y/n): ")
    if response.lower() == 'y':
        fix_database_encoding()
    
    print("\n✅ Encoding diagnostic complete!")

if __name__ == "__main__":
    asyncio.run(main()) 