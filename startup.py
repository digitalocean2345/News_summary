#!/usr/bin/env python3
"""
Startup script for App Engine deployment
"""

import os
import sys

def setup_directories():
    """Ensure required directories exist"""
    directories = [
        'app/templates',
        'app/static',
        '/tmp'  # For SQLite in production
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            except Exception as e:
                print(f"⚠️ Could not create directory {directory}: {e}")

def initialize_database():
    """Initialize database tables"""
    try:
        from app.database import engine
        from app.models.models import Base
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")

def main():
    """Main startup function"""
    print("🚀 Starting News Summary Application...")
    
    # Setup directories
    setup_directories()
    
    # Initialize database
    initialize_database()
    
    print("✅ Startup completed successfully")

if __name__ == "__main__":
    main() 