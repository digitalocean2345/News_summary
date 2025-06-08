#!/usr/bin/env python3
"""
Debug script to test the FastAPI application directly
Run this on the server to diagnose the issue
"""

import sys
import os
import traceback
from datetime import datetime

def test_app_import():
    """Test if the app can be imported successfully"""
    print("🔍 Testing app import...")
    try:
        from app.main import app
        print("✅ App imported successfully")
        return app
    except Exception as e:
        print(f"❌ App import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return None

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    try:
        from app.database import SessionLocal, engine
        from sqlalchemy import text
        
        # Test engine connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM news"))
            count = result.scalar()
            print(f"✅ Database connected - found {count} news articles")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Test the health endpoint directly"""
    print("\n🔍 Testing health endpoint logic...")
    try:
        from app.main import health_check
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Call the health check function directly
            import asyncio
            result = asyncio.run(health_check(db))
            print(f"✅ Health endpoint returned: {result}")
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_minimal_server():
    """Test running a minimal FastAPI server"""
    print("\n🔍 Testing minimal FastAPI server...")
    try:
        from fastapi import FastAPI
        import uvicorn
        
        # Create minimal app
        minimal_app = FastAPI()
        
        @minimal_app.get("/test")
        async def test():
            return {"status": "working", "timestamp": datetime.now().isoformat()}
        
        print("✅ Minimal app created successfully")
        print("💡 You can test this by running:")
        print("   python debug_server_issue.py --run-minimal")
        
        return True
    except Exception as e:
        print(f"❌ Minimal server test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def run_minimal_server():
    """Run a minimal server for testing"""
    print("🚀 Starting minimal test server on port 8001...")
    from fastapi import FastAPI
    import uvicorn
    
    minimal_app = FastAPI()
    
    @minimal_app.get("/test")
    async def test():
        return {"status": "working", "timestamp": datetime.now().isoformat()}
    
    @minimal_app.get("/health")
    async def health():
        return {"status": "healthy", "server": "minimal"}
    
    try:
        uvicorn.run(minimal_app, host="127.0.0.1", port=8001, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    """Main diagnostic function"""
    print("🔧 FastAPI Application Diagnostics")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--run-minimal":
        run_minimal_server()
        return
    
    # Run all tests
    results = []
    
    app = test_app_import()
    results.append(("App Import", app is not None))
    
    db_ok = test_database_connection()
    results.append(("Database Connection", db_ok))
    
    if app:
        health_ok = test_health_endpoint()
        results.append(("Health Endpoint", health_ok))
    
    minimal_ok = test_minimal_server()
    results.append(("Minimal Server Setup", minimal_ok))
    
    # Print summary
    print("\n" + "=" * 50)
    print("🏁 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print("\n💡 NEXT STEPS:")
    if not results[0][1]:  # App import failed
        print("1. Fix app import issues first")
        print("2. Check if all dependencies are installed")
        print("3. Check if database file exists and is accessible")
    elif not results[1][1]:  # Database failed
        print("1. Check database file permissions")
        print("2. Initialize database tables if needed")
        print("3. Run: python -c \"from app.database import engine; print(engine.url)\"")
    else:
        print("1. Try running minimal server: python debug_server_issue.py --run-minimal")
        print("2. Test with: curl http://127.0.0.1:8001/health")
        print("3. If minimal server works, issue is with Gunicorn configuration")

if __name__ == "__main__":
    main() 