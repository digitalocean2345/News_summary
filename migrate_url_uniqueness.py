#!/usr/bin/env python3
"""
Migration script to add URL uniqueness constraint to the news table.
This script will:
1. Check for existing duplicate URLs
2. Remove duplicate entries (keeping the oldest one)
3. Add the unique constraint to prevent future duplicates
"""

import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_db():
    """Connect to the SQLite database"""
    return sqlite3.connect('news.db')

def find_duplicate_urls(cursor):
    """Find all duplicate URLs in the database"""
    query = """
    SELECT source_url, COUNT(*) as count, GROUP_CONCAT(id) as ids
    FROM news 
    GROUP BY source_url 
    HAVING COUNT(*) > 1
    ORDER BY count DESC
    """
    cursor.execute(query)
    return cursor.fetchall()

def remove_duplicates(cursor):
    """Remove duplicate URLs, keeping the oldest entry (lowest ID)"""
    duplicates = find_duplicate_urls(cursor)
    
    if not duplicates:
        logger.info("No duplicate URLs found.")
        return 0
    
    logger.info(f"Found {len(duplicates)} URLs with duplicates")
    
    total_removed = 0
    
    for url, count, ids_str in duplicates:
        ids = [int(id_) for id_ in ids_str.split(',')]
        ids.sort()  # Sort to get the oldest (lowest) ID first
        
        # Keep the first (oldest) ID, remove the rest
        ids_to_remove = ids[1:]
        
        logger.info(f"URL: {url[:100]}... has {count} duplicates")
        logger.info(f"Keeping ID {ids[0]}, removing IDs: {ids_to_remove}")
        
        for id_to_remove in ids_to_remove:
            cursor.execute("DELETE FROM news WHERE id = ?", (id_to_remove,))
            total_removed += 1
    
    return total_removed

def add_unique_constraint(cursor):
    """Add unique constraint to source_url column"""
    try:
        # SQLite doesn't support adding constraints to existing tables directly
        # We need to create a new table and copy data
        
        logger.info("Creating new table with unique constraint...")
        
        # Create new table with unique constraint matching the existing schema
        cursor.execute("""
        CREATE TABLE news_new (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            title_english TEXT,
            source_url VARCHAR(500) NOT NULL UNIQUE,
            collection_date DATE NOT NULL,
            full_content TEXT,
            summary TEXT,
            is_content_scraped BOOLEAN DEFAULT 0,
            is_summarized BOOLEAN DEFAULT 0,
            content_scraped_at DATETIME,
            summarized_at DATETIME,
            full_content_english TEXT,
            summary_english TEXT,
            content_language VARCHAR(5),
            source_domain VARCHAR(100),
            is_content_translated BOOLEAN DEFAULT 0,
            content_translated_at DATETIME,
            source_section VARCHAR(255)
        )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
        INSERT INTO news_new 
        SELECT 
            id, title, title_english, source_url, collection_date,
            full_content, summary, 
            COALESCE(is_content_scraped, 0), 
            COALESCE(is_summarized, 0),
            content_scraped_at, summarized_at, full_content_english, 
            summary_english, content_language, source_domain,
            COALESCE(is_content_translated, 0),
            content_translated_at, source_section
        FROM news
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE news")
        
        # Rename new table
        cursor.execute("ALTER TABLE news_new RENAME TO news")
        
        logger.info("Successfully added unique constraint to source_url")
        
    except Exception as e:
        logger.error(f"Error adding unique constraint: {str(e)}")
        raise

def verify_uniqueness(cursor):
    """Verify that all URLs are now unique"""
    duplicates = find_duplicate_urls(cursor)
    if duplicates:
        logger.error(f"Still found {len(duplicates)} duplicate URLs after migration!")
        return False
    else:
        logger.info("All URLs are now unique.")
        return True

def test_unique_constraint(cursor):
    """Test that the unique constraint is working"""
    try:
        # Try to insert a duplicate URL
        cursor.execute("SELECT source_url FROM news LIMIT 1")
        existing_url = cursor.fetchone()[0]
        
        cursor.execute("""
        INSERT INTO news (title, source_url, collection_date) 
        VALUES ('Test Title', ?, '2023-01-01')
        """, (existing_url,))
        
        logger.error("Unique constraint test failed - duplicate was allowed!")
        return False
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            logger.info("Unique constraint test passed - duplicates are properly rejected")
            return True
        else:
            logger.error(f"Unexpected integrity error: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error during constraint test: {str(e)}")
        return False

def main():
    """Main migration function"""
    logger.info("Starting URL uniqueness migration...")
    
    try:
        # Connect to database
        conn = connect_db()
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Check current state
        cursor.execute("SELECT COUNT(*) FROM news")
        initial_count = cursor.fetchone()[0]
        logger.info(f"Initial article count: {initial_count}")
        
        # Find and remove duplicates
        removed_count = remove_duplicates(cursor)
        logger.info(f"Removed {removed_count} duplicate articles")
        
        # Add unique constraint
        add_unique_constraint(cursor)
        
        # Verify uniqueness
        if not verify_uniqueness(cursor):
            raise Exception("Uniqueness verification failed")
        
        # Test unique constraint
        if not test_unique_constraint(cursor):
            raise Exception("Unique constraint test failed")
        
        # Check final state
        cursor.execute("SELECT COUNT(*) FROM news")
        final_count = cursor.fetchone()[0]
        logger.info(f"Final article count: {final_count}")
        
        # Commit transaction
        conn.commit()
        logger.info(f"Migration completed successfully!")
        logger.info(f"Summary: {initial_count} -> {final_count} articles ({removed_count} duplicates removed)")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main() 