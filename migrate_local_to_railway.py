#!/usr/bin/env python3
"""
Script to migrate data from local SQLite to Railway PostgreSQL
"""
import os
import sqlite3
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import News, Category, Comment
import json
from datetime import datetime

def export_local_data():
    """Export data from local SQLite database"""
    print("🔍 Exporting data from local SQLite...")
    
    # Connect to local SQLite
    engine = create_engine("sqlite:///./news.db")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Export news articles
        news_articles = db.query(News).all()
        news_data = []
        for article in news_articles:
            news_data.append({
                'title': article.title,
                'title_english': article.title_english,
                'source_url': article.source_url,
                'source_section': article.source_section,
                'collection_date': article.collection_date.isoformat() if article.collection_date else None,
                'full_content': article.full_content,
                'full_content_english': article.full_content_english,
                'summary': article.summary,
                'summary_english': article.summary_english
            })
        
        # Export categories
        categories = db.query(Category).all()
        category_data = []
        for category in categories:
            category_data.append({
                'name': category.name,
                'description': category.description,
                'color': category.color
            })
        
        print(f"✅ Exported {len(news_data)} articles and {len(category_data)} categories")
        
        # Save to JSON file
        export_data = {
            'news': news_data,
            'categories': category_data,
            'exported_at': datetime.now().isoformat()
        }
        
        with open('local_data_export.json', 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print("💾 Data exported to local_data_export.json")
        return export_data
        
    finally:
        db.close()

def import_to_railway():
    """Import data to Railway PostgreSQL database"""
    print("📤 Importing data to Railway...")
    
    # You'll need to set your Railway DATABASE_URL
    railway_db_url = input("Enter your Railway DATABASE_URL (from Railway dashboard): ")
    
    if not railway_db_url:
        print("❌ DATABASE_URL required")
        return
    
    # Load exported data
    try:
        with open('local_data_export.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ local_data_export.json not found. Run export first.")
        return
    
    # Connect to Railway PostgreSQL
    engine = create_engine(railway_db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Import categories first
        for cat_data in data['categories']:
            existing = db.query(Category).filter(Category.name == cat_data['name']).first()
            if not existing:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    color=cat_data['color']
                )
                db.add(category)
        
        # Import news articles
        imported_count = 0
        duplicate_count = 0
        
        for news_data in data['news']:
            # Check if article already exists
            existing = db.query(News).filter(News.source_url == news_data['source_url']).first()
            if existing:
                duplicate_count += 1
                continue
            
            article = News(
                title=news_data['title'],
                title_english=news_data['title_english'],
                source_url=news_data['source_url'],
                source_section=news_data['source_section'],
                collection_date=datetime.fromisoformat(news_data['collection_date']) if news_data['collection_date'] else None,
                full_content=news_data.get('full_content'),
                full_content_english=news_data.get('full_content_english'),
                summary=news_data.get('summary'),
                summary_english=news_data.get('summary_english')
            )
            db.add(article)
            imported_count += 1
        
        db.commit()
        print(f"✅ Imported {imported_count} articles, {duplicate_count} duplicates skipped")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Import failed: {e}")
    finally:
        db.close()

def main():
    print("=== Local to Railway Data Migration ===")
    print("1. Export from local SQLite")
    print("2. Import to Railway PostgreSQL")
    print("3. Both (export then import)")
    
    choice = input("Choose option (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        export_local_data()
    
    if choice in ['2', '3']:
        import_to_railway()
    
    print("\n=== Important Notes ===")
    print("1. This is a ONE-TIME migration")
    print("2. Set up MS_TRANSLATOR_KEY on Railway for future articles")
    print("3. Future articles will be translated automatically on Railway")

if __name__ == "__main__":
    main() 