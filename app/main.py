from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import News, Category, Comment, SavedSummary
from app.models import models
from app.schemas import schemas
from app.scrapers.peoples_daily_scraper import PeoplesDailyScraper
from app.scrapers.paper_scraper import PaperScraper
from app.scrapers.state_council_scraper import StateCouncilScraper
from app.scrapers.nbs_scraper import NBSScraper
from app.scrapers.taiwan_affairs_scraper import TaiwanAffairsScraper
from app.scrapers.mnd_scraper import MNDScraper
from app.scrapers.guancha_scraper import GuanchaScraper
from app.scrapers.global_times_scraper import GlobalTimesScraper
from app.api.content_endpoints import router as content_router
from app.api.category_endpoints import router as category_router
from collections import defaultdict
import logging
from datetime import datetime, timedelta
import calendar
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Dict, Optional
from app.services.translator import MicrosoftTranslator
import os
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chinese News Aggregator with Content Scraping",
    description="API for aggregating Chinese news with full content extraction and translation",
    version="2.0.0"
)

# Include content scraping router
app.include_router(content_router)

# Include category management router
app.include_router(category_router)

# Try to configure templates - fail gracefully if jinja2 not available
templates = None
try:
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    logger.info("✅ Templates initialized successfully")
except ImportError as e:
    logger.warning(f"⚠️ Templates not available: {e}")
    logger.warning("HTML routes will not work, but API routes will function normally")
except Exception as e:
    logger.warning(f"⚠️ Template initialization failed: {e}")

# Mount static files if directory exists
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    logger.info("✅ Static files mounted successfully")
except Exception as e:
    logger.warning(f"⚠️ Static files not available: {e}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/news/fetch")
async def fetch_news(db: Session = Depends(get_db)):
    try:
        # Check if we're in production (Railway) environment
        is_production = bool(os.getenv('DATABASE_URL'))
        
        # Initialize all scrapers - enable translation in production
        pd_scraper = PeoplesDailyScraper(translate_immediately=is_production)
        paper_scraper = PaperScraper(translate_immediately=is_production)
        sc_scraper = StateCouncilScraper(translate_immediately=is_production)
        nbs_scraper = NBSScraper(translate_immediately=is_production)
        tao_scraper = TaiwanAffairsScraper(translate_immediately=is_production)
        mnd_scraper = MNDScraper(translate_immediately=is_production)
        guancha_scraper = GuanchaScraper(translate_immediately=is_production)
        gt_scraper = GlobalTimesScraper(translate_immediately=is_production)
        
        # Fetch articles from all sources
        pd_articles = pd_scraper.fetch_news()
        paper_articles = paper_scraper.fetch_news()
        sc_articles = sc_scraper.fetch_news()
        nbs_articles = nbs_scraper.fetch_news()
        tao_articles = tao_scraper.fetch_news()
        mnd_articles = mnd_scraper.fetch_news()
        guancha_articles = guancha_scraper.fetch_news()
        gt_articles = gt_scraper.fetch_news()
        
        # Combine all articles
        all_articles = pd_articles + paper_articles + sc_articles + nbs_articles + tao_articles + mnd_articles + guancha_articles + gt_articles
        
        translator = MicrosoftTranslator()
        new_articles_count = 0
        duplicate_count = 0
        
        for article in all_articles:
            # Check if article already exists by URL only (across all dates)
            existing_by_url = db.query(News).filter(News.source_url == article['source_url']).first()
            
            if existing_by_url:
                duplicate_count += 1
                logger.info(f"Skipping duplicate URL: {article['source_url']}")
                continue
            
            try:
                # Check if this is from Global Times (already in English)
                if article.get('source_section', '').startswith('Global Times'):
                    title_english = article['title']  # Already in English
                else:
                    title_english = translator.translate(article['title'])
            except Exception as e:
                logger.error(f"Translation failed: {str(e)}")
                title_english = None
            
            try:
                news_item = News(
                    title=article['title'],
                    title_english=title_english,
                    source_url=article['source_url'],
                    source_section=article.get('source_section'),
                    collection_date=article['collection_date']
                )
                db.add(news_item)
                db.flush()  # Check for constraint violations before commit
                new_articles_count += 1
            except Exception as db_error:
                logger.warning(f"Database constraint violation for article: {article['source_url']} - {str(db_error)}")
                db.rollback()
                duplicate_count += 1
                continue
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Database commit error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return {
            "message": f"Successfully fetched {new_articles_count} new articles from all sources (People's Daily, The Paper, State Council, NBS, Taiwan Affairs, MND, Guancha, Global Times)",
            "new_articles": new_articles_count,
            "duplicates_skipped": duplicate_count,
            "total_processed": len(all_articles)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/news/fetch/{date}")
async def fetch_news_by_date(date: str, db: Session = Depends(get_db)):
    """Fetch news from all sources for a specific date to populate subtabs"""
    try:
        # Parse the date
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Check if we're in production (Railway) environment
        is_production = bool(os.getenv('DATABASE_URL'))
        
        # Initialize all scrapers - enable translation in production
        pd_scraper = PeoplesDailyScraper(translate_immediately=is_production)
        paper_scraper = PaperScraper(translate_immediately=is_production)
        sc_scraper = StateCouncilScraper(translate_immediately=is_production)
        nbs_scraper = NBSScraper(translate_immediately=is_production)
        tao_scraper = TaiwanAffairsScraper(translate_immediately=is_production)
        mnd_scraper = MNDScraper(translate_immediately=is_production)
        guancha_scraper = GuanchaScraper(translate_immediately=is_production)
        gt_scraper = GlobalTimesScraper(translate_immediately=is_production)
        
        # Fetch articles from all sources
        pd_articles = pd_scraper.fetch_news_by_date(date_obj)
        paper_articles = paper_scraper.fetch_news_by_date(date_obj)
        sc_articles = sc_scraper.fetch_news_by_date(date_obj)
        nbs_articles = nbs_scraper.fetch_news_by_date(date_obj)
        tao_articles = tao_scraper.fetch_news_by_date(date_obj)
        mnd_articles = mnd_scraper.fetch_news_by_date(date_obj)
        guancha_articles = guancha_scraper.fetch_news_by_date(date_obj)
        gt_articles = gt_scraper.fetch_news_by_date(date_obj)
        
        # Combine all articles
        all_articles = pd_articles + paper_articles + sc_articles + nbs_articles + tao_articles + mnd_articles + guancha_articles + gt_articles
        
        translator = MicrosoftTranslator()
        new_articles_count = 0
        updated_articles_count = 0
        duplicate_count = 0
        
        for article in all_articles:
            # Check if article already exists by URL only (across all dates)
            existing_by_url = db.query(News).filter(News.source_url == article['source_url']).first()
            
            if existing_by_url:
                # Article exists - update if needed
                if not existing_by_url.source_section and article.get('source_section'):
                    existing_by_url.source_section = article.get('source_section')
                    updated_articles_count += 1
                else:
                    duplicate_count += 1
                    logger.info(f"Article already exists: {article['source_url']}")
                continue
            
            # Article doesn't exist - create new one
            try:
                # Check if this is from Global Times (already in English)
                if article.get('source_section', '').startswith('Global Times'):
                    title_english = article['title']  # Already in English
                else:
                    title_english = translator.translate(article['title'])
            except Exception as e:
                logger.error(f"Translation failed: {str(e)}")
                title_english = None
            
            try:
                news_item = News(
                    title=article['title'],
                    title_english=title_english,
                    source_url=article['source_url'],
                    source_section=article.get('source_section'),
                    collection_date=date_obj
                )
                db.add(news_item)
                db.flush()  # Check for constraint violations before commit
                new_articles_count += 1
            except Exception as db_error:
                logger.warning(f"Database constraint violation for article: {article['source_url']} - {str(db_error)}")
                db.rollback()
                duplicate_count += 1
                continue
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Database commit error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return {
            "message": f"Successfully processed articles for {date}: {new_articles_count} new, {updated_articles_count} updated, {duplicate_count} duplicates skipped",
            "new_articles": new_articles_count,
            "updated_articles": updated_articles_count,
            "duplicates_skipped": duplicate_count,
            "total_processed": len(all_articles)
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def calendar_view(request: Request, db: Session = Depends(get_db), year: int = None, month: int = None):
    # Use current date if year/month not provided
    today = datetime.now()
    current_year = year if year else today.year
    current_month = month if month else today.month
    
    # Handle month navigation boundaries
    if current_month > 12:
        current_month = 1
        current_year += 1
    elif current_month < 1:
        current_month = 12
        current_year -= 1
    
    cal = calendar.monthcalendar(current_year, current_month)
    
    # Get all dates with news for current month
    start_date = datetime(current_year, current_month, 1).date()
    if current_month == 12:
        end_date = datetime(current_year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(current_year, current_month + 1, 1).date() - timedelta(days=1)
    
    dates_with_news = db.query(News.collection_date).distinct().filter(
        News.collection_date.between(start_date, end_date)
    ).all()
    dates_with_news = {d[0] for d in dates_with_news}

    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day != 0:
                current_date = datetime(current_year, current_month, day).date()
                week_data.append({
                    'day': day,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'has_news': current_date in dates_with_news
                })
            else:
                week_data.append(None)
        calendar_data.append(week_data)

    # Calculate previous and next month/year
    prev_month = current_month - 1
    prev_year = current_year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    
    next_month = current_month + 1
    next_year = current_year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "calendar_data": calendar_data,
        "current_month": f"{calendar.month_name[current_month]} {current_year}",
        "current_year": current_year,
        "current_month_num": current_month,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month
    })

@app.get("/news/{date}", response_class=HTMLResponse)
async def news_by_date(request: Request, date: str, db: Session = Depends(get_db)):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        news_items = db.query(News).filter(News.collection_date == date_obj).all()
        
        # Initialize all scrapers to get website structure
        pd_scraper = PeoplesDailyScraper()
        paper_scraper = PaperScraper()
        sc_scraper = StateCouncilScraper()
        nbs_scraper = NBSScraper()
        tao_scraper = TaiwanAffairsScraper()
        mnd_scraper = MNDScraper()
        guancha_scraper = GuanchaScraper()
        gt_scraper = GlobalTimesScraper()
        
        # Initialize organized news structure for all sources
        organized_news = {}
        
        # Add People's Daily sections
        for source_name, source_sections in pd_scraper.websites.items():
            organized_news[source_name] = {}
            for section_name, section_url in source_sections.items():
                organized_news[source_name][section_name] = []
        
        # Add The Paper sections
        for source_name, source_sections in paper_scraper.websites.items():
            organized_news[source_name] = {}
            for section_name, section_url in source_sections.items():
                organized_news[source_name][section_name] = []
        
        # Add State Council sections
        for source_name, source_sections in sc_scraper.websites.items():
            organized_news[source_name] = {}
            for section_name, section_url in source_sections.items():
                organized_news[source_name][section_name] = []
        
        # Add NBS sections
        for source_name, source_sections in nbs_scraper.websites.items():
            organized_news[source_name] = {}
            for section_name, section_url in source_sections.items():
                organized_news[source_name][section_name] = []
        
        # Add Taiwan Affairs sections
        for source_name, source_sections in tao_scraper.websites.items():
            organized_news[source_name] = {}
            for section_name, section_url in source_sections.items():
                organized_news[source_name][section_name] = []
        
        # Add MND sections
        for source_name, source_sections in mnd_scraper.websites.items():
            organized_news[source_name] = {}
            for section_name, section_url in source_sections.items():
                organized_news[source_name][section_name] = []
        
        # Add Guancha sections
        for source_name, source_sections in guancha_scraper.websites.items():
            organized_news[source_name] = {}
            for section_name, section_url in source_sections.items():
                organized_news[source_name][section_name] = []
        
        # Add Global Times sections
        for source_name, source_sections in gt_scraper.websites.items():
            organized_news[source_name] = {}
            for section_name, section_url in source_sections.items():
                organized_news[source_name][section_name] = []
        
        # Categorize news using source_section field if available, fallback to URL pattern
        for item in news_items:
            categorized = False
            
            # First try to use stored source_section
            if item.source_section:
                parts = item.source_section.split(' - ')
                if len(parts) == 2:
                    source_name, section_name = parts
                    if source_name in organized_news and section_name in organized_news[source_name]:
                        organized_news[source_name][section_name].append(item)
                        categorized = True
            
            # Fallback to URL pattern matching for older articles
            if not categorized:
                url = item.source_url
                if "world.people.com.cn" in url:
                    if "People's Daily" in organized_news and "International Breaking News" in organized_news["People's Daily"]:
                        organized_news["People's Daily"]["International Breaking News"].append(item)
                        categorized = True
                elif "thepaper.cn" in url:
                    # Try to categorize The Paper articles by URL pattern
                    if "The Paper" in organized_news:
                        # Default to Paper China Government if we can't determine the specific section
                        if "Paper China Government" in organized_news["The Paper"]:
                            organized_news["The Paper"]["Paper China Government"].append(item)
                            categorized = True
                elif "gov.cn" in url:
                    # Categorize government sites
                    if "State Council" in organized_news:
                        # Default to State Council News Releases if we can't determine the specific section
                        if "State Council News Releases" in organized_news["State Council"]:
                            organized_news["State Council"]["State Council News Releases"].append(item)
                            categorized = True
                elif "mofcom.gov.cn" in url:
                    # Categorize MOFCOM articles
                    if "State Council" in organized_news:
                        if "MOFCOM Spokesperson" in organized_news["State Council"]:
                            organized_news["State Council"]["MOFCOM Spokesperson"].append(item)
                            categorized = True
                elif "stats.gov.cn" in url:
                    # Categorize NBS articles
                    if "NBS" in organized_news:
                        if "NBS Data Release" in organized_news["NBS"]:
                            organized_news["NBS"]["NBS Data Release"].append(item)
                            categorized = True
                elif "gwytb.gov.cn" in url:
                    # Categorize Taiwan Affairs articles
                    if "Taiwan Affairs" in organized_news:
                        if "Taiwan Affairs Office" in organized_news["Taiwan Affairs"]:
                            organized_news["Taiwan Affairs"]["Taiwan Affairs Office"].append(item)
                            categorized = True
                elif "mod.gov.cn" in url:
                    # Categorize MND articles
                    if "MND" in organized_news:
                        if "MND Regular PC" in organized_news["MND"]:
                            organized_news["MND"]["MND Regular PC"].append(item)
                            categorized = True
                elif "guancha.cn" in url:
                    # Categorize Guancha articles with improved pattern matching
                    if "Guancha" in organized_news:
                        # Try to determine section by URL pattern
                        if "ZhongGuoWaiJiao" in url or "Chinese" in url:
                            if "Guancha Chinese Diplomacy" in organized_news["Guancha"]:
                                organized_news["Guancha"]["Guancha Chinese Diplomacy"].append(item)
                                categorized = True
                        else:
                            # Default to Guancha International for other Guancha articles
                            if "Guancha International" in organized_news["Guancha"]:
                                organized_news["Guancha"]["Guancha International"].append(item)
                                categorized = True
                elif "globaltimes.cn" in url:
                    # Categorize Global Times articles
                    if "Global Times" in organized_news:
                        # Try to determine section by URL pattern
                        if "/china/politics/" in url:
                            if "GT China Politics" in organized_news["Global Times"]:
                                organized_news["Global Times"]["GT China Politics"].append(item)
                                categorized = True
                        elif "/china/society/" in url:
                            if "GT China Society" in organized_news["Global Times"]:
                                organized_news["Global Times"]["GT China Society"].append(item)
                                categorized = True
                        elif "/china/diplomacy/" in url:
                            if "GT China Diplomacy" in organized_news["Global Times"]:
                                organized_news["Global Times"]["GT China Diplomacy"].append(item)
                                categorized = True
                        elif "/china/military/" in url:
                            if "GT China Military" in organized_news["Global Times"]:
                                organized_news["Global Times"]["GT China Military"].append(item)
                                categorized = True
                        elif "/china/science/" in url:
                            if "GT China Science" in organized_news["Global Times"]:
                                organized_news["Global Times"]["GT China Science"].append(item)
                                categorized = True
                        elif "/opinion/" in url:
                            if "GT Opinion Editorial" in organized_news["Global Times"]:
                                organized_news["Global Times"]["GT Opinion Editorial"].append(item)
                                categorized = True
                        elif "/source/" in url:
                            if "GT Source Voice" in organized_news["Global Times"]:
                                organized_news["Global Times"]["GT Source Voice"].append(item)
                                categorized = True
                        elif "/In-depth/" in url:
                            if "GT Indepth" in organized_news["Global Times"]:
                                organized_news["Global Times"]["GT Indepth"].append(item)
                                categorized = True
                        else:
                            # Default to GT China Politics for other Global Times articles
                            if "GT China Politics" in organized_news["Global Times"]:
                                organized_news["Global Times"]["GT China Politics"].append(item)
                                categorized = True
        
        # MODIFIED: Don't remove empty sections - keep all tabs and subtabs visible
        # This ensures users can see all available sources even when no news has been fetched yet
        # The original logic that removed empty sections has been commented out:
        # for source_name in list(organized_news.keys()):
        #     for section_name in list(organized_news[source_name].keys()):
        #         if not organized_news[source_name][section_name]:
        #             del organized_news[source_name][section_name]
        #     if not organized_news[source_name]:
        #         del organized_news[source_name]
        
        # Calculate article counts per source for tab display
        source_counts = {}
        for source_name, sections in organized_news.items():
            total_count = 0
            for section_name, articles in sections.items():
                total_count += len(articles)
            source_counts[source_name] = total_count
        
        return templates.TemplateResponse("date_sources.html", {
            "request": request,
            "organized_news": organized_news,
            "source_counts": source_counts,
            "selected_date": date,
            "total_articles": len(news_items)
        })
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/debug/articles")
async def debug_articles(db: Session = Depends(get_db)):
    articles = db.query(News).all()
    return {
        "count": len(articles),
        "articles": [
            {
                "id": article.id,
                "title": article.title,
                "title_english": article.title_english,
                "url": article.source_url,
                "date": str(article.collection_date)
            }
            for article in articles
        ]
    }

@app.get("/api/debug/sources")
async def debug_sources(db: Session = Depends(get_db)):
    """Debug endpoint to view all sources and categories"""
    try:
        sources = db.query(models.NewsSource).all()
        sources_list = []
        for source in sources:
            categories = []
            for category in source.categories:
                categories.append({
                    "id": category.id,
                    "name": category.name,
                    "url": category.url
                })
            
            sources_list.append({
                "id": source.id,
                "name": source.name,
                "url": source.url,
                "categories": categories
            })
        
        return {
            "total_sources": len(sources_list),
            "sources": sources_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debug/all")
async def debug_all(db: Session = Depends(get_db)):
    """Debug endpoint to view everything in database"""
    try:
        # Get all sources
        sources = db.query(models.NewsSource).all()
        sources_data = []
        for source in sources:
            source_data = {
                "id": source.id,
                "name": source.name,
                "url": source.url
            }
            sources_data.append(source_data)

        # Get all news articles
        news = db.query(News).all()
        news_data = []
        for article in news:
            news_data.append({
                "id": article.id,
                "title": article.title,
                "source_url": article.source_url,
                "collection_date": article.collection_date.isoformat() if article.collection_date else None,
                "source_id": article.source_id
            })

        return {
            "sources": sources_data,
            "total_sources": len(sources_data),
            "news": news_data,
            "total_news": len(news_data)
        }
    except Exception as e:
        print(f"Debug error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-translation")
async def test_translation():
    try:
        translator = MicrosoftTranslator()
        test_text = "你好，世界"
        result = translator.translate(test_text)
        return {
            "original": test_text,
            "translated": result,
            "success": result is not None
        }
    except Exception as e:
        logger.error(f"Translation test failed: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "success": False
        }
@app.get("/api/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    return {
        "MS_TRANSLATOR_KEY_EXISTS": bool(os.getenv('MS_TRANSLATOR_KEY')),
        "MS_TRANSLATOR_KEY_LENGTH": len(os.getenv('MS_TRANSLATOR_KEY', '')),
        "MS_TRANSLATOR_LOCATION": os.getenv('MS_TRANSLATOR_LOCATION', 'not set')
    }

# New Routes for Phase 5 - Content Display UI

@app.get("/article/{article_id}", response_class=HTMLResponse)
async def article_detail(request: Request, article_id: int, db: Session = Depends(get_db)):
    """Display detailed view of a single article with content scraping features"""
    try:
        # Get the article
        article = db.query(News).filter(News.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get categories for saving
        categories = db.query(Category).all()
        
        # Debug mode (can be controlled by environment variable)
        debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        return templates.TemplateResponse("article_detail.html", {
            "request": request,
            "article": article,
            "categories": categories,
            "debug_mode": debug_mode
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in article detail view: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/articles/{article_id}")
async def get_article_api(article_id: int, db: Session = Depends(get_db)):
    """API endpoint to get article details as JSON"""
    try:
        article = db.query(News).filter(News.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {
            "id": article.id,
            "title": article.title,
            "title_english": article.title_english,
            "source_url": article.source_url,
            "collection_date": article.collection_date.isoformat() if article.collection_date else None,
            "full_content": article.full_content,
            "full_content_english": article.full_content_english,
            "summary": article.summary,
            "summary_english": article.summary_english,
            "content_language": article.content_language,
            "source_domain": article.source_domain,
            "is_content_scraped": article.is_content_scraped,
            "is_content_translated": article.is_content_translated,
            "is_summarized": article.is_summarized,
            "content_scraped_at": article.content_scraped_at.isoformat() if article.content_scraped_at else None,
            "content_translated_at": article.content_translated_at.isoformat() if article.content_translated_at else None,
            "summarized_at": article.summarized_at.isoformat() if article.summarized_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article API: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all available categories"""
    try:
        categories = db.query(Category).all()
        return [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "color": category.color,
                "created_at": category.created_at.isoformat() if category.created_at else None
            }
            for category in categories
        ]
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/categories/stats")
async def get_categories_stats(db: Session = Depends(get_db)):
    """Get comment counts for all categories"""
    try:
        categories = db.query(Category).all()
        stats = []
        
        for category in categories:
            comment_count = db.query(Comment).filter(Comment.category_id == category.id).count()
            stats.append({
                "category_id": category.id,
                "category_name": category.name,
                "comment_count": comment_count
            })
        
        return stats
    except Exception as e:
        logger.error(f"Error getting category stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/comments", response_model=List[schemas.CommentResponse])
async def get_all_comments(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all comments, optionally filtered by category"""
    try:
        query = db.query(Comment)
        
        # Filter by category if specified
        if category:
            if category == "null" or category == "uncategorized":
                query = query.filter(Comment.category_id.is_(None))
            else:
                try:
                    category_id = int(category)
                    query = query.filter(Comment.category_id == category_id)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid category parameter")
        
        comments = query.all()
        
        result = []
        for comment in comments:
            # Get news info
            news = db.query(News).filter(News.id == comment.news_id).first()
            
            # Get category info if exists
            category_obj = None
            if comment.category_id:
                category_obj = db.query(Category).filter(Category.id == comment.category_id).first()
            
            result.append(schemas.CommentResponse(
                id=comment.id,
                news_id=comment.news_id,
                comment_text=comment.comment_text,
                category_id=comment.category_id,
                category_name=category_obj.name if category_obj else None,
                user_name=comment.user_name,
                created_at=comment.created_at,
                news_title=news.title if news else "Unknown",
                news_title_english=news.title_english if news else None,
                news_url=news.source_url if news else ""
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting all comments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources", response_class=HTMLResponse)
async def sources_view(request: Request):
    """Display all available sources organized by tabs and subtabs"""
    try:
        # Get the websites configuration from all scrapers
        pd_scraper = PeoplesDailyScraper()
        paper_scraper = PaperScraper()
        sc_scraper = StateCouncilScraper()
        nbs_scraper = NBSScraper()
        tao_scraper = TaiwanAffairsScraper()
        mnd_scraper = MNDScraper()
        guancha_scraper = GuanchaScraper()
        gt_scraper = GlobalTimesScraper()
        
        # Combine all websites from all scrapers
        all_websites = {}
        all_websites.update(pd_scraper.websites)
        all_websites.update(paper_scraper.websites)
        all_websites.update(sc_scraper.websites)
        all_websites.update(nbs_scraper.websites)
        all_websites.update(tao_scraper.websites)
        all_websites.update(mnd_scraper.websites)
        all_websites.update(guancha_scraper.websites)
        all_websites.update(gt_scraper.websites)
        
        return templates.TemplateResponse("sources.html", {
            "request": request,
            "websites": all_websites
        })
    except Exception as e:
        logger.error(f"Error in sources view: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/debug/date-urls/{date}")
async def debug_date_urls(date: str, db: Session = Depends(get_db)):
    """Debug endpoint to view all URLs for a specific date"""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        news_items = db.query(News).filter(News.collection_date == date_obj).all()
        
        urls_by_domain = {}
        for item in news_items:
            domain = item.source_url.split('/')[2] if '//' in item.source_url else 'unknown'
            if domain not in urls_by_domain:
                urls_by_domain[domain] = []
            urls_by_domain[domain].append({
                'id': item.id,
                'title': item.title[:100] + '...' if len(item.title) > 100 else item.title,
                'url': item.source_url
            })
        
        return {
            "date": date,
            "total_articles": len(news_items),
            "domains": urls_by_domain,
            "domain_counts": {domain: len(articles) for domain, articles in urls_by_domain.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/comments", response_model=schemas.CommentResponse)
async def add_comment(
    news_id: int,
    comment_data: schemas.CommentCreateRequest,
    db: Session = Depends(get_db)
):
    """Add a new comment to a news article"""
    try:
        # Verify news article exists
        news = db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News article not found")
        
        # Verify category exists if provided
        category = None
        if comment_data.category_id:
            category = db.query(Category).filter(Category.id == comment_data.category_id).first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
        
        # Create new comment
        new_comment = Comment(
            news_id=news_id,
            comment_text=comment_data.comment_text,
            category_id=comment_data.category_id,
            user_name=comment_data.user_name
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        # Return formatted response
        return schemas.CommentResponse(
            id=new_comment.id,
            news_id=new_comment.news_id,
            comment_text=new_comment.comment_text,
            category_id=new_comment.category_id,
            category_name=category.name if category else None,
            user_name=new_comment.user_name,
            created_at=new_comment.created_at,
            news_title=news.title,
            news_title_english=news.title_english,
            news_url=news.source_url
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding comment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/comments/{news_id}", response_model=List[schemas.CommentResponse])
async def get_comments_for_news(news_id: int, db: Session = Depends(get_db)):
    """Get all comments for a specific news article"""
    try:
        # Verify news article exists
        news = db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News article not found")
        
        # Get comments with category info
        comments = db.query(Comment).filter(Comment.news_id == news_id).all()
        
        result = []
        for comment in comments:
            category = None
            if comment.category_id:
                category = db.query(Category).filter(Category.id == comment.category_id).first()
            
            result.append(schemas.CommentResponse(
                id=comment.id,
                news_id=comment.news_id,
                comment_text=comment.comment_text,
                category_id=comment.category_id,
                category_name=category.name if category else None,
                user_name=comment.user_name,
                created_at=comment.created_at,
                news_title=news.title,
                news_title_english=news.title_english,
                news_url=news.source_url
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting comments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/comments/category/{category_id}", response_model=List[schemas.CommentResponse])
async def get_comments_by_category(category_id: int, db: Session = Depends(get_db)):
    """Get all comments for a specific category"""
    try:
        # Verify category exists
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Get comments with news info
        comments = db.query(Comment).filter(Comment.category_id == category_id).order_by(Comment.created_at.desc()).all()
        
        result = []
        for comment in comments:
            news = db.query(News).filter(News.id == comment.news_id).first()
            
            result.append(schemas.CommentResponse(
                id=comment.id,
                news_id=comment.news_id,
                comment_text=comment.comment_text,
                category_id=comment.category_id,
                category_name=category.name,
                user_name=comment.user_name,
                created_at=comment.created_at,
                news_title=news.title if news else "Unknown",
                news_title_english=news.title_english if news else None,
                news_url=news.source_url if news else ""
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting comments by category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/categories", response_model=schemas.Category)
async def create_category(
    category_data: schemas.CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category"""
    try:
        # Check if category already exists
        existing = db.query(Category).filter(Category.name == category_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category already exists")
        
        new_category = Category(
            name=category_data.name,
            description=category_data.description,
            color=category_data.color
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        return new_category
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete a category and all its associated saved summaries and comments"""
    try:
        # Check if category exists
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Count how many items will be affected
        saved_summaries_count = db.query(SavedSummary).filter(SavedSummary.category_id == category_id).count()
        comments_count = db.query(Comment).filter(Comment.category_id == category_id).count()
        
        # Delete all saved summaries associated with this category
        db.query(SavedSummary).filter(SavedSummary.category_id == category_id).delete()
        
        # Delete all comments associated with this category
        db.query(Comment).filter(Comment.category_id == category_id).delete()
        
        # Delete the category itself
        db.delete(category)
        db.commit()
        
        logger.info(f"Category {category_id} deleted with {saved_summaries_count} saved summaries and {comments_count} comments")
        
        return {
            "message": f"Category '{category.name}' deleted successfully",
            "deleted_saved_summaries": saved_summaries_count,
            "deleted_comments": comments_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete category: {str(e)}")

@app.delete("/api/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific comment"""
    try:
        # Check if comment exists
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Store comment info for response
        comment_info = {
            "id": comment.id,
            "news_id": comment.news_id,
            "comment_text": comment.comment_text[:50] + "..." if len(comment.comment_text) > 50 else comment.comment_text,
            "user_name": comment.user_name,
            "created_at": comment.created_at
        }
        
        # Delete the comment
        db.delete(comment)
        db.commit()
        
        logger.info(f"Comment {comment_id} deleted")
        
        return {
            "message": "Comment deleted successfully",
            "deleted_comment": comment_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting comment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")

@app.get("/comments", response_class=HTMLResponse)
async def comments_view(request: Request, db: Session = Depends(get_db)):
    """View for browsing comments by category"""
    try:
        # Get all categories with comment counts
        categories = db.query(Category).all()
        category_data = []
        
        for category in categories:
            comment_count = db.query(Comment).filter(Comment.category_id == category.id).count()
            category_data.append({
                "category": category,
                "comment_count": comment_count
            })
        
        return templates.TemplateResponse("comments_by_category.html", {
            "request": request,
            "categories": category_data
        })
        
    except Exception as e:
        logger.error(f"Error in comments view: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comments/category/{category_id}", response_class=HTMLResponse)
async def comments_by_category_view(
    request: Request, 
    category_id: int, 
    db: Session = Depends(get_db)
):
    """View comments for a specific category"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        comments = db.query(Comment).filter(Comment.category_id == category_id).order_by(Comment.created_at.desc()).all()
        
        # Format comments with news details
        comment_data = []
        for comment in comments:
            news = db.query(News).filter(News.id == comment.news_id).first()
            comment_data.append({
                "comment": comment,
                "news": news
            })
        
        return templates.TemplateResponse("category_comments.html", {
            "request": request,
            "category": category,
            "comments": comment_data
        })
        
    except Exception as e:
        logger.error(f"Error in category comments view: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories", response_class=HTMLResponse)
async def categories_view(request: Request, db: Session = Depends(get_db)):
    """Categories and comments management page"""
    try:
        # Get all categories
        categories = db.query(Category).all()
        
        # Get current date for navigation
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        return templates.TemplateResponse("categories.html", {
            "request": request,
            "categories": categories,
            "current_date": current_date
        })
        
    except Exception as e:
        logger.error(f"Error in categories view: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint for monitoring and GitHub Actions
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection by counting news articles
        result = db.execute(text("SELECT COUNT(*) FROM news"))
        count = result.scalar()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "news-aggregator-api",
            "database": "connected",
            "articles_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "service": "news-aggregator-api",
            "database": "disconnected",
            "error": str(e)
        }

@app.post("/api/admin/init-database")
async def initialize_database():
    """Initialize database tables - creates all tables if they don't exist"""
    try:
        from app.database import engine
        from app.models.models import Base
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created - SQLite compatible query
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """))
            tables = [row[0] for row in result.fetchall()]
        
        return {
            "message": "Database initialized successfully",
            "tables_created": tables,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")

@app.post("/api/admin/add-test-data")
async def add_test_data(db: Session = Depends(get_db)):
    """Add some test news data for demonstration"""
    try:
        from datetime import datetime, date
        
        # Add test categories
        categories_data = [
            {"name": "Technology", "description": "Tech news and innovations"},
            {"name": "Business", "description": "Business and finance news"},
            {"name": "Environment", "description": "Environmental and climate news"},
            {"name": "Health", "description": "Health and medical news"}
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not category:
                category = Category(**cat_data)
                db.add(category)
                db.commit()
                db.refresh(category)
            categories[cat_data["name"]] = category
        
        # Add test news articles
        today = date.today()
        test_articles = [
            {
                "headline": "Tech Giants Report Strong Q4 Earnings",
                "summary": "Major technology companies showed robust financial performance in the fourth quarter.",
                "content": "Technology giants reported strong earnings for Q4 2024, with cloud computing and AI investments paying off significantly.",
                "url": "https://example.com/tech-earnings",
                "published_at": datetime.now(),
                "date": today,
                "category_id": categories["Technology"].id,
                "source": "Test Source"
            },
            {
                "headline": "Global Climate Summit Reaches Historic Agreement",
                "summary": "World leaders agreed on ambitious carbon reduction targets at the international climate summit.",
                "content": "The global climate summit concluded with unprecedented agreement on carbon emission reduction targets.",
                "url": "https://example.com/climate-summit",
                "published_at": datetime.now(),
                "date": today,
                "category_id": categories["Environment"].id,
                "source": "Test Source"
            },
            {
                "headline": "Revolutionary Medical Breakthrough in Cancer Treatment",
                "summary": "Scientists announce a breakthrough in personalized cancer therapy.",
                "content": "Researchers have developed a new personalized cancer treatment approach that shows remarkable success rates.",
                "url": "https://example.com/cancer-breakthrough",
                "published_at": datetime.now(),
                "date": today,
                "category_id": categories["Health"].id,
                "source": "Test Source"
            },
            {
                "headline": "Asian Markets Rally on Economic Optimism",
                "summary": "Stock markets across Asia showed strong gains as investors responded positively.",
                "content": "Asian stock markets experienced significant rallies as positive economic data boosted investor confidence.",
                "url": "https://example.com/asia-markets",
                "published_at": datetime.now(),
                "date": today,
                "category_id": categories["Business"].id,
                "source": "Test Source"
            }
        ]
        
        added_articles = []
        for article_data in test_articles:
            # Check if article already exists
            existing = db.query(News).filter(News.headline == article_data["headline"]).first()
            if not existing:
                article = News(**article_data)
                db.add(article)
                db.commit()
                db.refresh(article)
                added_articles.append(article.headline)
        
        return {
            "message": "Test data added successfully",
            "categories_created": len(categories),
            "articles_added": len(added_articles),
            "articles": added_articles,
            "status": "success"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add test data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add test data: {str(e)}")

