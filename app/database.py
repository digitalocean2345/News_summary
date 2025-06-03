from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create SQLite engine with proper UTF-8 support
SQLALCHEMY_DATABASE_URL = "sqlite:///./news.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "isolation_level": None
    },
    echo=False  # Set to True for debugging SQL queries
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 