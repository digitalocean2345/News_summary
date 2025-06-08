#!/usr/bin/env python3
"""
Test script to verify Microsoft Translator functionality on DigitalOcean droplet
Run this script on your droplet after setting up the API key
"""

import os
import sys
import requests
from datetime import datetime

def test_translation_api_key():
    """Test if the Microsoft Translator API key is properly configured"""
    print("🔑 Testing Microsoft Translator API Key Configuration")
    print("=" * 50)
    
    # Check environment variables
    api_key = os.getenv('MS_TRANSLATOR_KEY')
    location = os.getenv('MS_TRANSLATOR_LOCATION', 'global')
    
    if api_key:
        print(f"✅ MS_TRANSLATOR_KEY: Present (length: {len(api_key)})")
        print(f"✅ MS_TRANSLATOR_LOCATION: {location}")
    else:
        print("❌ MS_TRANSLATOR_KEY: Not found!")
        return False
    
    return True

def test_direct_translation():
    """Test translation functionality directly"""
    print("\n🔤 Testing Direct Translation")
    print("=" * 30)
    
    try:
        # Import the translator service
        sys.path.append('/var/www/news_summary')
        from app.services.translator import MicrosoftTranslator
        
        translator = MicrosoftTranslator()
        
        # Test Chinese to English translation
        test_text = "这是一个测试消息。今天天气很好。"
        print(f"Original text: {test_text}")
        
        result = translator.translate(test_text, from_lang='zh', to_lang='en')
        
        if result:
            print(f"✅ Translation successful!")
            print(f"Translated text: {result}")
            return True
        else:
            print("❌ Translation failed - no result returned")
            return False
            
    except Exception as e:
        print(f"❌ Translation test failed: {str(e)}")
        return False

def test_api_endpoint():
    """Test the translation API endpoint"""
    print("\n🌐 Testing Translation API Endpoint")
    print("=" * 35)
    
    try:
        # Test the health endpoint first
        health_response = requests.get("http://localhost:8000/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ API server is responding")
        else:
            print(f"⚠️ API server health check returned {health_response.status_code}")
        
        # Test the translation endpoint
        translation_response = requests.get("http://localhost:8000/api/test-translation", timeout=30)
        
        if translation_response.status_code == 200:
            result = translation_response.json()
            print("✅ Translation endpoint is working!")
            print(f"Response: {result}")
            return True
        else:
            print(f"❌ Translation endpoint failed with status {translation_response.status_code}")
            print(f"Response: {translation_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        return False

def check_service_status():
    """Check the systemd service status"""
    print("\n⚙️ Checking Service Status")
    print("=" * 25)
    
    try:
        import subprocess
        
        # Check if service is active
        result = subprocess.run(['systemctl', 'is-active', 'news-summary.service'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ news-summary.service is active")
        else:
            print("❌ news-summary.service is not active")
        
        # Get service status
        status_result = subprocess.run(['systemctl', 'status', 'news-summary.service', '--no-pager'], 
                                     capture_output=True, text=True)
        
        print("\nService Status Details:")
        print("-" * 20)
        print(status_result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Service status check failed: {str(e)}")
        return False

def main():
    """Run all translation tests"""
    print(f"🧪 Translation Test Suite - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: API Key Configuration
    if test_translation_api_key():
        tests_passed += 1
    
    # Test 2: Service Status
    if check_service_status():
        tests_passed += 1
    
    # Test 3: Direct Translation
    if test_direct_translation():
        tests_passed += 1
    
    # Test 4: API Endpoint
    if test_api_endpoint():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 25)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Translation is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
        
        print("\n🔧 Troubleshooting Steps:")
        print("1. Verify your Microsoft Translator API key is correct")
        print("2. Check service logs: sudo journalctl -u news-summary.service -f")
        print("3. Restart the service: sudo systemctl restart news-summary.service")
        print("4. Ensure your Azure Translator service is active and has quota")
        
        return 1

if __name__ == "__main__":
    exit(main()) 