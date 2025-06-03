"""
Database migration script to add Comment table for the comment system.
Run this script to update your existing database with the new Comment model.
"""

import sqlite3
from datetime import datetime
import os

def migrate_database():
    """Add Comment table to existing database"""
    
    # Database file path
    db_path = "news.db"
    
    if not os.path.exists(db_path):
        print("Database file not found. Please ensure news.db exists.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if comments table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='comments'
        """)
        
        if cursor.fetchone():
            print("Comments table already exists. Migration not needed.")
            conn.close()
            return True
        
        # Create comments table
        cursor.execute("""
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER NOT NULL,
                category_id INTEGER,
                comment_text TEXT NOT NULL,
                user_name VARCHAR(100),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (news_id) REFERENCES news (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        # Create indices for better performance
        cursor.execute("CREATE INDEX idx_comments_news_id ON comments (news_id)")
        cursor.execute("CREATE INDEX idx_comments_category_id ON comments (category_id)")
        cursor.execute("CREATE INDEX idx_comments_created_at ON comments (created_at)")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Successfully added comments table to database!")
        print("   - Added comments table with proper foreign keys")
        print("   - Added performance indices")
        print("   - Migration completed successfully")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    
    db_path = "news.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("PRAGMA table_info(comments)")
        columns = cursor.fetchall()
        
        expected_columns = ['id', 'news_id', 'category_id', 'comment_text', 'user_name', 'created_at']
        actual_columns = [col[1] for col in columns]
        
        print("\n📋 Verification Results:")
        print(f"   Expected columns: {expected_columns}")
        print(f"   Actual columns: {actual_columns}")
        
        missing_columns = set(expected_columns) - set(actual_columns)
        if missing_columns:
            print(f"   ❌ Missing columns: {missing_columns}")
            return False
        
        print("   ✅ All expected columns present")
        
        # Check indices
        cursor.execute("PRAGMA index_list(comments)")
        indices = cursor.fetchall()
        print(f"   📊 Created indices: {len(indices)} total")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration for Comments system...")
    print("=" * 60)
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Verify migration
        print("\n🔍 Verifying migration...")
        verify_success = verify_migration()
        
        if verify_success:
            print("\n🎉 Migration completed successfully!")
            print("You can now use the comment system in your webapp.")
        else:
            print("\n⚠️  Migration completed but verification failed.")
            print("Please check the database manually.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
    
    print("=" * 60) 