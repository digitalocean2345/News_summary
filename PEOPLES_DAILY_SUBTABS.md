# People's Daily Subtabs Feature

## Overview
The People's Daily tab now includes 6 specialized subtabs that allow you to fetch and view headlines from different sections of People's Daily website for any selected date.

## Available Subtabs

1. **人民网人事频道** (Personnel Channel)
   - URL: http://renshi.people.com.cn/
   - Selector: `div.fl a[href*="/n1/"]`

2. **PD Anti Corruption**
   - URL: http://fanfu.people.com.cn/
   - Selector: `div.fl a[href*="/n1/"]`

3. **PD International Breaking News**
   - URL: http://world.people.com.cn/GB/157278/index.html
   - Selector: `div.ej_bor a[href*="/n1/"]`

4. **PD International In-depth**
   - URL: http://world.people.com.cn/GB/14549/index.html
   - Selector: `div.ej_bor a[href*="/n1/"]`

5. **PD Society**
   - URL: http://society.people.com.cn/GB/136657/index.html
   - Selector: `div.ej_list_box a[href*="/n1/"]`

6. **PD Economy**
   - URL: http://finance.people.com.cn/GB/70846/index.html
   - Selector: `div.ej_list_box a[href*="/n1/"]`

## How to Use

1. **Navigate to a Date**: Click on any date in the calendar to view headlines for that date.

2. **Select People's Daily Tab**: Click on the "People's Daily" tab in the main navigation.

3. **Fetch Headlines**: Click the "🔄 Fetch People's Daily Headlines for [DATE]" button to scrape fresh headlines from all 6 sections.

4. **Browse Subtabs**: After fetching, you'll see subtabs for each section. Click on any subtab to view headlines from that specific section.

5. **View Articles**: Click on any headline to view the full article content.

## API Endpoint

The feature adds a new API endpoint:

```
POST /api/news/fetch/{date}
```

- **Parameters**: `date` in YYYY-MM-DD format
- **Returns**: JSON with fetch results including counts of new and updated articles
- **Example**: `POST /api/news/fetch/2024-12-19`

## Technical Implementation

- **Scraper**: Enhanced `PeoplesDailyScraper` class with date-specific fetching
- **Selectors**: Mapped specific CSS selectors for each section type
- **Database**: Articles are stored with `source_section` field for proper categorization
- **UI**: Dynamic subtabs with real-time fetching and status updates

## Features

- ✅ Date-specific headline fetching
- ✅ Real-time scraping with progress indicators
- ✅ Automatic page refresh after successful fetch
- ✅ Error handling and user feedback
- ✅ Organized subtabs by section
- ✅ Article count display for each section
- ✅ Translation support for headlines 