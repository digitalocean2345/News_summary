#!/usr/bin/env python3
"""
Script to fix garbled Chinese text encoding in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.models import News
import re

def is_garbled_text(text):
    """Check if text appears to be garbled Chinese"""
    if not text:
        return False
    
    # Common garbled characters that appear when Chinese text is incorrectly encoded
    garbled_patterns = [
        'ç', 'â', '¦', 'å', 'è', 'ä', 'ï', 'ü', 'ö', 'ñ',
        'Â', 'Ã', 'Ä', 'Å', 'Æ', 'Ç', 'È', 'É', 'Ê', 'Ë'
    ]
    
    # Check if text contains garbled patterns
    garbled_count = sum(1 for pattern in garbled_patterns if pattern in text)
    
    # If more than 10% of unique characters are garbled patterns, consider it garbled
    unique_chars = len(set(text))
    if unique_chars > 0 and (garbled_count / unique_chars) > 0.1:
        return True
    
    # Also check for specific garbled sequences common in Chinese text
    garbled_sequences = ['ç«¯', 'åè', 'æ¥å', 'è®¡', 'éè·¯', 'ä¸ä¸']
    return any(seq in text for seq in garbled_sequences)

def fix_encoding(text):
    """Attempt to fix garbled Chinese text encoding"""
    if not text or not is_garbled_text(text):
        return text
    
    # Try different encoding fix methods
    methods = [
        # Method 1: latin-1 -> utf-8 (most common for Chinese garbled text)
        lambda t: t.encode('latin-1').decode('utf-8'),
        
        # Method 2: cp1252 -> utf-8
        lambda t: t.encode('cp1252').decode('utf-8'),
        
        # Method 3: iso-8859-1 -> utf-8
        lambda t: t.encode('iso-8859-1').decode('utf-8'),
    ]
    
    for method in methods:
        try:
            fixed_text = method(text)
            
            # Verify the fix by checking if it contains Chinese characters
            if any('\u4e00' <= char <= '\u9fff' for char in fixed_text):
                # Additional check: make sure it doesn't still look garbled
                if not is_garbled_text(fixed_text):
                    return fixed_text
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    
    # If no method worked, return original text
    return text

def main():
    """Fix encoding issues in the database"""
    print("🔧 Fixing Chinese Text Encoding in Database")
    print("=" * 50)
    
    db = next(get_db())
    
    try:
        # Get all articles
        articles = db.query(News).all()
        print(f"Found {len(articles)} articles in database")
        
        fixed_count = 0
        
        for article in articles:
            original_title = article.title
            original_title_english = article.title_english
            
            # Fix title if garbled
            if original_title and is_garbled_text(original_title):
                fixed_title = fix_encoding(original_title)
                if fixed_title != original_title:
                    print(f"Fixing title: '{original_title}' -> '{fixed_title}'")
                    article.title = fixed_title
                    fixed_count += 1
            
            # Fix English title if garbled
            if original_title_english and is_garbled_text(original_title_english):
                fixed_title_english = fix_encoding(original_title_english)
                if fixed_title_english != original_title_english:
                    print(f"Fixing English title: '{original_title_english}' -> '{fixed_title_english}'")
                    article.title_english = fixed_title_english
                    fixed_count += 1
        
        if fixed_count > 0:
            print(f"\n✅ Fixed {fixed_count} encoding issues")
            
            # Ask for confirmation before committing
            response = input("Do you want to commit these changes to the database? (y/n): ")
            if response.lower() == 'y':
                db.commit()
                print("✅ Changes committed to database")
            else:
                db.rollback()
                print("❌ Changes rolled back")
        else:
            print("✅ No encoding issues found to fix")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 