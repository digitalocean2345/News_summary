import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine
from models.models import Base

def init_database():
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("Dropped all existing tables")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Created all tables")
    print("Database initialized successfully")

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialization complete!")
