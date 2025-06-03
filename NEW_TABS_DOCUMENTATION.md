# New Tabs and Scrapers Documentation

This document describes the new tabs and scrapers that have been added to the Chinese News Aggregator system.

## Overview

Four new tabs have been added to the system, each with their own subtabs and dedicated scrapers:

1. **State Council** - 8 subtabs
2. **NBS** (National Bureau of Statistics) - 3 subtabs  
3. **Taiwan Affairs** - 2 subtabs
4. **MND** (Ministry of National Defense) - 3 subtabs

## New Scrapers Created

### 1. State Council Scraper (`state_council_scraper.py`)

**Source Name:** State Council  
**Selector:** `div.news_box a` (general), `div#loadingInfoPage a` (for CAC)

**Subtabs:**
- State Council News Releases: https://www.gov.cn/lianbo/fabu/
- State Council Department News: https://www.gov.cn/lianbo/bumen/
- State Council Local News: https://www.gov.cn/lianbo/difang/
- State Council Government News Broadcast: https://www.gov.cn/lianbo/
- State Council Breaking News: https://www.gov.cn/toutiao/liebiao/
- State Council Latest Policies: https://www.gov.cn/zhengce/zuixin/
- State Council Policy Interpretation: https://www.gov.cn/zhengce/jiedu/
- CAC: https://www.cac.gov.cn/yaowen/wxyw/A093602index_1.htm

### 2. NBS Scraper (`nbs_scraper.py`)

**Source Name:** NBS  
**Selector:** `a.pc1200`

**Subtabs:**
- NBS Data Release: https://www.stats.gov.cn/sj/zxfb/
- NBS Data Interpretation: https://www.stats.gov.cn/sj/sjjd/
- NBS Press Conference: https://www.stats.gov.cn/sj/xwfbh/fbhwd/

### 3. Taiwan Affairs Scraper (`taiwan_affairs_scraper.py`)

**Source Name:** Taiwan Affairs  
**Selector:** `ul.scdList a`

**Subtabs:**
- Taiwan Affairs Office: http://www.gwytb.gov.cn/xwdt/xwfb/wyly/
- Chinese Departments on Taiwan: http://www.gwytb.gov.cn/bmst/

### 4. MND Scraper (`mnd_scraper.py`)

**Source Name:** MND  
**Selector:** `li a`

**Subtabs:**
- MND Regular PC: http://www.mod.gov.cn/gfbw/xwfyr/lxjzh_246940/index.html
- MND Routine PC: http://www.mod.gov.cn/gfbw/xwfyr/yzxwfb/index.html
- MND Special PC: http://www.mod.gov.cn/gfbw/xwfyr/ztjzh/index.html

## Implementation Details

### Files Modified/Created

1. **New Scraper Files:**
   - `app/scrapers/state_council_scraper.py`
   - `app/scrapers/nbs_scraper.py`
   - `app/scrapers/taiwan_affairs_scraper.py`
   - `app/scrapers/mnd_scraper.py`

2. **Modified Files:**
   - `app/scrapers/__init__.py` - Added imports for all new scrapers
   - `app/main.py` - Updated to include new scrapers in fetch endpoints and UI organization

### Integration Points

1. **Fetch Endpoints:** All new scrapers are integrated into both `/api/news/fetch` and `/api/news/fetch/{date}` endpoints
2. **UI Organization:** The `news_by_date` function now includes all new scrapers in the organized news structure
3. **URL Pattern Matching:** Added fallback categorization for articles from the new sources based on URL patterns

### Features

- **Translation Support:** All scrapers support optional immediate translation using Microsoft Translator
- **Error Handling:** Comprehensive error handling and logging for each scraper
- **Encoding Support:** Proper UTF-8 encoding handling for Chinese government websites
- **Rate Limiting:** Built-in delays between requests to be respectful to source websites
- **Async Support:** All scrapers implement the async `get_news()` method for concurrent operation

### Usage

The new tabs will automatically appear in the UI when news is fetched from these sources. Users can:

1. Fetch news from all sources using the existing fetch endpoints
2. Browse news by date with the new tabs and subtabs automatically organized
3. View articles with proper Chinese and English titles (if translation is enabled)
4. Access original source URLs for each article

### Technical Notes

- All scrapers follow the same pattern as existing `PeoplesDailyScraper` and `PaperScraper`
- Each scraper has a unique `source_id` (3-6) for database organization
- Proper URL construction for relative links from each source domain
- Consistent error handling and logging across all scrapers

## Testing

All scrapers have been tested for:
- ✅ Successful import and instantiation
- ✅ Proper source name and section configuration
- ✅ Integration with main application endpoints
- ✅ Compatibility with existing UI structure

The system now supports 6 major Chinese news sources with a total of 22 different subtabs for comprehensive news coverage. 