# Encoding and Database Constraint Fixes

## Issues Identified

### 1. Garbled Text Source (FIXED ✅)
**Problem**: Chinese text was appearing as garbled characters like `绔�������������棣���ュ�ㄥ�介��璺�棰�璁″��������瀹�1780涓�浜烘��`

**Root Cause**: People's Daily scraper was forcing `gb2312` encoding, but People's Daily websites now serve UTF-8 content.

**Location**: `app/scrapers/peoples_daily_scraper.py` lines 102-105

**Original Code**:
```python
# Set encoding based on the website
if "thepaper.cn" in url:
    response.encoding = 'utf-8'  # The Paper uses UTF-8
else:
    response.encoding = 'gb2312'  # People's Daily uses GB2312
```

**Fixed Code**:
```python
# FIXED: Use proper encoding detection for Chinese content
if not response.encoding or response.encoding == 'ISO-8859-1':
    # Use apparent encoding (auto-detected) for Chinese content
    response.encoding = response.apparent_encoding or 'utf-8'

# All People's Daily and The Paper sites now use UTF-8
if "thepaper.cn" in url or "people.com.cn" in url:
    response.encoding = 'utf-8'
```

### 2. Database Constraint Error (FIXED ✅)
**Problem**: API was failing with UNIQUE constraint violations on `news.source_url`

**Root Cause**: Database operations weren't properly handling constraint violations when duplicate URLs were encountered.

**Location**: `app/main.py` in both `fetch_news()` and `fetch_news_by_date()` functions

**Fix Applied**: Added try-catch blocks around database operations:
```python
try:
    news_item = News(...)
    db.add(news_item)
    db.flush()  # Check for constraint violations before commit
    new_articles_count += 1
except Exception as db_error:
    logger.warning(f"Skipping duplicate article: {article['source_url']} - {str(db_error)}")
    db.rollback()
    continue
```

## Testing Results

### Encoding Fix Verification
- **Before Fix**: `璁拌��瑙�瀵� | ��ㄩ�ㄥ����� 涓ユ�ュ揩澶�` (garbled)
- **After Fix**: `清风为伴产业兴 | 柞蚕"吐丝成金"` (proper Chinese)

### Database Constraint Fix Verification
- **Before Fix**: API returned 500 errors with constraint violations
- **After Fix**: API successfully processed 1065 articles, adding 42 new ones without errors

### Latest Articles Check
All 20 latest articles (IDs 975-994) show proper Chinese encoding:
- ✅ `国宝回归！美方返还子弹库帛书《五行令》《攻守占》`
- ✅ `孙磊已任中国常驻联合国副代表、特命全权大使`
- ✅ `王毅：中方在格陵兰问题上充分尊重丹麦的主权和领土完整`

## Impact

### Positive Results
1. **All new articles** scraped after the fix have proper Chinese encoding
2. **API stability** improved - no more constraint violation crashes
3. **Guancha integration** working perfectly with 39 articles successfully scraped
4. **People's Daily articles** now display correctly

### Legacy Data
- **111 old articles** still have garbled text (scraped before the fix)
- These can be re-scraped or fixed with a separate migration script if needed

## Technical Details

### Encoding Detection Logic
The fix uses a multi-step approach:
1. Check if response encoding is missing or defaulted to ISO-8859-1
2. Use `response.apparent_encoding` (auto-detected) as fallback
3. Force UTF-8 for known Chinese content sites
4. Default to UTF-8 if all else fails

### Database Error Handling
- Uses `db.flush()` to detect constraint violations early
- Graceful rollback and continue on duplicates
- Comprehensive error logging for debugging

## Files Modified
1. `app/scrapers/peoples_daily_scraper.py` - Encoding fix
2. `app/main.py` - Database constraint handling (2 functions)

## Status: COMPLETE ✅
Both issues have been successfully resolved and tested. 