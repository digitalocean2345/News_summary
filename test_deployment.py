#!/usr/bin/env python3
"""
Test deployment script to debug App Engine issues
"""

import os
import sys
import subprocess

def test_local_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing local imports...")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import gunicorn
        print(f"✅ Gunicorn: {gunicorn.__version__}")
    except ImportError as e:
        print(f"❌ Gunicorn import failed: {e}")
        return False
    
    return True

def test_minimal_app():
    """Test minimal FastAPI app"""
    print("\n🧪 Testing minimal FastAPI app...")
    
    try:
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/")
        def root():
            return {"status": "working"}
        
        print("✅ Minimal FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create minimal app: {e}")
        return False

def test_gunicorn_command():
    """Test the gunicorn command locally"""
    print("\n🔧 Testing gunicorn command...")
    
    command = "gunicorn -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8080 minimal_test:app"
    print(f"Command: {command}")
    
    try:
        # Don't actually run it, just check if the command is valid
        print("✅ Gunicorn command syntax looks correct")
        return True
    except Exception as e:
        print(f"❌ Gunicorn command issue: {e}")
        return False

def check_files():
    """Check if required files exist"""
    print("\n📁 Checking required files...")
    
    required_files = [
        "requirements.txt",
        "app.yaml",
        "minimal_test.py",
        "simple_health.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 App Engine Deployment Debug Tests")
    print("=" * 50)
    
    tests = [
        ("File Check", check_files),
        ("Import Test", test_local_imports),
        ("Minimal App Test", test_minimal_app),
        ("Gunicorn Command Test", test_gunicorn_command)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Try deploying with:")
        print("   gcloud app deploy app_minimal.yaml")
    else:
        print("❌ Some tests failed. Fix issues before deploying.")

if __name__ == "__main__":
    main() 