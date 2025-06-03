"""
Test script for Phase 5 - Basic UI for Content Display
Tests the new UI components, templates, and API endpoints
"""

import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import News, Category
import os

def test_static_files():
    """Test 1: Verify static files exist"""
    print("📁 Test 1: Static Files")
    print("-" * 20)
    
    static_files = [
        "app/static/css/main.css",
        "app/static/js/content-manager.js"
    ]
    
    for file_path in static_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} exists ({size} bytes)")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def test_templates():
    """Test 2: Verify templates exist"""
    print("\n📄 Test 2: Templates")
    print("-" * 18)
    
    templates = [
        "app/templates/article_detail.html",
        "app/templates/categories.html",
        "app/templates/calendar.html"
    ]
    
    for template_path in templates:
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ {template_path} exists ({len(content)} chars)")
                
                # Check for key elements
                if template_path.endswith('article_detail.html'):
                    if 'data-action="scrape-content"' in content:
                        print("   ✅ Contains scrape button")
                    if 'language-toggle' in content:
                        print("   ✅ Contains language toggle")
                    if 'category-grid' in content:
                        print("   ✅ Contains category grid")
        else:
            print(f"❌ {template_path} missing")
            return False
    
    return True

def test_database_schema():
    """Test 3: Verify database has required data"""
    print("\n🗄️ Test 3: Database Schema")
    print("-" * 24)
    
    try:
        engine = create_engine("sqlite:///./news.db", echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check articles
        articles = db.query(News).limit(5).all()
        print(f"📰 Found {len(articles)} sample articles")
        
        if articles:
            article = articles[0]
            print(f"   Sample: {article.title[:50]}...")
            print(f"   Has content fields: {hasattr(article, 'full_content')}")
            print(f"   Has translation fields: {hasattr(article, 'full_content_english')}")
            print(f"   Has status fields: {hasattr(article, 'is_content_scraped')}")
        
        # Check categories
        categories = db.query(Category).all()
        print(f"📁 Found {len(categories)} categories")
        
        for cat in categories[:3]:
            print(f"   - {cat.name}: {cat.description}")
        
        db.close()
        return len(articles) > 0 and len(categories) > 0
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api_endpoints():
    """Test 4: Test API endpoints (if server is running)"""
    print("\n🌐 Test 4: API Endpoints")
    print("-" * 22)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test basic health
        response = requests.get(f"{base_url}/api/debug/articles", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Articles API working ({data['count']} articles)")
            
            if data['count'] > 0:
                # Test article detail API
                article_id = data['articles'][0]['id']
                detail_response = requests.get(f"{base_url}/api/articles/{article_id}", timeout=5)
                if detail_response.status_code == 200:
                    print(f"✅ Article detail API working (ID: {article_id})")
                else:
                    print(f"❌ Article detail API failed: {detail_response.status_code}")
        else:
            print(f"❌ Articles API failed: {response.status_code}")
            return False
        
        # Test categories API
        cat_response = requests.get(f"{base_url}/api/categories", timeout=5)
        if cat_response.status_code == 200:
            categories = cat_response.json()
            print(f"✅ Categories API working ({len(categories)} categories)")
        else:
            print(f"❌ Categories API failed: {cat_response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Server not running or not accessible: {e}")
        print("   Start server with: uvicorn app.main:app --reload")
        return False

def test_css_classes():
    """Test 5: Verify CSS classes are defined"""
    print("\n🎨 Test 5: CSS Classes")
    print("-" * 19)
    
    css_file = "app/static/css/main.css"
    if not os.path.exists(css_file):
        print("❌ CSS file not found")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    required_classes = [
        '.article-detail',
        '.content-actions',
        '.language-toggle',
        '.status-badge',
        '.category-grid',
        '.btn-primary',
        '.content-text'
    ]
    
    for class_name in required_classes:
        if class_name in css_content:
            print(f"✅ {class_name} defined")
        else:
            print(f"❌ {class_name} missing")
            return False
    
    return True

def main():
    """Run all Phase 5 tests"""
    print("🚀 Phase 5 UI Testing")
    print("=" * 21)
    
    tests = [
        ("Static Files", test_static_files),
        ("Templates", test_templates),
        ("Database Schema", test_database_schema),
        ("API Endpoints", test_api_endpoints),
        ("CSS Classes", test_css_classes)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 15)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Phase 5 UI implementation complete!")
        print("\n📋 Next Steps:")
        print("1. Start the server: uvicorn app.main:app --reload")
        print("2. Visit http://localhost:8000 to see the calendar")
        print("3. Click on a date to see headlines")
        print("4. Click on an article title to see the detail view")
        print("5. Test content scraping and category saving")
    else:
        print("⚠️ Some tests failed - check implementation")

if __name__ == "__main__":
    main() 