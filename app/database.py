import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use PostgreSQL in production, SQLite in development
DATABASE_URL = os.getenv('DATABASE_URL')

# Railway sometimes provides postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if not DATABASE_URL:
    # Local development with SQLite - use absolute path for persistence
    if os.getenv('ENVIRONMENT') == 'production':
        # In production (Digital Ocean), use persistent directory
        # Ensure the directory exists
        db_dir = "/var/www/news_summary"
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        DATABASE_URL = f"sqlite:///{db_dir}/news_aggregator.db"
    else:
        # Local development - use current directory
        DATABASE_URL = "sqlite:///./news_aggregator.db"
    
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
    print(f"✅ Database tables created/verified successfully at: {DATABASE_URL}")
    
    # Set proper permissions for SQLite database on Digital Ocean
    if DATABASE_URL.startswith('sqlite:///') and os.getenv('ENVIRONMENT') == 'production':
        db_file = DATABASE_URL.replace('sqlite:///', '')
        if os.path.exists(db_file):
            import stat
            # Set read/write permissions for owner and group
            os.chmod(db_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
            print(f"✅ Database permissions set for: {db_file}")
            
except Exception as e:
    print(f"⚠️ Table creation failed: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 