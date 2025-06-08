#!/usr/bin/env python3
"""
Check the news_aggregator.db database
"""
import sqlite3

def check_aggregator_db():
    """Check the news_aggregator.db database"""
    print("📅 Checking news_aggregator.db...")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('news_aggregator.db')
        cursor = conn.cursor()
        
        # Get table name
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        # Assuming table is 'news' or similar, let's try common names
        table_name = None
        for possible_name in ['news', 'news_articles', 'articles']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {possible_name}")
                table_name = possible_name
                break
            except:
                continue
        
        if not table_name:
            print("❌ Could not find articles table")
            return
            
        print(f"✅ Using table: {table_name}")
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        print(f"📊 Total articles: {total}")
        
        # Get date counts
        cursor.execute(f"""
            SELECT collection_date, COUNT(*) 
            FROM {table_name} 
            GROUP BY collection_date 
            ORDER BY collection_date DESC
        """)
        
        dates = cursor.fetchall()
        print(f"\n📋 Available dates ({len(dates)} dates):")
        
        for date, count in dates[:15]:
            print(f"  {date}: {count} articles")
        
        # Check June 6th and 7th specifically
        print("\n🔍 Checking June 6th and 7th:")
        for target_date in ['2025-06-06', '2025-06-07']:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE collection_date = ?", (target_date,))
            count = cursor.fetchone()[0]
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {target_date}: {count} articles")
            
            if count > 0:
                # Show sample titles
                cursor.execute(f"SELECT title FROM {table_name} WHERE collection_date = ? LIMIT 3", (target_date,))
                titles = cursor.fetchall()
                for title_row in titles:
                    title = title_row[0][:60] + "..." if len(title_row[0]) > 60 else title_row[0]
                    print(f"    📰 {title}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_aggregator_db() 