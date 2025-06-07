from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
import logging
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from typing import List, Dict
from app.services.translator import MicrosoftTranslator
import os
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chinese News Aggregator API",
    description="API-only version for Railway deployment - aggregating Chinese news with full content extraction and translation",
    version="2.0.0"
)

# Include routers
app.include_router(content_router)
app.include_router(category_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Chinese News Aggregator API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "fetch_news": "/api/news/fetch",
            "fetch_by_date": "/api/news/fetch/{date}",
            "articles": "/api/debug/articles",
            "categories": "/api/categories"
        }
    }

@app.post("/api/news/fetch")
async def fetch_news(db: Session = Depends(get_db)):
    try:
        # Initialize all scrapers
        pd_scraper = PeoplesDailyScraper(translate_immediately=False)
        paper_scraper = PaperScraper(translate_immediately=False)
        sc_scraper = StateCouncilScraper(translate_immediately=False)
        nbs_scraper = NBSScraper(translate_immediately=False)
        tao_scraper = TaiwanAffairsScraper(translate_immediately=False)
        mnd_scraper = MNDScraper(translate_immediately=False)
        guancha_scraper = GuanchaScraper(translate_immediately=False)
        gt_scraper = GlobalTimesScraper(translate_immediately=False)
        
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
            "message": f"Successfully fetched {new_articles_count} new articles from all sources",
            "new_articles": new_articles_count,
            "duplicates_skipped": duplicate_count,
            "total_processed": len(all_articles),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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

# Health check endpoint for monitoring and GitHub Actions
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring and deployment verification"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        # Get basic stats
        news_count = db.query(News).count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "news-aggregator-api",
            "database": "connected",
            "total_articles": news_count,
            "version": "2.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "service": "news-aggregator-api",
            "database": "disconnected",
            "error": str(e)
        } 