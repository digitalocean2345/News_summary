"""
Test script to verify the comment system functionality
"""

import requests
import json
from datetime import datetime

# Base URL - adjust if your server runs on a different port
BASE_URL = "http://localhost:8000"

def test_comment_system():
    """Test the complete comment system functionality"""
    
    print("🧪 Testing Comment System Functionality")
    print("=" * 50)
    
    # Test 1: Get all categories
    print("\n1. Testing category retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/api/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"   ✅ Found {len(categories)} existing categories")
            for cat in categories:
                print(f"      - {cat['name']}: {cat.get('description', 'No description')}")
        else:
            print(f"   ❌ Failed to get categories: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Server not running. Please start your FastAPI server first.")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Create a new category
    print("\n2. Testing category creation...")
    try:
        new_category = {
            "name": "Test Category",
            "description": "A test category for the comment system",
            "color": "#FF6B6B"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/categories",
            headers={"Content-Type": "application/json"},
            data=json.dumps(new_category)
        )
        
        if response.status_code == 200:
            created_category = response.json()
            print(f"   ✅ Created category: {created_category['name']} (ID: {created_category['id']})")
            test_category_id = created_category['id']
        else:
            print(f"   ❌ Failed to create category: {response.status_code}")
            if response.status_code == 400:
                print("   💡 Category might already exist")
                # Try to get existing category
                response = requests.get(f"{BASE_URL}/api/categories")
                if response.status_code == 200:
                    categories = response.json()
                    test_category = next((cat for cat in categories if cat['name'] == 'Test Category'), None)
                    if test_category:
                        test_category_id = test_category['id']
                        print(f"   📋 Using existing category (ID: {test_category_id})")
                    else:
                        print("   ❌ Could not find or create test category")
                        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Get a news article to comment on
    print("\n3. Finding a news article to test with...")
    try:
        # This is a simplified test - in reality you'd get an actual article ID
        # For testing purposes, let's assume article ID 1 exists
        test_article_id = 1
        print(f"   📰 Using article ID: {test_article_id}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Add a comment
    print("\n4. Testing comment creation...")
    try:
        test_comment = {
            "comment_text": "This is a test comment for the new comment system!",
            "user_name": "Test User",
            "category_id": test_category_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/comments?news_id={test_article_id}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_comment)
        )
        
        if response.status_code == 200:
            created_comment = response.json()
            print(f"   ✅ Created comment: {created_comment['id']}")
            print(f"      Author: {created_comment['user_name']}")
            print(f"      Category: {created_comment['category_name']}")
            print(f"      Text: {created_comment['comment_text'][:50]}...")
        else:
            print(f"   ❌ Failed to create comment: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 5: Get comments for the article
    print("\n5. Testing comment retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/api/comments/{test_article_id}")
        
        if response.status_code == 200:
            comments = response.json()
            print(f"   ✅ Found {len(comments)} comments for article {test_article_id}")
            for comment in comments:
                print(f"      - {comment['user_name']}: {comment['comment_text'][:30]}...")
        else:
            print(f"   ❌ Failed to get comments: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 6: Get comments by category
    print("\n6. Testing category-based comment retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/api/comments/category/{test_category_id}")
        
        if response.status_code == 200:
            comments = response.json()
            print(f"   ✅ Found {len(comments)} comments in test category")
            for comment in comments:
                print(f"      - {comment['user_name']}: {comment['comment_text'][:30]}...")
        else:
            print(f"   ❌ Failed to get category comments: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Comment system test completed!")
    print("\n📋 Next Steps:")
    print("   1. Start your FastAPI server: uvicorn app.main:app --reload")
    print("   2. Visit an article page: http://localhost:8000/article/1")
    print("   3. Try adding comments with categories")
    print("   4. Visit: http://localhost:8000/comments to browse by category")
    
    return True

def check_database_structure():
    """Check if the database has the required structure"""
    
    print("\n🔍 Checking database structure...")
    
    import sqlite3
    import os
    
    db_path = "news.db"
    if not os.path.exists(db_path):
        print("   ❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if comments table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments'")
        if not cursor.fetchone():
            print("   ❌ Comments table not found")
            return False
        
        print("   ✅ Comments table exists")
        
        # Check table structure
        cursor.execute("PRAGMA table_info(comments)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        required_columns = ['id', 'news_id', 'category_id', 'comment_text', 'user_name', 'created_at']
        missing_columns = set(required_columns) - set(column_names)
        
        if missing_columns:
            print(f"   ❌ Missing columns: {missing_columns}")
            return False
        
        print("   ✅ All required columns present")
        
        # Check if there are any news articles
        cursor.execute("SELECT COUNT(*) FROM news")
        news_count = cursor.fetchone()[0]
        print(f"   📰 Found {news_count} news articles")
        
        # Check if there are any categories
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        print(f"   📁 Found {category_count} categories")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Comment System Test Suite...")
    
    # Check database first
    db_ok = check_database_structure()
    
    if db_ok:
        # Run API tests
        test_comment_system()
    else:
        print("\n💥 Database structure check failed.")
        print("Please run the migration script first: python migrate_comments.py") 