"""
Database migration script to add new functionality
Run this script to update your existing database with the new schema
"""

import sqlite3
from datetime import datetime

def migrate_database():
    """
    Migrate the existing database to support new functionality:
    - Add new columns to News table
    - Create Category table
    - Create SavedSummary table
    """
    
    # Connect to the database
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    
    try:
        print("Starting database migration...")
        
        # Add new columns to News table
        print("Adding new columns to News table...")
        
        # Check if columns already exist before adding them
        cursor.execute("PRAGMA table_info(news)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            ("full_content", "TEXT"),
            ("summary", "TEXT"),
            ("is_content_scraped", "BOOLEAN DEFAULT 0"),
            ("is_summarized", "BOOLEAN DEFAULT 0"),
            ("content_scraped_at", "DATETIME"),
            ("summarized_at", "DATETIME")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE news ADD COLUMN {column_name} {column_type}")
                    print(f"  ✓ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"  ⚠ Column {column_name} might already exist: {e}")
        
        # Create Category table
        print("Creating Category table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                created_at DATETIME NOT NULL,
                color VARCHAR(7)
            )
        """)
        print("  ✓ Category table created")
        
        # Create SavedSummary table
        print("Creating SavedSummary table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                custom_title VARCHAR(200),
                notes TEXT,
                saved_at DATETIME NOT NULL,
                is_favorite BOOLEAN DEFAULT 0,
                FOREIGN KEY (news_id) REFERENCES news (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        print("  ✓ SavedSummary table created")
        
        # Insert default categories
        print("Adding default categories...")
        default_categories = [
            ("Economy", "Economic news and financial updates", "#2E8B57"),  # Sea Green
            ("Society", "Social issues and community news", "#4169E1"),     # Royal Blue
            ("Politics", "Political developments and governance", "#DC143C"), # Crimson
            ("Technology", "Tech innovations and digital trends", "#FF8C00"), # Dark Orange
            ("International", "Global news and international relations", "#9932CC"), # Dark Orchid
            ("Environment", "Environmental and climate news", "#228B22"),   # Forest Green
            ("Health", "Health and medical news", "#B22222"),              # Fire Brick
            ("Education", "Educational developments and research", "#4682B4") # Steel Blue
        ]
        
        for name, description, color in default_categories:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO categories (name, description, created_at, color)
                    VALUES (?, ?, ?, ?)
                """, (name, description, datetime.utcnow(), color))
                print(f"  ✓ Added category: {name}")
            except sqlite3.IntegrityError:
                print(f"  ⚠ Category {name} already exists")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        
        # Display summary
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news")
        news_count = cursor.fetchone()[0]
        
        print(f"\nDatabase Summary:")
        print(f"  - News articles: {news_count}")
        print(f"  - Categories: {category_count}")
        print(f"  - Ready for content scraping and summarization!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 