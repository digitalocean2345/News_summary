import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use PostgreSQL in production, SQLite in development
DATABASE_URL = os.getenv('DATABASE_URL')

# Railway sometimes provides postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if not DATABASE_URL:
    # Local development with SQLite - use absolute path for App Engine
    if os.getenv('ENVIRONMENT') == 'production':
        # In production (App Engine), create database in /tmp directory
        DATABASE_URL = "sqlite:////tmp/news.db"
    else:
        # Local development
        DATABASE_URL = "sqlite:///./news.db"
    
    engine = create_engine(
        DATABASE_URL, 
        connect_args={
            "check_same_thread": False,
            "isolation_level": None
        },
        echo=False
    )
else:
    # Production with PostgreSQL (Railway)
    engine = create_engine(
        DATABASE_URL, 
        echo=False,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        pool_size=5,         # Connection pool size
        max_overflow=10      # Maximum overflow connections
    )

# Create tables automatically when the module is imported
try:
    from app.models.models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified successfully")
except Exception as e:
    print(f"⚠️ Table creation failed: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 