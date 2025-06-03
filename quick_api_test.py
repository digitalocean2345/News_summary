import requests
import time

# Wait for server to start
time.sleep(3)

try:
    # Test articles API
    r = requests.get('http://localhost:8000/api/debug/articles')
    print(f'API Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'Articles: {data["count"]}')
        
        if data["count"] > 0:
            # Test article detail
            article_id = data["articles"][0]["id"]
            detail_r = requests.get(f'http://localhost:8000/api/articles/{article_id}')
            print(f'Article Detail Status: {detail_r.status_code}')
            
            # Test categories
            cat_r = requests.get('http://localhost:8000/api/categories')
            print(f'Categories Status: {cat_r.status_code}')
            if cat_r.status_code == 200:
                categories = cat_r.json()
                print(f'Categories: {len(categories)}')
                
        print("✅ All API tests passed!")
    else:
        print(f"❌ API test failed: {r.status_code}")
        
except Exception as e:
    print(f"❌ API test error: {e}") 