#!/usr/bin/env python3
"""
Test script to verify translation functionality based on environment detection
"""
import os
import sys
sys.path.append('.')

from app.scrapers.peoples_daily_scraper import PeoplesDailyScraper
from app.services.translator import MicrosoftTranslator

def test_environment_detection():
    """Test that environment detection works correctly"""
    print("=== Environment Detection Test ===")
    
    # Test local environment (no DATABASE_URL)
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    
    is_production = bool(os.getenv('DATABASE_URL'))
    print(f"Local environment - is_production: {is_production}")
    
    # Test production environment (with DATABASE_URL)
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
    is_production = bool(os.getenv('DATABASE_URL'))
    print(f"Production environment - is_production: {is_production}")
    
    # Clean up
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']

def test_scraper_translation_setting():
    """Test that scrapers are initialized with correct translation setting"""
    print("\n=== Scraper Translation Setting Test ===")
    
    # Test local (translation disabled)
    scraper_local = PeoplesDailyScraper(translate_immediately=False)
    print(f"Local scraper - translate_immediately: {scraper_local.translate_immediately}")
    print(f"Local scraper - translator: {'Initialized' if scraper_local.translator else 'None'}")
    
    # Test production (translation enabled)
    try:
        scraper_prod = PeoplesDailyScraper(translate_immediately=True)
        print(f"Production scraper - translate_immediately: {scraper_prod.translate_immediately}")
        print(f"Production scraper - translator: {'Initialized' if scraper_prod.translator else 'None'}")
    except Exception as e:
        print(f"Production scraper failed (expected if no MS_TRANSLATOR_KEY): {e}")

def test_translator_initialization():
    """Test Microsoft Translator initialization requirements"""
    print("\n=== Translator Initialization Test ===")
    
    # Check if MS_TRANSLATOR_KEY is available
    ms_key = os.getenv('MS_TRANSLATOR_KEY')
    ms_location = os.getenv('MS_TRANSLATOR_LOCATION')
    
    print(f"MS_TRANSLATOR_KEY present: {'Yes' if ms_key else 'No'}")
    print(f"MS_TRANSLATOR_LOCATION: {ms_location or 'Not set'}")
    
    if ms_key:
        try:
            translator = MicrosoftTranslator()
            print("✅ Translator initialized successfully")
            
            # Test translation (only if key is present)
            test_text = "你好世界"
            result = translator.translate(test_text)
            print(f"Translation test: '{test_text}' → '{result}'")
        except Exception as e:
            print(f"❌ Translator initialization failed: {e}")
    else:
        print("⚠️ MS_TRANSLATOR_KEY not found - translation will not work in production")

if __name__ == "__main__":
    test_environment_detection()
    test_scraper_translation_setting()
    test_translator_initialization()
    
    print("\n=== Summary ===")
    print("1. For translation to work on Railway, you need to set:")
    print("   - MS_TRANSLATOR_KEY=your_api_key")
    print("   - MS_TRANSLATOR_LOCATION=your_region")
    print("2. The app will auto-detect production environment via DATABASE_URL")
    print("3. Translation will be enabled automatically in production") 