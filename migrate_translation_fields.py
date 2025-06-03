"""
Migration script to add translation-related fields to the News table
Run this script to add support for translated content storage
"""

import sqlite3
from datetime import datetime
import urllib.parse

def migrate_translation_fields():
    """
    Add translation-related fields to the News table:
    - full_content_english: translated content
    - summary_english: translated summary  
    - content_language: language detection
    - source_domain: extracted domain for selector mapping
    - is_content_translated: translation status tracking
    - content_translated_at: translation timestamp
    """
    
    # Connect to the database
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting translation fields migration...")
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(news)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Define new columns to add
        new_columns = [
            ("full_content_english", "TEXT"),
            ("summary_english", "TEXT"), 
            ("content_language", "VARCHAR(5)"),
            ("source_domain", "VARCHAR(100)"),
            ("is_content_translated", "BOOLEAN DEFAULT 0"),
            ("content_translated_at", "DATETIME")
        ]
        
        # Add new columns
        print("Adding translation-related columns...")
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE news ADD COLUMN {column_name} {column_type}")
                    print(f"  ✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"  ⚠️ Column {column_name} might already exist: {e}")
        
        # Populate source_domain and content_language for existing records
        print("\nPopulating source domains and language detection...")
        cursor.execute("SELECT id, source_url FROM news WHERE source_domain IS NULL")
        news_items = cursor.fetchall()
        
        updated_count = 0
        for news_id, source_url in news_items:
            try:
                # Extract domain from URL
                parsed_url = urllib.parse.urlparse(source_url)
                domain = parsed_url.netloc
                
                # Detect language based on domain
                if any(chinese_domain in domain for chinese_domain in ['people.com.cn', '.cn', 'xinhua', 'cctv']):
                    language = 'zh'
                else:
                    language = 'en'  # Default to English for other domains
                
                # Update the record
                cursor.execute("""
                    UPDATE news 
                    SET source_domain = ?, content_language = ?
                    WHERE id = ?
                """, (domain, language, news_id))
                
                updated_count += 1
                
            except Exception as e:
                print(f"  ⚠️ Could not process URL {source_url}: {e}")
        
        print(f"  ✅ Updated {updated_count} records with source domain and language")
        
        # Commit changes
        conn.commit()
        
        # Display summary
        cursor.execute("SELECT COUNT(*) FROM news WHERE content_language = 'zh'")
        chinese_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news WHERE content_language = 'en'")
        english_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news")
        total_count = cursor.fetchone()[0]
        
        print(f"\n✅ Translation fields migration completed successfully!")
        print(f"\n📊 Language Distribution:")
        print(f"  - Chinese articles: {chinese_count}")
        print(f"  - English articles: {english_count}")
        print(f"  - Total articles: {total_count}")
        
        # Show some sample domains
        print(f"\n🌐 Sample Source Domains:")
        cursor.execute("SELECT DISTINCT source_domain, COUNT(*) as count FROM news GROUP BY source_domain ORDER BY count DESC LIMIT 5")
        domains = cursor.fetchall()
        for domain, count in domains:
            print(f"  - {domain}: {count} articles")
        
        print(f"\n🚀 Ready to implement content scraping with translation support!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_translation_fields() 