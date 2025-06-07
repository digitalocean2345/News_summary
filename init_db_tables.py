#!/usr/bin/env python3
"""
Initialize database tables for Railway PostgreSQL
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add the app directory to the path so we can import models
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from models.models import Base
from database import DATABASE_URL

def create_tables():
    """Create all database tables"""
    print("🚀 Initializing database tables...")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found!")
        return False
    
    print(f"📊 Database URL: {DATABASE_URL[:50]}...")
    
    try:
        # Create engine
        if DATABASE_URL.startswith('postgres://'):
            db_url = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        else:
            db_url = DATABASE_URL
            
        engine = create_engine(
            db_url,
            echo=True,  # Show SQL commands
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10
        )
        
        print("🔗 Connecting to database...")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
        
        print("📋 Creating tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ All tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT name 
                FROM sqlite_master
                WHERE type='table'
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📊 Created tables: {', '.join(tables)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Railway Database Table Initialization")
    print("=" * 50)
    
    success = create_tables()
    
    if success:
        print("\n🎉 Database initialization complete!")
        print("✅ Your Railway app should now work properly!")
    else:
        print("\n❌ Database initialization failed!")
        print("💡 Check your DATABASE_URL environment variable") 