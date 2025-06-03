import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use PostgreSQL in production, SQLite in development
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Local development with SQLite
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
    # Production with PostgreSQL
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 