#!/usr/bin/env python3
"""
Database initialization script for Railway deployment
"""
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.models.models import Base
from app.database import engine
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def verify_database():
    """Verify database connection and tables"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection verified")
            
            # Check if main tables exist
            tables = ['news', 'categories', 'comments', 'saved_summaries']
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"✅ Table '{table}' exists with {count} records")
                except Exception as e:
                    logger.warning(f"⚠️ Table '{table}' might not exist: {e}")
            
            return True
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Railway database initialization...")
    
    # Check if we're in Railway environment
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("🚂 Railway environment detected")
    else:
        logger.info("🏠 Local environment detected")
    
    # Initialize database
    if init_database():
        logger.info("🔍 Verifying database setup...")
        if verify_database():
            logger.info("🎉 Database initialization completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Database verification failed")
            sys.exit(1)
    else:
        logger.error("❌ Database initialization failed")
        sys.exit(1) 