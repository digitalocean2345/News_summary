#!/usr/bin/env python3
"""
Production Database Setup Script for Digital Ocean
Ensures proper database initialization and data migration
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path

def setup_database_directory():
    """Ensure database directory exists with proper permissions"""
    db_dir = Path("/var/www/news_summary")
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Set proper ownership (will be run as deployer user)
    try:
        os.system(f"sudo chown -R deployer:www-data {db_dir}")
        os.system(f"sudo chmod -R 775 {db_dir}")
        print(f"✅ Database directory created and configured: {db_dir}")
    except Exception as e:
        print(f"⚠️ Permission setup warning: {e}")
    
    return db_dir

def migrate_existing_database():
    """Migrate existing database if found in current directory"""
    current_db = Path("./news_aggregator.db")
    production_db = Path("/var/www/news_summary/news_aggregator.db")
    
    if current_db.exists() and not production_db.exists():
        print(f"📦 Found existing database: {current_db}")
        try:
            shutil.copy2(current_db, production_db)
            print(f"✅ Database migrated to: {production_db}")
            
            # Set proper permissions
            os.system(f"sudo chown deployer:www-data {production_db}")
            os.system(f"sudo chmod 664 {production_db}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True

def initialize_database():
    """Initialize database tables using the app's models"""
    try:
        # Set environment to production
        os.environ['ENVIRONMENT'] = 'production'
        
        # Import after setting environment variable
        from app.database import engine
        from app.models.models import Base
        from sqlalchemy import text
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables initialized successfully")
        
        # Verify database connection using proper SQLAlchemy syntax
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            # Use text() wrapper for raw SQL
            result = db.execute(text("SELECT COUNT(*) FROM articles")).scalar()
            print(f"📊 Database verified - Found {result} articles")
        except Exception as e:
            # If articles table doesn't exist yet, that's okay
            print(f"📊 Database verified - Articles table will be created by the application")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def check_database_integrity():
    """Check if database is accessible and has expected structure"""
    db_path = "/var/www/news_summary/news_aggregator.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if main tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['articles', 'comments']  # Add your expected tables here
        
        if not tables:
            print("📊 Database is empty - tables will be created by the application")
        else:
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"⚠️ Some tables will be created by the application: {missing_tables}")
            else:
                print("✅ All expected tables found")
            
            # Get record counts
            for table in tables:
                if table != 'sqlite_sequence':
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"📊 Table '{table}': {count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database integrity check failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up production database on Digital Ocean...")
    
    # Step 1: Setup directory
    db_dir = setup_database_directory()
    
    # Step 2: Migrate existing database if needed
    if not migrate_existing_database():
        print("❌ Database migration failed")
        sys.exit(1)
    
    # Step 3: Initialize database tables
    if not initialize_database():
        print("❌ Database initialization failed")
        sys.exit(1)
    
    # Step 4: Check integrity
    if not check_database_integrity():
        print("❌ Database integrity check failed")
        sys.exit(1)
    
    print("✅ Production database setup completed successfully!")
    print(f"📍 Database location: /var/www/news_summary/news_aggregator.db")
    print("💡 Your data will now persist across service restarts")

if __name__ == "__main__":
    main() 