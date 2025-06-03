from app.database import engine
from sqlalchemy import inspect

def check_database():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables: {tables}")
    
    if 'news' in tables:
        columns = inspector.get_columns('news')
        column_names = [col['name'] for col in columns]
        print(f"News table columns: {column_names}")
        
        if 'source_section' in column_names:
            print("✓ source_section column exists")
        else:
            print("✗ source_section column missing")
    else:
        print("News table doesn't exist")

if __name__ == "__main__":
    check_database() 