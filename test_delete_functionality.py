"""
Test script for delete functionality of categories and comments
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_category_delete():
    """Test category deletion functionality"""
    print("=== Testing Category Delete Functionality ===")
    
    # First, create a test category
    print("1. Creating a test category...")
    category_data = {
        "name": f"Test Category {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": "A test category for deletion testing",
        "color": "#FF5733"
    }
    
    response = requests.post(f"{BASE_URL}/api/categories", json=category_data)
    if response.status_code == 200:
        created_category = response.json()
        category_id = created_category["id"]
        print(f"✓ Category created successfully with ID: {category_id}")
        print(f"  Name: {created_category['name']}")
        
        # Now try to delete the category
        print(f"2. Deleting category with ID: {category_id}")
        delete_response = requests.delete(f"{BASE_URL}/api/categories/{category_id}")
        
        if delete_response.status_code == 200:
            delete_result = delete_response.json()
            print("✓ Category deleted successfully!")
            print(f"  Message: {delete_result['message']}")
            print(f"  Deleted saved summaries: {delete_result['deleted_saved_summaries']}")
            print(f"  Deleted comments: {delete_result['deleted_comments']}")
        else:
            print(f"✗ Failed to delete category: {delete_response.status_code}")
            print(f"  Error: {delete_response.text}")
    else:
        print(f"✗ Failed to create category: {response.status_code}")
        print(f"  Error: {response.text}")

def test_comment_delete():
    """Test comment deletion functionality"""
    print("\n=== Testing Comment Delete Functionality ===")
    
    # Get all existing news articles to find one we can comment on
    print("1. Getting news articles...")
    response = requests.get(f"{BASE_URL}/api/debug/articles")
    
    if response.status_code == 200:
        articles_data = response.json()
        if articles_data and "articles" in articles_data and articles_data["articles"]:
            news_id = articles_data["articles"][0]["id"]  # Use the first article
            print(f"✓ Found article with ID: {news_id}")
            
            # Create a test comment
            print("2. Creating a test comment...")
            comment_data = {
                "comment_text": f"Test comment created at {datetime.now()}",
                "user_name": "TestUser"
            }
            
            create_response = requests.post(
                f"{BASE_URL}/api/comments?news_id={news_id}", 
                json=comment_data
            )
            
            if create_response.status_code == 200:
                created_comment = create_response.json()
                comment_id = created_comment["id"]
                print(f"✓ Comment created successfully with ID: {comment_id}")
                print(f"  Text: {created_comment['comment_text'][:50]}...")
                
                # Now try to delete the comment
                print(f"3. Deleting comment with ID: {comment_id}")
                delete_response = requests.delete(f"{BASE_URL}/api/comments/{comment_id}")
                
                if delete_response.status_code == 200:
                    delete_result = delete_response.json()
                    print("✓ Comment deleted successfully!")
                    print(f"  Message: {delete_result['message']}")
                    print(f"  Deleted comment info: {delete_result['deleted_comment']}")
                else:
                    print(f"✗ Failed to delete comment: {delete_response.status_code}")
                    print(f"  Error: {delete_response.text}")
            else:
                print(f"✗ Failed to create comment: {create_response.status_code}")
                print(f"  Error: {create_response.text}")
        else:
            print("✗ No articles found to test comment functionality")
    else:
        print(f"✗ Failed to get articles: {response.status_code}")
        print(f"  Error: {response.text}")

def test_nonexistent_deletes():
    """Test deletion of non-existent items"""
    print("\n=== Testing Non-existent Item Deletion ===")
    
    # Try to delete a non-existent category
    print("1. Trying to delete non-existent category (ID: 99999)...")
    response = requests.delete(f"{BASE_URL}/api/categories/99999")
    if response.status_code == 404:
        print("✓ Correctly returned 404 for non-existent category")
    else:
        print(f"✗ Unexpected response: {response.status_code}")
    
    # Try to delete a non-existent comment
    print("2. Trying to delete non-existent comment (ID: 99999)...")
    response = requests.delete(f"{BASE_URL}/api/comments/99999")
    if response.status_code == 404:
        print("✓ Correctly returned 404 for non-existent comment")
    else:
        print(f"✗ Unexpected response: {response.status_code}")

if __name__ == "__main__":
    print("Testing Delete Functionality for Categories and Comments")
    print("=" * 60)
    
    try:
        # Test category deletion
        test_category_delete()
        
        # Test comment deletion
        test_comment_delete()
        
        # Test edge cases
        test_nonexistent_deletes()
        
        print("\n" + "=" * 60)
        print("Delete functionality testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to the API server.")
        print("  Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"✗ An error occurred during testing: {str(e)}") 